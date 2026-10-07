#!/usr/bin/env python3
"""Build private end-of-turn samples locally from a CSV of mixed user-and-agent call recordings.

The CSV must contain `language,audio_file`. Stereo recordings require `--user-channel`; mono recordings require `--agent-reference` plus a Hugging Face token accepted by the pyannote diarization models. The script never uploads recordings or calls a third-party inference API.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from indic_turn.build import fit_window
from indic_turn.common import LANG_NAMES, SR

MAX_RESPONSE_DELAY = 2.0
OVERLAP_WINDOW = 1.5
MIN_PAUSE = 0.2


@dataclass(frozen=True)
class Boundary:
    at: float
    label: bool | None


def require_executable(name: str) -> None:
    if not shutil.which(name):
        raise RuntimeError(f"{name} is required but was not found on PATH")


def audio_channels(path: Path) -> int:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise RuntimeError(f"{path} has no audio stream")
    return int(streams[0]["channels"])


def decode_audio(path: Path, channels: int) -> np.ndarray:
    result = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-f", "f32le", "-ar", str(SR), "-ac", str(channels), "pipe:1"],
        check=True,
        capture_output=True,
    )
    raw = np.frombuffer(result.stdout, dtype=np.float32)
    if not len(raw) or len(raw) % channels:
        raise RuntimeError(f"ffmpeg produced malformed PCM for {path}")
    return raw.reshape(-1, channels).T.copy()


def merge_regions(regions: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[tuple[float, float]] = []
    for start, end in sorted(regions):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def silero_vad() -> Callable[[np.ndarray], list[tuple[float, float]]]:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("Install torch to use the local Silero VAD extractor") from exc
    model, utils = torch.hub.load("snakers4/silero-vad", "silero_vad", trust_repo=True)
    get_speech_timestamps = utils[0]

    def detect(audio: np.ndarray) -> list[tuple[float, float]]:
        timestamps = get_speech_timestamps(torch.from_numpy(audio.copy()), model, sampling_rate=SR)
        return merge_regions((item["start"] / SR, item["end"] / SR) for item in timestamps)

    return detect


def next_start_after(regions: list[tuple[float, float]], at: float) -> float | None:
    for start, _ in regions:
        if start > at:
            return start
    return None


def label_boundaries(user_regions: list[tuple[float, float]], agent_regions: list[tuple[float, float]]) -> list[Boundary]:
    out: list[Boundary] = []
    for index, (_, end) in enumerate(user_regions[:-1]):
        user_next = user_regions[index + 1][0]
        if user_next - end < MIN_PAUSE:
            continue
        agent_next = next_start_after(agent_regions, end)
        agent_close = agent_next is not None and agent_next - end <= MAX_RESPONSE_DELAY
        user_close = user_next - end <= MAX_RESPONSE_DELAY
        if agent_close and user_close and abs(agent_next - user_next) <= OVERLAP_WINDOW:
            out.append(Boundary(end, None))
        elif agent_close and (not user_close or agent_next < user_next):
            out.append(Boundary(end, True))
        elif user_close and (not agent_close or user_next < agent_next):
            out.append(Boundary(end, False))
        else:
            out.append(Boundary(end, None))
    return out


def zero_regions(audio: np.ndarray, regions: Iterable[tuple[float, float]]) -> np.ndarray:
    result = audio.copy()
    for start, end in regions:
        result[max(0, int(start * SR)):min(len(result), int(end * SR))] = 0
    return result


def call_id(path: Path, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{path.name}".encode()).hexdigest()[:20]


def split_of(call: str, salt: str) -> str:
    value = int(hashlib.sha256(f"{salt}:split:{call}".encode()).hexdigest(), 16) % 10_000
    return "train" if value < 7_000 else "test"


class MonoDiarizer:
    """Tag pyannote diarization speakers against a fixed agent voice reference."""

    def __init__(self, agent_reference: Path, hf_token: str):
        try:
            import torch
            from pyannote.audio import Inference, Model, Pipeline
        except ImportError as exc:
            raise RuntimeError("Mono extraction needs pyannote.audio and torch; install them before running this script") from exc
        self.torch = torch
        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
        self.embedding = Inference(Model.from_pretrained("pyannote/embedding", use_auth_token=hf_token), window="whole")
        reference = decode_audio(agent_reference, 1)[0]
        self.reference = self._embed(reference)

    def _embed(self, audio: np.ndarray) -> np.ndarray:
        if not len(audio):
            raise RuntimeError("Cannot embed empty audio")
        embedding = np.asarray(self.embedding({"waveform": self.torch.from_numpy(audio[None, :]), "sample_rate": SR})).reshape(-1)
        return embedding / max(np.linalg.norm(embedding), 1e-12)

    def regions(self, path: Path, mixed_audio: np.ndarray) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
        diarization = self.pipeline(str(path))
        by_speaker: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            by_speaker[str(speaker)].append((float(segment.start), float(segment.end)))
        if len(by_speaker) < 2:
            raise RuntimeError(f"{path}: diarization did not find two speakers")
        scores: dict[str, float] = {}
        for speaker, spans in by_speaker.items():
            pieces = [mixed_audio[int(start * SR):int(end * SR)] for start, end in merge_regions(spans)]
            probe = np.concatenate(pieces)[: 60 * SR] if pieces else np.zeros(0, np.float32)
            scores[speaker] = float(np.dot(self.reference, self._embed(probe)))
        agent = max(scores, key=scores.get)
        agent_regions = merge_regions(by_speaker[agent])
        user_regions = merge_regions(span for speaker, spans in by_speaker.items() if speaker != agent for span in spans)
        return user_regions, agent_regions


def private_schema() -> pa.Schema:
    return pa.schema([
        ("audio", pa.struct([("bytes", pa.binary()), ("path", pa.string())])),
        ("endpoint_bool", pa.bool_()), ("language", pa.string()), ("dataset", pa.string()),
        ("synthetic", pa.bool_()), ("midfiller", pa.bool_()), ("endfiller", pa.bool_()),
        ("spoken_text", pa.string()), ("speaker_id", pa.string()), ("session", pa.string()),
        ("chunk", pa.int32()), ("split", pa.string()), ("llm_conf", pa.float32()),
        ("call_id", pa.string()), ("ambiguous", pa.bool_()),
    ])


def wav_bytes(audio: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, audio, SR, format="WAV", subtype="PCM_16")
    return buffer.getvalue()


def write_language(out_dir: Path, language: str, rows: list[dict]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=private_schema())
    path = out_dir / f"{language}.parquet"
    pq.write_table(table, path, row_group_size=2_000)
    print(f"[{language}] wrote {len(rows)} unambiguous samples to {path}")


def process_call(path: Path, language: str, salt: str, vad: Callable[[np.ndarray], list[tuple[float, float]]], user_channel: int | None, diarizer: MonoDiarizer | None) -> tuple[list[dict], Counter]:
    channels = audio_channels(path)
    audio = decode_audio(path, channels)
    if channels >= 2:
        if user_channel is None or not 0 <= user_channel < channels:
            raise RuntimeError(f"{path}: pass --user-channel for {channels}-channel recordings")
        user_audio = audio[user_channel]
        agent_audio = np.mean(np.delete(audio, user_channel, axis=0), axis=0)
        user_regions, agent_regions = vad(user_audio), vad(agent_audio)
    else:
        if diarizer is None:
            raise RuntimeError(f"{path}: mono recordings need --agent-reference for local diarization")
        mixed = audio[0]
        user_regions, agent_regions = diarizer.regions(path, mixed)
        user_audio = zero_regions(mixed, agent_regions)
    identifier = call_id(path, salt)
    stats: Counter = Counter(calls=1)
    rows: list[dict] = []
    for number, boundary in enumerate(label_boundaries(user_regions, agent_regions)):
        if boundary.label is None:
            stats["dropped"] += 1
            continue
        stats["complete" if boundary.label else "incomplete"] += 1
        clipped = fit_window(user_audio[:min(len(user_audio), int((boundary.at + 0.2) * SR))])
        rows.append({
            "audio": {"bytes": wav_bytes(clipped), "path": f"private/{identifier}_{number:05d}.wav"},
            "endpoint_bool": boundary.label, "language": language, "dataset": f"private_{language}",
            "synthetic": False, "midfiller": False, "endfiller": False, "spoken_text": "",
            "speaker_id": identifier, "session": identifier, "chunk": number, "split": split_of(identifier, salt),
            "llm_conf": 1.0, "call_id": identifier, "ambiguous": False,
        })
    stats["candidates"] = stats["complete"] + stats["incomplete"] + stats["dropped"]
    return rows, stats


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calls", required=True, type=Path, help="CSV with language,audio_file columns")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "data" / "private")
    ap.add_argument("--salt", default=os.environ.get("PRIVATE_CALL_SALT"), help="required stable secret for call-id hashing")
    ap.add_argument("--user-channel", type=int, default=None, help="zero-based user channel for recordings with separate channels")
    ap.add_argument("--agent-reference", type=Path, help="fixed agent-voice audio used only for mono-call diarization")
    ap.add_argument("--hf-token", default=os.environ.get("HF_TOKEN"), help="token for local pyannote model download when mono calls are present")
    args = ap.parse_args()
    if not args.salt:
        raise SystemExit("Set PRIVATE_CALL_SALT or pass --salt; call IDs must remain salted and reproducible")
    require_executable("ffmpeg")
    require_executable("ffprobe")
    with args.calls.open(newline="") as handle:
        calls = list(csv.DictReader(handle))
    if not calls or set(("language", "audio_file")) - set(calls[0]):
        raise SystemExit("--calls must contain language,audio_file columns")
    invalid = sorted({row["language"] for row in calls if row["language"] not in LANG_NAMES})
    if invalid:
        raise SystemExit(f"Unsupported language codes: {', '.join(invalid)}")
    has_mono = any(audio_channels(Path(row["audio_file"])) == 1 for row in calls)
    if has_mono and (not args.agent_reference or not args.hf_token):
        raise SystemExit("Mono calls require --agent-reference and HF_TOKEN for local pyannote diarization")
    vad = silero_vad()
    diarizer = MonoDiarizer(args.agent_reference, args.hf_token) if has_mono else None
    rows_by_language: dict[str, list[dict]] = defaultdict(list)
    totals: dict[str, Counter] = defaultdict(Counter)
    for row in calls:
        path = Path(row["audio_file"]).expanduser()
        if not path.is_file():
            raise SystemExit(f"Missing audio file: {path}")
        rows, stats = process_call(path, row["language"], args.salt, vad, args.user_channel, diarizer)
        rows_by_language[row["language"]].extend(rows)
        totals[row["language"]].update(stats)
    print("| language | calls | candidates | complete | incomplete | dropped |")
    print("|---|---:|---:|---:|---:|---:|")
    for language in sorted(rows_by_language):
        stats = totals[language]
        print(f"| {language} | {stats['calls']} | {stats['candidates']} | {stats['complete']} | {stats['incomplete']} | {stats['dropped']} |")
        write_language(args.out_dir, language, rows_by_language[language])


if __name__ == "__main__":
    main()
