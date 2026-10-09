#!/usr/bin/env python3
"""Show live Gemini-label progress from private parquet and resumable JSONL files.

Run `python scripts/label_progress.py` in a terminal. It refreshes once per second and reports exact successful verdict counts, total rate, and ETA without displaying clip content or identifiers.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data" / "private"


def successful_labels(path: Path) -> int:
    if not path.exists():
        return 0
    keys = set()
    with path.open() as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("verdict") in {"complete", "incomplete"}:
                keys.add(row.get("key"))
    return len(keys)


def render(completed: dict[str, int], totals: dict[str, int], start_count: int, started: float) -> str:
    progress = {language: min(completed[language], total) for language, total in totals.items()}
    complete = sum(progress.values())
    total = sum(totals.values())
    elapsed = max(time.monotonic() - started, 1e-9)
    rate = (complete - start_count) / elapsed
    remaining = (total - complete) / rate if rate > 0 else float("inf")
    width = 40
    filled = int(width * complete / total) if total else 0
    eta = "--" if not rate else time.strftime("%H:%M:%S", time.gmtime(remaining))
    lines = [f"Gemini audio labels  [{'#' * filled}{'.' * (width - filled)}]  {complete:,}/{total:,} ({100 * complete / total:.1f}%)", f"Rate: {rate:.2f} clips/s  ETA: {eta}  Refresh: 1 s", "", "language  complete / target"]
    lines.extend(
        f"{language:8}  {completed[language]:>6,} / {totals[language]:<6,}"
        + ("  target reached" if completed[language] >= totals[language] else "")
        for language in sorted(totals)
    )
    return "\n".join(lines)


def parse_targets(raw_targets: list[str]) -> dict[str, int]:
    targets = {}
    for raw_target in raw_targets:
        language, separator, count = raw_target.partition("=")
        if not separator or not language or not count.isdigit() or int(count) < 1:
            raise SystemExit(f"Invalid target {raw_target!r}; use LANGUAGE=COUNT")
        targets[language] = int(count)
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="print one accurate snapshot and exit")
    parser.add_argument("--language", action="append", default=[], help="limit the display to one language; repeat for each language")
    parser.add_argument("--target", action="append", default=[], metavar="LANGUAGE=COUNT", help="override a source-row total with the requested label target; repeat as needed")
    args = parser.parse_args()
    source_totals = {path.stem: pq.ParquetFile(path).metadata.num_rows for path in sorted(PRIVATE.glob("*.parquet"))}
    if not source_totals:
        raise SystemExit("No private parquets found")
    unknown_languages = set(args.language) - source_totals.keys()
    if unknown_languages:
        raise SystemExit(f"Unknown language(s): {', '.join(sorted(unknown_languages))}")
    totals = {language: source_totals[language] for language in (args.language or source_totals)}
    targets = parse_targets(args.target)
    unknown_targets = targets.keys() - totals.keys()
    if unknown_targets:
        raise SystemExit(f"Target is outside the displayed languages: {', '.join(sorted(unknown_targets))}")
    totals.update(targets)
    started = time.monotonic()
    initial = None
    try:
        while True:
            completed = {language: successful_labels(PRIVATE / "labels" / f"{language}.audio.jsonl") for language in totals}
            if initial is None:
                initial = sum(min(completed[language], totals[language]) for language in totals)
            if not args.once:
                os.system("clear")
            print(render(completed, totals, initial, started), flush=True)
            if args.once:
                return
            time.sleep(1)
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
