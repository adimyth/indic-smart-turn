"""Report primary text-label coverage and class balance without making API requests."""
from __future__ import annotations

import argparse
import json
from collections.abc import Iterable

from .common import DATA

LANGS = ("hin", "mar", "tam", "kan", "mal", "guj", "pan", "tel", "asm", "ori", "ben")


def label_stats(lang: str) -> tuple[int, int, int, int, int]:
    """Return (rows, complete_rows, long_rows, long_complete_rows, malformed_rows) for one primary label file."""
    path = DATA / "labels" / f"{lang}.jsonl"
    if not path.exists():
        return 0, 0, 0, 0, 0
    rows = complete = long_rows = long_complete = malformed = 0
    for line in path.open():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            endpoint = bool(row["endpoint_bool"])
            complete += endpoint
            if float(row.get("duration") or 0) >= 4.0:
                long_rows += 1
                long_complete += endpoint
            rows += 1
        except (json.JSONDecodeError, KeyError, TypeError):
            malformed += 1
    return rows, complete, long_rows, long_complete, malformed


def required_rows(lang: str) -> int:
    return 2_900 if lang == "tam" else 4_800


def report(langs: Iterable[str], strict: bool) -> bool:
    """Print the Stage 1 coverage table and return whether every gate passes."""
    passed = True
    print("| Language | Rows | Required | Complete rate | Complete rate (≥4 s) | Malformed | Status |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for lang in langs:
        rows, complete, long_rows, long_complete, malformed = label_stats(lang)
        rate = complete / rows if rows else 0.0
        long_rate = long_complete / long_rows if long_rows else 0.0
        ok = rows >= required_rows(lang) and 0.80 <= rate <= 0.92 and malformed == 0
        passed &= ok
        status = "pass" if ok else "needs attention"
        print(f"| {lang} | {rows:,} | {required_rows(lang):,} | {rate:.1%} | {long_rate:.1%} | {malformed:,} | {status} |")
    if strict and not passed:
        print("Stage 1 label checks failed.")
    return passed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--langs", nargs="+", default=list(LANGS))
    ap.add_argument("--strict", action="store_true", help="exit 1 unless all Stage 1 gates pass")
    args = ap.parse_args()
    passed = report(args.langs, strict=args.strict)
    if args.strict and not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
