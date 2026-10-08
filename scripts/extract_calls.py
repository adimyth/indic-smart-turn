#!/usr/bin/env python3
"""Extract local private end-of-turn samples from mixed roleplay-call recordings.

The CSV must contain `language,audio_file`. Source recordings remain local: the script downloads each MP4, decodes a 16 kHz mono WAV to `data/private/raw/`, and deletes the MP4. It never logs source names or URLs and never calls an API.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlsplit

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import soundfile as sf
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from indic_turn.build import fit_window
from indic_turn.common import LANG_NAMES, SR

MIN_SILENCE_MS = 200
MIN_SPEECH_MS = 150
SPEECH_PAD_MS = 60
MIN_EMBED_SECONDS = 0.4
MIN_TRAINEE_SECONDS = 30.0
AGENT_RESPONSE_SECONDS = 5.0
INCOMPLETE_RESUME_SECONDS = 2.0
REFERENCE_MARGIN = 0.1
KMEANS_RESTARTS = 10
NO_FUTURE_SPEECH = float("nan")

LANGUAGE_CODES = {name.lower(): code for code, name in LANG_NAMES.items()}


@dataclass(frozen=True)
class Call:
    language: str
    url: str
    source_name: str
    call_id: str


@dataclass(frozen=True)
class Candidate:
    position: int
    end: float
    pause_s: float
    gap_user: float
    gap_agent: float
    rule_label: str


class QuarantinedCall(RuntimeError):
    """A recording did not meet the pre-registered speaker-assignment checks."""


class ExtractionFailure(RuntimeError):
    """A recording could not be downloaded, decoded, or analysed locally."""


def private_schema() -> pa.Schema:
    """Match the built public schema and append private-call metadata."""
    return pa.schema([
        ("audio", pa.struct([("bytes", pa.binary()), ("path", pa.string())])),
        ("endpoint_bool", pa.bool_()),
        ("text_label", pa.bool_()),
        ("audio_conf", pa.float32()),
        ("audio_reason", pa.string()),
        ("ambiguous", pa.bool_()),
        ("language", pa.string()),
        ("dataset", pa.string()),
        ("synthetic", pa.bool_()),
        ("midfiller", pa.bool_()),
        ("endfiller", pa.bool_()),
        ("spoken_text", pa.string()),
        ("speaker_id", pa.string()),
        ("session", pa.string()),
        ("chunk", pa.int32()),
        ("split", pa.string()),
        ("llm_conf", pa.float32()),
        ("call_id", pa.string()),
        ("pause_s", pa.float32()),
        ("gap_user", pa.float32()),
        ("gap_agent", pa.float32()),
        ("rule_label", pa.string()),
    ])


def normalise(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-12:
        raise ExtractionFailure("zero-norm speaker embedding")
    return vector / norm


def salted_call_id(source_name: str, salt: str) -> str:
    """Return a non-reversible stable call identifier without retaining the path."""
    return hashlib.sha1(f"{salt}:{source_name}".encode("utf-8")).hexdigest()


def split_of(call_id: str) -> str:
    """Assign the complete call, not individual boundaries, to a deterministic 70/30 split."""
    bucket = int(hashlib.sha1(call_id.encode("ascii")).hexdigest(), 16) % 10_000
    return "train" if bucket < 7_000 else "test"


def wav_bytes(audio: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, audio, SR, format="WAV", subtype="PCM_16")
    return buffer.getvalue()


def percentile_summary(values: Iterable[float]) -> str:
    finite = np.asarray([value for value in values if np.isfinite(value)], dtype=np.float64)
    if not len(finite):
        return "n=0"
    p10, p50, p90 = np.percentile(finite, [10, 50, 90])
    return f"n={len(finite)} p10={p10:.2f}s p50={p50:.2f}s p90={p90:.2f}s"


def raw_path(raw_dir: Path, call: Call) -> Path:
    return raw_dir / f"{call.call_id}.wav"


def download_and_decode(call: Call, raw_dir: Path) -> Path:
    """Fetch one recording and retain only a decoded WAV without exposing its URL."""
    target = raw_path(raw_dir, call)
    if target.is_file() and target.stat().st_size:
        return target
    mp4 = raw_dir / f"{call.call_id}.mp4"
    temporary_wav = raw_dir / f".{call.call_id}.tmp.wav"
    raw_dir.mkdir(parents=True, exist_ok=True)
    temporary_wav.unlink(missing_ok=True)
    mp4.unlink(missing_ok=True)
    try:
        subprocess.run(
            ["curl", "--fail", "--location", "--silent", "--show-error", "--retry", "3", "--output", str(mp4), call.url],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(mp4), "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(temporary_wav)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if not temporary_wav.is_file() or not temporary_wav.stat().st_size:
            raise ExtractionFailure("decoder wrote no audio")
        temporary_wav.replace(target)
        return target
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ExtractionFailure("local download or decode failed") from exc
    finally:
        temporary_wav.unlink(missing_ok=True)
        mp4.unlink(missing_ok=True)


def vad_segments(audio: np.ndarray, vad) -> list[tuple[float, float]]:
    import torch
    from silero_vad import get_speech_timestamps

    timestamps = get_speech_timestamps(
        torch.from_numpy(np.asarray(audio, dtype=np.float32)),
        vad,
        sampling_rate=SR,
        min_silence_duration_ms=MIN_SILENCE_MS,
        min_speech_duration_ms=MIN_SPEECH_MS,
        speech_pad_ms=SPEECH_PAD_MS,
        return_seconds=True,
    )
    return [(float(item["start"]), float(item["end"])) for item in timestamps if item["end"] > item["start"]]


def embed_segment(encoder, audio: np.ndarray, start: float, end: float) -> np.ndarray:
    piece = audio[int(start * SR):int(end * SR)]
    if not len(piece):
        raise ExtractionFailure("empty speech segment")
    return normalise(encoder.embed_utterance(piece))


def cosine_kmeans(embeddings: np.ndarray, restarts: int = KMEANS_RESTARTS) -> tuple[np.ndarray, np.ndarray]:
    """Run two-cluster spherical k-means and retain the highest mean-cosine solution."""
    if len(embeddings) < 2:
        raise QuarantinedCall("too_few_embeddings")
    best: tuple[float, np.ndarray, np.ndarray] | None = None
    for seed in range(restarts):
        rng = np.random.default_rng(seed)
        centres = embeddings[rng.choice(len(embeddings), 2, replace=False)].copy()
        labels = np.zeros(len(embeddings), dtype=np.int8)
        for _ in range(30):
            labels = np.argmax(embeddings @ centres.T, axis=1).astype(np.int8)
            if not all(np.any(labels == cluster) for cluster in range(2)):
                break
            updated = np.stack([normalise(embeddings[labels == cluster].mean(axis=0)) for cluster in range(2)])
            if np.array_equal(np.argmax(embeddings @ updated.T, axis=1), labels):
                centres = updated
                break
            centres = updated
        if not all(np.any(labels == cluster) for cluster in range(2)):
            continue
        score = float(np.mean(np.max(embeddings @ centres.T, axis=1)))
        if best is None or score > best[0]:
            best = (score, labels.copy(), centres.copy())
    if best is None:
        raise QuarantinedCall("degenerate_clusters")
    _, labels, centres = best
    labels = np.argmax(embeddings @ centres.T, axis=1).astype(np.int8)
    if not all(np.any(labels == cluster) for cluster in range(2)):
        raise QuarantinedCall("degenerate_clusters")
    return labels, centres


def speaker_regions(audio: np.ndarray, vad, encoder, reference: np.ndarray) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Return trainee and agent VAD regions after the fixed-agent safety checks."""
    segments = vad_segments(audio, vad)
    long_indices = [index for index, (start, end) in enumerate(segments) if end - start >= MIN_EMBED_SECONDS]
    if len(long_indices) < 2:
        raise QuarantinedCall("too_few_embeddings")
    embeddings = np.stack([embed_segment(encoder, audio, *segments[index]) for index in long_indices])
    labels, centres = cosine_kmeans(embeddings)
    reference_similarities = reference @ centres.T
    agent_cluster = int(np.argmax(reference_similarities))
    if float(abs(reference_similarities[0] - reference_similarities[1])) < REFERENCE_MARGIN:
        raise QuarantinedCall("low_reference_margin")

    assignment: dict[int, int] = {index: int(label) for index, label in zip(long_indices, labels)}
    for index, (start, end) in enumerate(segments):
        if index in assignment:
            continue
        try:
            assignment[index] = int(np.argmax(embed_segment(encoder, audio, start, end) @ centres.T))
        except ExtractionFailure:
            assignment[index] = assignment.get(index - 1, agent_cluster)

    if assignment.get(0) != agent_cluster:
        raise QuarantinedCall("first_speaker_mismatch")
    trainee_cluster = 1 - agent_cluster
    trainee = [segment for index, segment in enumerate(segments) if assignment[index] == trainee_cluster]
    agent = [segment for index, segment in enumerate(segments) if assignment[index] == agent_cluster]
    trainee_seconds = sum(end - start for start, end in trainee)
    if trainee_seconds < MIN_TRAINEE_SECONDS:
        raise QuarantinedCall("short_trainee")
    return trainee, agent


def next_start(regions: list[tuple[float, float]], after: float) -> float | None:
    for start, _ in regions:
        if start > after:
            return start
    return None


def candidate_boundaries(trainee: list[tuple[float, float]], agent: list[tuple[float, float]]) -> list[Candidate]:
    """Apply the pre-registered behavioural complete/incomplete rules to trainee endings."""
    candidates: list[Candidate] = []
    for position, (_, end) in enumerate(trainee[:-1]):
        trainee_next = trainee[position + 1][0]
        agent_next = next_start(agent, end)
        gap_user = trainee_next - end
        gap_agent = NO_FUTURE_SPEECH if agent_next is None else agent_next - end
        pause_s = min(gap_user, gap_agent) if np.isfinite(gap_agent) else gap_user
        if np.isfinite(gap_agent) and gap_agent <= AGENT_RESPONSE_SECONDS and trainee_next > agent_next:
            rule_label = "complete"
        elif gap_user <= INCOMPLETE_RESUME_SECONDS and (not np.isfinite(gap_agent) or trainee_next < agent_next):
            rule_label = "incomplete"
        else:
            rule_label = "ambiguous"
        candidates.append(Candidate(position, end, pause_s, gap_user, gap_agent, rule_label))
    return candidates


def trainee_only(audio: np.ndarray, agent: Iterable[tuple[float, float]]) -> np.ndarray:
    result = audio.copy()
    for start, end in agent:
        result[max(0, int(start * SR)):min(len(result), int(end * SR))] = 0.0
    return result


def rows_for_call(wav: Path, call: Call, vad, encoder, reference: np.ndarray) -> tuple[list[dict], Counter, list[float], list[float]]:
    """Extract public-schema samples from one already-decoded local recording."""
    try:
        audio, sample_rate = sf.read(wav, dtype="float32", always_2d=False)
    except (OSError, RuntimeError) as exc:
        raise ExtractionFailure("decoded WAV could not be read") from exc
    if sample_rate != SR:
        raise ExtractionFailure("decoded WAV has the wrong sample rate")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    audio = np.asarray(audio, dtype=np.float32)
    trainee, agent = speaker_regions(audio, vad, encoder, reference)
    candidates = candidate_boundaries(trainee, agent)
    isolated = trainee_only(audio, agent)
    stats: Counter = Counter(candidates=len(candidates))
    rows: list[dict] = []
    pauses: list[float] = []
    latencies: list[float] = []
    for candidate in candidates:
        pauses.append(candidate.pause_s)
        if candidate.rule_label == "ambiguous":
            stats["dropped"] += 1
            continue
        endpoint = candidate.rule_label == "complete"
        if endpoint:
            stats["complete"] += 1
            latencies.append(candidate.gap_agent)
        else:
            stats["incomplete"] += 1
        end_sample = min(len(isolated), int((candidate.end + 0.2) * SR))
        clip = fit_window(isolated[:end_sample])
        rows.append({
            "audio": {"bytes": wav_bytes(clip), "path": f"private/{call.call_id}_{candidate.position:05d}.wav"},
            "endpoint_bool": endpoint,
            "text_label": endpoint,
            "audio_conf": None,
            "audio_reason": None,
            "ambiguous": False,
            "language": call.language,
            "dataset": f"private_{call.language}",
            "synthetic": False,
            "midfiller": False,
            "endfiller": False,
            "spoken_text": "",
            "speaker_id": call.call_id,
            "session": call.call_id,
            "chunk": candidate.position,
            "split": split_of(call.call_id),
            "llm_conf": 1.0,
            "call_id": call.call_id,
            "pause_s": candidate.pause_s,
            "gap_user": candidate.gap_user,
            "gap_agent": candidate.gap_agent,
            "rule_label": candidate.rule_label,
        })
    return rows, stats, pauses, latencies


def load_calls(path: Path, salt: str, languages: set[str] | None, limit: int) -> list[Call]:
    with path.open(newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if not raw_rows or {"language", "audio_file"} - set(raw_rows[0]):
        raise SystemExit("--calls must contain language,audio_file columns")
    calls: list[Call] = []
    for row in raw_rows:
        language = LANGUAGE_CODES.get(row["language"].strip().lower())
        if language is None:
            raise SystemExit("The CSV contains an unsupported language")
        if languages is not None and language not in languages:
            continue
        url = row["audio_file"].strip()
        source_name = unquote(Path(urlsplit(url).path).name)
        if not source_name or not url:
            raise SystemExit("The CSV contains an empty audio source")
        calls.append(Call(language, url, source_name, salted_call_id(source_name, salt)))
    if limit > 0:
        calls = calls[:limit]
    if len({call.call_id for call in calls}) != len(calls):
        raise SystemExit("The CSV has duplicate source file names, so stable private call IDs would collide")
    return calls


def start_writers(out_dir: Path, languages: Iterable[str], overwrite: bool) -> tuple[dict[str, pq.ParquetWriter], dict[str, Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    writers: dict[str, pq.ParquetWriter] = {}
    temporary: dict[str, Path] = {}
    schema = private_schema()
    for language in sorted(set(languages)):
        destination = out_dir / f"{language}.parquet"
        if destination.exists() and not overwrite:
            raise SystemExit("Private parquet output already exists; pass --overwrite to replace it atomically")
        temp = out_dir / f".{language}.extract.tmp.parquet"
        temp.unlink(missing_ok=True)
        writers[language] = pq.ParquetWriter(temp, schema, compression="snappy")
        temporary[language] = temp
    return writers, temporary


def commit_outputs(writers: dict[str, pq.ParquetWriter], temporary: dict[str, Path], out_dir: Path) -> None:
    for writer in writers.values():
        writer.close()
    for language, temp in temporary.items():
        temp.replace(out_dir / f"{language}.parquet")


def discard_temporary_outputs(writers: dict[str, pq.ParquetWriter], temporary: dict[str, Path]) -> None:
    for writer in writers.values():
        writer.close()
    for temp in temporary.values():
        temp.unlink(missing_ok=True)


def print_summary(totals: dict[str, Counter], pauses: dict[str, list[float]], latencies: dict[str, list[float]]) -> None:
    print("| language | sessions used | quarantined | failed | boundaries | complete | incomplete | dropped | agent latency | pause distribution |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for language in sorted(totals):
        stats = totals[language]
        print(
            f"| {language} | {stats['used']} | {stats['quarantined']} | {stats['failed']} | {stats['candidates']} | "
            f"{stats['complete']} | {stats['incomplete']} | {stats['dropped']} | {percentile_summary(latencies[language])} | "
            f"{percentile_summary(pauses[language])} |"
        )
        if stats["quarantined"]:
            reasons = ", ".join(f"{reason}={count}" for reason, count in sorted(stats.items()) if reason.startswith("quarantine_"))
            print(f"  quarantine reasons: {reasons}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calls", type=Path, default=ROOT / "data" / "private" / "additional-data.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "private")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "private" / "raw")
    parser.add_argument("--agent-reference", type=Path, default=ROOT / "data" / "private" / "agent_reference.npy")
    parser.add_argument("--workers", type=int, default=4, help="parallel download and decode workers")
    parser.add_argument("--languages", nargs="*", choices=sorted(LANG_NAMES), help="optional language codes to extract")
    parser.add_argument("--limit", type=int, default=0, help="limit calls after language filtering for a local smoke test")
    parser.add_argument("--overwrite", action="store_true", help="atomically replace existing private language parquets")
    args = parser.parse_args()
    if args.workers < 1:
        raise SystemExit("--workers must be at least one")
    if not shutil.which("curl") or not shutil.which("ffmpeg"):
        raise SystemExit("curl and ffmpeg are required")
    load_dotenv(ROOT / ".env")
    salt = os.environ.get("PRIVATE_CALL_SALT")
    if not salt:
        raise SystemExit("Set PRIVATE_CALL_SALT in .env before extracting private calls")
    if not args.agent_reference.is_file():
        raise SystemExit("The fixed agent reference embedding is missing")
    reference = normalise(np.load(args.agent_reference))
    calls = load_calls(args.calls, salt, set(args.languages) if args.languages else None, args.limit)
    if not calls:
        raise SystemExit("No calls matched the requested language filter")

    import torch
    from resemblyzer import VoiceEncoder
    from silero_vad import load_silero_vad

    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    vad = load_silero_vad()
    encoder = VoiceEncoder(verbose=False)
    writers, temporary = start_writers(args.out_dir, (call.language for call in calls), args.overwrite)
    totals: dict[str, Counter] = defaultdict(Counter)
    pauses: dict[str, list[float]] = defaultdict(list)
    latencies: dict[str, list[float]] = defaultdict(list)
    pending: dict[Future[Path], Call] = {}
    iterator = iter(calls)
    completed = 0

    def submit_next(pool: ThreadPoolExecutor) -> bool:
        try:
            call = next(iterator)
        except StopIteration:
            return False
        pending[pool.submit(download_and_decode, call, args.raw_dir)] = call
        return True

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for _ in range(min(args.workers, len(calls))):
                submit_next(pool)
            while pending:
                done, _ = wait(pending, return_when="FIRST_COMPLETED")
                future = next(iter(done))
                call = pending.pop(future)
                submit_next(pool)
                completed += 1
                try:
                    wav = future.result()
                    rows, stats, call_pauses, call_latencies = rows_for_call(wav, call, vad, encoder, reference)
                except QuarantinedCall as exc:
                    totals[call.language]["quarantined"] += 1
                    totals[call.language][f"quarantine_{exc}"] += 1
                except (ExtractionFailure, OSError, RuntimeError):
                    totals[call.language]["failed"] += 1
                else:
                    totals[call.language]["used"] += 1
                    totals[call.language].update(stats)
                    pauses[call.language].extend(call_pauses)
                    latencies[call.language].extend(call_latencies)
                    if rows:
                        writers[call.language].write_table(pa.Table.from_pylist(rows, schema=private_schema()), row_group_size=2_000)
                if completed % 25 == 0 or completed == len(calls):
                    print(f"processed {completed}/{len(calls)} sessions", flush=True)
        commit_outputs(writers, temporary, args.out_dir)
    except BaseException:
        discard_temporary_outputs(writers, temporary)
        raise
    print_summary(totals, pauses, latencies)


if __name__ == "__main__":
    main()
