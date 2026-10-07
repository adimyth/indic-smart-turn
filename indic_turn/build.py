"""Step 3: turn labelled chunks + downloaded shards into smart-turn style training
samples (16 kHz audio, last 8 s, `endpoint_bool`), speaker-disjoint splits.

Sample construction for a labelled chunk k of one speaker's session:
  context = preceding chunks of the same speaker, joined with simulated gaps
            (short gap after an incomplete chunk, long gap after a complete one,
             because the other party would have spoken in between)
  audio   = last 8 s of (context + chunk), trailing silence trimmed to 0.2 s
Extra negatives: a chunk cut at an internal pause ("pausecut"), which is exactly
the situation where a VAD would fire mid-turn in production.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, random
from collections import defaultdict
from pathlib import Path
import numpy as np, pyarrow as pa, pyarrow.parquet as pq, soundfile as sf
from huggingface_hub import hf_hub_download
from .common import DATA, HF_DATASET, SR, hf_token

WINDOW = 8 * SR
TRAIL = int(0.2 * SR)
AUDIO_VERDICTS = {"complete": True, "incomplete": False}
AUDIO_COLUMNS = ("text_label", "audio_conf", "audio_reason", "ambiguous")

def split_of(speaker_id: str, dev=0.10, test=0.10) -> str:
    h = int(hashlib.sha1(speaker_id.encode()).hexdigest(), 16) % 10000 / 10000
    return "test" if h < test else "dev" if h < test + dev else "train"

def decode(flac_bytes: bytes) -> np.ndarray:
    x, sr = sf.read(io.BytesIO(flac_bytes), dtype="float32", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        import librosa
        x = librosa.resample(x, orig_sr=sr, target_sr=SR)
    return x.astype(np.float32)

def frame_energy(x: np.ndarray, win=400, hop=160):
    n = max(0, (len(x) - win) // hop + 1)
    if n == 0:
        return np.zeros(0), hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    return np.sqrt((x[idx] ** 2).mean(axis=1) + 1e-12), hop

def trim_trailing_silence(x: np.ndarray, rel=0.03, floor=1e-3) -> np.ndarray:
    e, hop = frame_energy(x)
    if len(e) == 0:
        return x
    thr = max(floor, rel * e.max())
    voiced = np.where(e > thr)[0]
    if len(voiced) == 0:
        return x
    end = min(len(x), (voiced[-1] + 1) * hop + 400)
    return x[:end]

def internal_pauses(x: np.ndarray, min_pause=0.18, rel=0.03, floor=1e-3):
    """Return sample positions of the centres of internal pauses >= min_pause seconds."""
    e, hop = frame_energy(x)
    if len(e) == 0:
        return []
    thr = max(floor, rel * e.max())
    quiet = e <= thr
    out, i, n = [], 0, len(e)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            dur = (j - i) * hop / SR
            start_s, end_s = i * hop / SR, j * hop / SR
            # ignore leading / trailing silence
            if dur >= min_pause and start_s > 0.5 and end_s < len(x) / SR - 0.3:
                out.append(int(((i + j) / 2) * hop))
            i = j
        else:
            i += 1
    return out

def fit_window(x: np.ndarray) -> np.ndarray:
    x = trim_trailing_silence(x)
    x = np.concatenate([x, np.zeros(TRAIL, np.float32)])
    if len(x) > WINDOW:
        x = x[-WINDOW:]
    return x

def load_shard_audio(shard: str, rows_needed: set):
    path = hf_hub_download(HF_DATASET, shard, repo_type="dataset", token=hf_token(),
                           cache_dir=str(DATA / "hf_cache"))
    pf = pq.ParquetFile(path)
    out, base = {}, 0
    for g in range(pf.metadata.num_row_groups):
        n = pf.metadata.row_group(g).num_rows
        want = [r - base for r in rows_needed if base <= r < base + n]
        if want:
            col = pf.read_row_group(g, columns=["audio_filepath"]).column(0)
            for w in want:
                out[base + w] = col[w].as_py()["bytes"]
        base += n
    return out

def apply_short_cap(labels, short_cap: float, max_short_s: float = 1.5, seed: int = 0):
    """Downsample segments shorter than `max_short_s` so they are at most `short_cap` of the rows.
    Deterministic: sorted by (session, chunk) and sampled with a fixed seed, so re-runs agree."""
    if not short_cap or short_cap >= 1:
        return labels
    long_ = [r for r in labels if r["duration"] >= max_short_s]
    short = sorted((r for r in labels if r["duration"] < max_short_s), key=lambda r: (r["session"], r["chunk"]))
    keep_n = int(short_cap / (1 - short_cap) * len(long_))
    if len(short) > keep_n:
        short = random.Random(seed).sample(short, keep_n)
    out = long_ + short
    out.sort(key=lambda r: (r["session"], r["chunk"]))
    return out

def build_language(lang: str, rng: random.Random, pausecut_frac: float, max_rows: int, short_cap: float = 0.0):
    labels = [json.loads(l) for l in (DATA / "labels" / f"{lang}.jsonl").open()]
    if max_rows:
        labels = labels[:max_rows]
    n0 = len(labels); labels = apply_short_cap(labels, short_cap)
    if len(labels) != n0:
        print(f"[{lang}] short-segment cap {short_cap:.0%}: {n0} -> {len(labels)} labelled chunks", flush=True)
    sessions = defaultdict(list)
    for r in labels:
        sessions[r["session"]].append(r)
    for s in sessions.values():
        s.sort(key=lambda r: r["chunk"])
    by_shard = defaultdict(set)
    for r in labels:
        by_shard[r["shard"]].add(r["row"])
    print(f"[{lang}] {len(labels)} labelled chunks, {len(sessions)} sessions, {len(by_shard)} shards", flush=True)
    audio = {}
    for shard, rows in by_shard.items():
        got = load_shard_audio(shard, rows)
        audio.update({(shard, r): b for r, b in got.items()})
        print(f"[{lang}]   {shard}: {len(got)} clips", flush=True)

    samples = []
    for sid, chunks in sessions.items():
        wavs = {}
        for c in chunks:
            b = audio.get((c["shard"], c["row"]))
            if b:
                wavs[c["chunk"]] = decode(b)
        for i, c in enumerate(chunks):
            if c["chunk"] not in wavs:
                continue
            cur = wavs[c["chunk"]]
            # ---- context from preceding consecutive chunks ----
            parts, total, j = [cur], len(cur), i - 1
            while total < WINDOW and j >= 0 and chunks[j]["chunk"] == chunks[j + 1]["chunk"] - 1 and chunks[j]["chunk"] in wavs:
                prev = chunks[j]
                gap = rng.uniform(1.5, 4.0) if prev["endpoint_bool"] else rng.uniform(0.15, 0.6)
                g = np.zeros(int(gap * SR), np.float32)
                parts = [wavs[prev["chunk"]], g] + parts
                total += len(g) + len(wavs[prev["chunk"]]); j -= 1
            full = np.concatenate(parts) if len(parts) > 1 else cur
            ctx_len = len(full) - len(cur)
            base = {"language": lang, "speaker_id": c["speaker_id"], "session": sid, "chunk": c["chunk"],
                    "split": split_of(c["speaker_id"]), "synthetic": False, "midfiller": False, "endfiller": False,
                    "spoken_text": c["text"], "llm_conf": c["llm_conf"]}
            samples.append({**base, "audio": fit_window(full), "endpoint_bool": bool(c["endpoint_bool"]),
                            "dataset": f"indicvoices_{lang}"})
            # ---- pause-cut negative ----
            if len(cur) >= 2.0 * SR and rng.random() < pausecut_frac:
                ps = internal_pauses(cur)
                if ps:
                    cut = rng.choice(ps)
                    samples.append({**base, "audio": fit_window(full[: ctx_len + cut]), "endpoint_bool": False,
                                    "dataset": f"indicvoices_{lang}_pausecut", "spoken_text": ""})
    return samples

def save(samples, lang):
    """Write parquet with the same columns as pipecat's datasets (audio = struct<bytes,path>)."""
    import pyarrow as pa
    out = DATA / "built"; out.mkdir(parents=True, exist_ok=True)
    def wav_bytes(x):
        b = io.BytesIO(); sf.write(b, x, SR, format="WAV", subtype="PCM_16"); return b.getvalue()
    cols = {
        "audio": [{"bytes": wav_bytes(s["audio"]), "path": f"{s['session']}_{s['chunk']}.wav"} for s in samples],
        "endpoint_bool": [s["endpoint_bool"] for s in samples],
        "language": [s["language"] for s in samples], "dataset": [s["dataset"] for s in samples],
        "synthetic": [False] * len(samples), "midfiller": [False] * len(samples), "endfiller": [False] * len(samples),
        "spoken_text": [s["spoken_text"] for s in samples], "speaker_id": [s["speaker_id"] for s in samples],
        "session": [s["session"] for s in samples], "chunk": [s["chunk"] for s in samples],
        "split": [s["split"] for s in samples], "llm_conf": [float(s["llm_conf"]) for s in samples],
    }
    schema = pa.schema([("audio", pa.struct([("bytes", pa.binary()), ("path", pa.string())])),
                        ("endpoint_bool", pa.bool_()), ("language", pa.string()), ("dataset", pa.string()),
                        ("synthetic", pa.bool_()), ("midfiller", pa.bool_()), ("endfiller", pa.bool_()),
                        ("spoken_text", pa.string()), ("speaker_id", pa.string()), ("session", pa.string()),
                        ("chunk", pa.int32()), ("split", pa.string()), ("llm_conf", pa.float32())])
    tbl = pa.Table.from_pydict(cols, schema=schema)
    path = out / f"{lang}.parquet"
    pq.write_table(tbl, path, row_group_size=2000)
    pos = sum(cols["endpoint_bool"]); n = len(samples)
    by_split = defaultdict(int)
    for s in cols["split"]:
        by_split[s] += 1
    print(f"[{lang}] saved {n} samples to {path} ({path.stat().st_size/1e6:.0f} MB): {pos} complete / {n-pos} incomplete "
          f"({100*pos/n:.0f}% positive); splits {dict(by_split)}", flush=True)

def audio_key(session: str, chunk: int, dataset: str, wav: bytes) -> str:
    return f"{session}|{chunk}|{dataset}|{hashlib.md5(wav).hexdigest()[:10]}"

def load_audio_labels(path: Path):
    """Load one Gemini result per audio key, preferring a successful retry over an earlier error."""
    labels = {}
    duplicate_keys = 0
    for line in path.open():
        row = json.loads(line)
        key = row.get("key")
        if not key:
            continue
        old = labels.get(key)
        if old is not None:
            duplicate_keys += 1
        if old is None or row.get("verdict") in AUDIO_VERDICTS or old.get("verdict") not in AUDIO_VERDICTS:
            labels[key] = row
    if duplicate_keys:
        print(f"[{path.stem.removesuffix('.audio')}] {duplicate_keys} duplicate audio-label keys; preferred successful retries", flush=True)
    return labels

def audio_schema(source_schema):
    fields = []
    inserted = False
    additions = [
        ("text_label", pa.bool_()),
        ("audio_conf", pa.float32()),
        ("audio_reason", pa.string()),
        ("ambiguous", pa.bool_()),
    ]
    for field in source_schema:
        if field.name in AUDIO_COLUMNS:
            continue
        fields.append(field)
        if field.name == "endpoint_bool":
            fields.extend(pa.field(name, type_) for name, type_ in additions)
            inserted = True
    if not inserted:
        fields.extend(pa.field(name, type_) for name, type_ in additions)
    return pa.schema(fields, metadata=source_schema.metadata)

def _new_audio_stats():
    return {"segments": 0, "pausecuts": 0, "pausecuts_kept": 0, "pausecuts_dropped": 0, "errored": 0,
            "missing": 0, "invalid": 0, "final": 0, "positive": 0, "agreements": 0, "compared": 0,
            "splits": defaultdict(int)}

def print_audio_summary(lang: str, stats):
    agreement = "n/a" if not stats["compared"] else f"{stats['agreements']}/{stats['compared']} = {100 * stats['agreements'] / stats['compared']:.1f}%"
    positive = "n/a" if not stats["final"] else f"{100 * stats['positive'] / stats['final']:.1f}%"
    print(
        f"[{lang}] segments={stats['segments']}; pause-cuts kept={stats['pausecuts_kept']} dropped={stats['pausecuts_dropped']} "
        f"(seen={stats['pausecuts']}); errored={stats['errored']}; final={stats['final']}; positive={positive}; "
        f"splits={dict(sorted(stats['splits'].items()))}; text-vs-audio agreement={agreement}",
        flush=True,
    )

def apply_audio_labels(lang: str, batch_size: int = 250):
    """Atomically replace one built parquet with Gemini-primary labels without rebuilding audio samples."""
    path = DATA / "built" / f"{lang}.parquet"
    labels_path = DATA / "labels" / f"{lang}.audio.jsonl"
    if not path.exists():
        print(f"[{lang}] skipping: no built parquet at {path}", flush=True)
        return None
    if not labels_path.exists():
        print(f"[{lang}] skipping: no audio labels at {labels_path}", flush=True)
        return None
    labels = load_audio_labels(labels_path)
    source = pq.ParquetFile(path)
    if len(labels) < source.metadata.num_rows:
        print(f"[{lang}] skipping: {len(labels)} audio-label keys for {source.metadata.num_rows} built rows (labelling is incomplete)", flush=True)
        return None
    schema = audio_schema(source.schema_arrow)
    temp_path = path.with_name(f".{path.stem}.apply-audio-labels.tmp.parquet")
    if temp_path.exists():
        temp_path.unlink()
    stats = _new_audio_stats()
    try:
        with pq.ParquetWriter(temp_path, schema, compression="snappy") as writer:
            for batch in source.iter_batches(batch_size=batch_size):
                data = batch.to_pydict()
                base_columns = [name for name in schema.names if name not in AUDIO_COLUMNS and name != "endpoint_bool"]
                out = {name: [] for name in schema.names}
                has_text_label = "text_label" in data
                for i in range(batch.num_rows):
                    dataset = data["dataset"][i]
                    pausecut = dataset.endswith("_pausecut")
                    wav = data["audio"][i]["bytes"]
                    key = audio_key(data["session"][i], data["chunk"][i], dataset, wav)
                    label = labels.get(key)
                    if label is None:
                        stats["missing"] += 1
                        continue
                    verdict = label.get("verdict")
                    if verdict == "error":
                        stats["errored"] += 1
                        continue
                    if verdict not in AUDIO_VERDICTS:
                        stats["invalid"] += 1
                        continue
                    audio_label = AUDIO_VERDICTS[verdict]
                    confidence = float(label.get("confidence", 0.0))
                    if pausecut:
                        stats["pausecuts"] += 1
                        if audio_label or confidence < 0.7:
                            stats["pausecuts_dropped"] += 1
                            continue
                        text_label, ambiguous = None, False
                        stats["pausecuts_kept"] += 1
                    else:
                        stats["segments"] += 1
                        text_label = data["text_label"][i] if has_text_label else data["endpoint_bool"][i]
                        text_label = bool(text_label)
                        ambiguous = audio_label != text_label
                        stats["compared"] += 1
                        stats["agreements"] += not ambiguous
                    for name in base_columns:
                        out[name].append(data[name][i])
                    split = data["split"][i]
                    if not pausecut and ambiguous and split in ("test", "test_ambiguous"):
                        out["split"][-1] = "test_ambiguous"
                    out["endpoint_bool"].append(audio_label)
                    out["text_label"].append(text_label)
                    out["audio_conf"].append(confidence)
                    out["audio_reason"].append(str(label.get("reason", "")))
                    out["ambiguous"].append(ambiguous)
                    stats["final"] += 1
                    stats["positive"] += audio_label
                    stats["splits"][out["split"][-1]] += 1
                if out["audio"]:
                    writer.write_table(pa.Table.from_pydict(out, schema=schema), row_group_size=batch_size)
        if stats["missing"] or stats["invalid"]:
            raise RuntimeError(f"[{lang}] refusing to replace {path}: {stats['missing']} missing and {stats['invalid']} invalid audio labels")
        os.replace(temp_path, path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
    print_audio_summary(lang, stats)
    return stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", help="languages to build, or languages whose audio labels should be applied")
    ap.add_argument("--apply-audio-labels", action="store_true", help="rewrite existing built parquets with Gemini audio verdicts; never rebuilds shards or audio")
    ap.add_argument("--pausecut-frac", type=float, default=1.0, help="prob. of adding a pause-cut candidate per chunk >= 2 s (Gemini audio labels decide if it is kept)")
    ap.add_argument("--short-cap", type=float, default=0.2, help="max share of labelled chunks shorter than 1.5 s (0 = no cap)")
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    if a.apply_audio_labels:
        langs = a.langs or [p.stem for p in sorted((DATA / "built").glob("*.parquet")) if (DATA / "labels" / f"{p.stem}.audio.jsonl").exists()]
        if not langs:
            ap.error("--apply-audio-labels found no built parquets with audio labels")
        for lang in langs:
            apply_audio_labels(lang)
        return
    if not a.langs:
        ap.error("--langs is required unless --apply-audio-labels is used")
    for lang in a.langs:
        samples = build_language(lang, random.Random(a.seed), a.pausecut_frac, a.max_rows, a.short_cap)
        save(samples, lang)

if __name__ == "__main__":
    main()
