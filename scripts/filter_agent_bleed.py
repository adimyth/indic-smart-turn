#!/usr/bin/env python3
"""Remove private clips whose voiced samples match the fixed agent voice too closely.

The script runs only on local private parquets. It keeps rows with fewer than 0.8 seconds of samples above the amplitude floor, and atomically rewrites every input parquet without exposing clip identifiers or audio.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import soundfile as sf
from resemblyzer import VoiceEncoder

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data" / "private"
AMPLITUDE_FLOOR = 1e-4
MIN_VOICED_SECONDS = 0.8
AGENT_SIMILARITY = 0.80


def normalise(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-12:
        raise ValueError("zero-norm embedding")
    return vector / norm


def resembles_agent(wav: bytes, encoder: VoiceEncoder, reference: np.ndarray) -> tuple[bool, bool]:
    """Return whether a clip is agent-like and whether it had enough voiced audio to score."""
    audio, sample_rate = sf.read(io.BytesIO(wav), dtype="float32", always_2d=False)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    voiced = np.asarray(audio, dtype=np.float32)[np.abs(audio) > AMPLITUDE_FLOOR]
    if len(voiced) < MIN_VOICED_SECONDS * sample_rate:
        return False, False
    embedding = normalise(encoder.embed_utterance(voiced))
    return float(embedding @ reference) >= AGENT_SIMILARITY, True


def filter_parquet(path: Path, encoder: VoiceEncoder, reference: np.ndarray, batch_size: int) -> dict[str, int]:
    """Atomically replace one private parquet with rows that pass the agent-voice gate."""
    source = pq.ParquetFile(path)
    temporary = path.with_name(f".{path.stem}.agent-bleed.tmp.parquet")
    temporary.unlink(missing_ok=True)
    stats = {"input": 0, "dropped": 0, "short": 0, "kept": 0}
    try:
        with pq.ParquetWriter(temporary, source.schema_arrow, compression="snappy") as writer:
            for batch in source.iter_batches(batch_size=batch_size):
                columns = batch.to_pydict()
                keep: list[int] = []
                for index, audio in enumerate(columns["audio"]):
                    stats["input"] += 1
                    drop, scored = resembles_agent(audio["bytes"], encoder, reference)
                    if not scored:
                        stats["short"] += 1
                    if drop:
                        stats["dropped"] += 1
                    else:
                        keep.append(index)
                if keep:
                    filtered = {name: [values[index] for index in keep] for name, values in columns.items()}
                    writer.write_table(pa.Table.from_pydict(filtered, schema=source.schema_arrow))
                    stats["kept"] += len(keep)
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=PRIVATE)
    parser.add_argument("--agent-reference", type=Path, default=PRIVATE / "agent_reference.npy")
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be at least one")
    if not args.agent_reference.is_file():
        raise SystemExit("The fixed agent reference embedding is missing")
    paths = sorted(args.source.glob("*.parquet"))
    if not paths:
        raise SystemExit("No private parquet files found")
    reference = normalise(np.load(args.agent_reference))
    encoder = VoiceEncoder(verbose=False)
    print("| language | input | dropped | kept | too short to score |")
    print("|---|---:|---:|---:|---:|")
    for path in paths:
        stats = filter_parquet(path, encoder, reference, args.batch_size)
        print(f"| {path.stem} | {stats['input']} | {stats['dropped']} | {stats['kept']} | {stats['short']} |")


if __name__ == "__main__":
    main()
