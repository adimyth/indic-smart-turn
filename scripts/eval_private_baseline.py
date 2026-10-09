#!/usr/bin/env python3
"""Join local private call rows to Gemini verdicts and write the Stage 9 baseline report.

The script never uploads private data. It streams parquet batches, retains only probabilities and non-sensitive evaluation metadata, writes local category sidecars under data/private/categories, and writes a counts-and-metrics report.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import soundfile as sf
from dotenv import load_dotenv
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from indic_turn.common import LANG_NAMES, SR
from indic_turn.eval import Model, features
from scripts.extract_calls import load_calls

PRIVATE = ROOT / "data" / "private"
PUBLIC = ROOT / "data" / "built"
LABELS = PRIVATE / "labels"
DEFAULT_CATEGORIES = PRIVATE / "categories"
DEFAULT_REPORT = ROOT / "reports" / "private_baseline.md"
MODEL_SPECS = {
    "smartturn_v3.2": ROOT / "models" / "smart-turn-v3.2-cpu.onnx",
    "base_fp32": ROOT / "models" / "indic-base" / "indic-smart-turn-fp32.onnx",
    "base_int8_dynamic": ROOT / "models" / "indic-base" / "indic-smart-turn-int8-dynamic.onnx",
    "tiny_int8": ROOT / "models" / "indic-tiny" / "indic-smart-turn-int8.onnx",
}
CATEGORIES = ("A", "B", "C", "D", "unlabeled")
MODEL_CATEGORIES = {"A", "B", "C"}
PAUSE_BINS = (
    ("under 0.2 s", 0.0, 0.2),
    ("0.2–0.5 s", 0.2, 0.5),
    ("0.5–1.0 s", 0.5, 1.0),
    ("1.0 s and over", 1.0, float("inf")),
)
LATENCY_BINS = (
    ("under 2.0 s", 0.0, 2.0),
    ("2.0–3.5 s", 2.0, 3.5),
    ("3.5–5.0 s", 3.5, 5.000001),
)


@dataclass
class ScoredRow:
    language: str
    category: str
    pause_s: float
    gap_agent: float
    probabilities: dict[str, float] = field(default_factory=dict)


def read_verdicts(path: Path) -> dict[str, str]:
    """Read successful resumable Gemini verdicts without retaining prompt or audio content."""
    verdicts: dict[str, str] = {}
    if not path.exists():
        return verdicts
    with path.open() as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            verdict = row.get("verdict")
            key = row.get("key")
            if key and verdict in {"complete", "incomplete"}:
                verdicts[key] = verdict
    return verdicts


def key_of(columns: dict[str, list], index: int) -> str:
    audio = columns["audio"][index]["bytes"]
    digest = hashlib.md5(audio).hexdigest()[:10]
    return f"{columns['session'][index]}|{columns['chunk'][index]}|{columns['dataset'][index]}|{digest}"


def category_of(rule_label: str, verdict: str | None) -> str:
    if verdict is None:
        return "unlabeled"
    if rule_label == "complete" and verdict == "complete":
        return "A"
    if rule_label == "incomplete" and verdict == "incomplete":
        return "B"
    if rule_label == "incomplete" and verdict == "complete":
        return "C"
    if rule_label == "complete" and verdict == "incomplete":
        return "D"
    raise ValueError(f"Unexpected rule/Gemini label pair: {rule_label!r}/{verdict!r}")


def decode_wav(raw: bytes) -> np.ndarray:
    wav, sample_rate = sf.read(io.BytesIO(raw), dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sample_rate != SR:
        raise ValueError(f"Expected {SR} Hz audio, received {sample_rate} Hz")
    return np.asarray(wav, dtype=np.float32)


def flush_scores(pending: list[tuple[ScoredRow, bytes]], models: list[Model]) -> None:
    """Run all models on a bounded audio batch and immediately release the source bytes."""
    if not pending:
        return
    wavs = [decode_wav(raw) for _, raw in pending]
    shared_features = features(wavs) if any(not model.raw_audio for model in models) else None
    for model in models:
        probabilities = model.run(wavs, shared_features)
        for (record, _), probability in zip(pending, probabilities):
            record.probabilities[model.name] = float(probability)
    pending.clear()
    del wavs, shared_features


def open_category_writers(category_dir: Path, languages: list[str]) -> tuple[dict[str, object], dict[str, Path]]:
    category_dir.mkdir(parents=True, exist_ok=True)
    handles: dict[str, object] = {}
    temporary: dict[str, Path] = {}
    for language in languages:
        destination = category_dir / f"{language}.jsonl"
        temp = category_dir / f".{language}.categories.tmp.jsonl"
        temp.unlink(missing_ok=True)
        handles[language] = temp.open("w")
        temporary[language] = destination
    return handles, temporary


def close_category_writers(handles: dict[str, object], destinations: dict[str, Path], success: bool) -> None:
    for handle in handles.values():
        handle.close()
    for language, destination in destinations.items():
        temp = destination.with_name(f".{language}.categories.tmp.jsonl")
        if success:
            temp.replace(destination)
        else:
            temp.unlink(missing_ok=True)


def write_category(handle, key: str, split: str, category: str, rule_label: str, verdict: str | None, pause_s: float, gap_agent: float) -> None:
    """Persist only local join metadata required to select a future training split."""
    handle.write(json.dumps({"key": key, "split": split, "category": category, "rule_label": rule_label, "gemini_verdict": verdict, "pause_s": pause_s, "gap_agent": gap_agent}) + "\n")


def join_and_score(private_dir: Path, category_dir: Path, models: list[Model], batch_size: int) -> tuple[dict[str, dict[str, Counter]], list[ScoredRow]]:
    paths = sorted(private_dir.glob("*.parquet"))
    languages = [path.stem for path in paths]
    counts: dict[str, dict[str, Counter]] = {language: {"train": Counter(), "test": Counter()} for language in languages}
    scored: list[ScoredRow] = []
    pending: list[tuple[ScoredRow, bytes]] = []
    handles, destinations = open_category_writers(category_dir, languages)
    try:
        for path in paths:
            language = path.stem
            verdicts = read_verdicts(LABELS / f"{language}.audio.jsonl")
            for batch in pq.ParquetFile(path).iter_batches(batch_size=batch_size):
                columns = batch.to_pydict()
                for index in range(batch.num_rows):
                    split = columns["split"][index]
                    if split not in counts[language]:
                        continue
                    rule_label = columns["rule_label"][index]
                    key = key_of(columns, index)
                    verdict = verdicts.get(key)
                    category = category_of(rule_label, verdict)
                    pause_s = float(columns["pause_s"][index])
                    gap_agent = float(columns["gap_agent"][index])
                    counts[language][split][category] += 1
                    write_category(handles[language], key, split, category, rule_label, verdict, pause_s, gap_agent)
                    if split == "test" and category in MODEL_CATEGORIES:
                        record = ScoredRow(language, category, pause_s, gap_agent)
                        scored.append(record)
                        pending.append((record, columns["audio"][index]["bytes"]))
                        if len(pending) >= batch_size:
                            flush_scores(pending, models)
            print(f"joined {LANG_NAMES.get(language, language)}", flush=True)
        flush_scores(pending, models)
    except BaseException:
        close_category_writers(handles, destinations, success=False)
        raise
    close_category_writers(handles, destinations, success=True)
    return counts, scored


def public_rows(public_dir: Path, models: list[Model], batch_size: int) -> list[dict[str, object]]:
    """Score the final local public test parquets without downloading any external data."""
    rows: list[dict[str, object]] = []
    pending: list[tuple[dict[str, object], bytes]] = []

    def flush() -> None:
        if not pending:
            return
        wavs = [decode_wav(raw) for _, raw in pending]
        shared_features = features(wavs) if any(not model.raw_audio for model in models) else None
        for model in models:
            probabilities = model.run(wavs, shared_features)
            for (record, _), probability in zip(pending, probabilities):
                record[model.name] = float(probability)
        pending.clear()
        del wavs, shared_features

    for path in sorted(public_dir.glob("*.parquet")):
        for batch in pq.ParquetFile(path).iter_batches(batch_size=batch_size):
            columns = batch.to_pydict()
            for index, split in enumerate(columns["split"]):
                if split != "test":
                    continue
                record: dict[str, object] = {"language": columns["language"][index], "label": int(bool(columns["endpoint_bool"][index]))}
                rows.append(record)
                pending.append((record, columns["audio"][index]["bytes"]))
                if len(pending) >= batch_size:
                    flush()
        print(f"scored public {path.stem}", flush=True)
    flush()
    return rows


def ci_rate(values: list[bool], seed_text: str, resamples: int) -> tuple[int, float, tuple[float, float]]:
    count = len(values)
    if not count:
        return 0, float("nan"), (float("nan"), float("nan"))
    rate = float(np.mean(values))
    if not resamples:
        return count, rate, (float("nan"), float("nan"))
    seed = int.from_bytes(hashlib.sha1(seed_text.encode()).digest()[:8], "little")
    rng = np.random.default_rng(seed)
    samples = rng.binomial(count, rate, size=resamples) / count
    return count, rate, (float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975)))


def fmt_rate(rate: float, interval: tuple[float, float] | None = None) -> str:
    if not np.isfinite(rate):
        return "n/a"
    if interval is None or not all(np.isfinite(interval)):
        return f"{100 * rate:.1f}%"
    return f"{100 * rate:.1f}% [{100 * interval[0]:.1f}, {100 * interval[1]:.1f}]"


def category_outcomes(rows: list[ScoredRow], language: str | None, category: str, model: str, threshold: float, minimum_pause: float = 0.0, pause_bin: tuple[float, float] | None = None) -> list[bool]:
    outcomes: list[bool] = []
    for row in rows:
        if language is not None and row.language != language:
            continue
        if row.category != category or row.pause_s < minimum_pause:
            continue
        if pause_bin is not None and not (pause_bin[0] <= row.pause_s < pause_bin[1]):
            continue
        predicted_complete = row.probabilities[model] > threshold
        outcomes.append(predicted_complete if category in {"A", "C"} else not predicted_complete)
    return outcomes


def metric_label(category: str) -> str:
    return {"A": "A recall", "B": "B specificity", "C": "C interrupt rate"}[category]


def private_metric_table(rows: list[ScoredRow], models: list[Model], resamples: int) -> list[str]:
    lines = ["## Private test metrics at threshold 0.5", "", "Category A recall is the rate of answering on clear turn ends. Category B specificity is the rate of staying quiet on jointly unfinished pauses. Category C interrupt rate is the rate of answering on sentence-final pauses where the trainee resumed.", "", "| language | category | n | model | metric (95% CI) |", "|---|---|---:|---|---|"]
    for language in sorted({row.language for row in rows}):
        for category in ("A", "B", "C"):
            for model in models:
                outcomes = category_outcomes(rows, language, category, model.name, 0.5)
                count, rate, interval = ci_rate(outcomes, f"private|{language}|{category}|{model.name}|0.5", resamples)
                lines.append(f"| {LANG_NAMES.get(language, language)} | {category} | {count} | {model.name} | {metric_label(category)}: {fmt_rate(rate, interval)} |")
    lines.append("")
    return lines


def pause_metric_table(rows: list[ScoredRow], models: list[Model], resamples: int) -> list[str]:
    lines = ["## Metrics by pause length", "", "| language | pause length | category | n | model | metric (95% CI) |", "|---|---|---|---:|---|---|"]
    for language in sorted({row.language for row in rows}):
        for bin_name, lower, upper in PAUSE_BINS:
            for category in ("A", "B", "C"):
                for model in models:
                    outcomes = category_outcomes(rows, language, category, model.name, 0.5, pause_bin=(lower, upper))
                    count, rate, interval = ci_rate(outcomes, f"pause|{language}|{bin_name}|{category}|{model.name}", resamples)
                    lines.append(f"| {LANG_NAMES.get(language, language)} | {bin_name} | {category} | {count} | {model.name} | {metric_label(category)}: {fmt_rate(rate, interval)} |")
    lines.append("")
    return lines


def policy_sweep_table(rows: list[ScoredRow], models: list[Model]) -> list[str]:
    lines = ["## Deployment policy sweep", "", "Each row applies both the minimum-pause gate and model threshold. It reports the desired A recall and the C interruption trade-off; category B is not part of this policy trade-off table.", "", "| language | minimum pause | threshold | A n | C n | model | A recall | C interrupt rate |", "|---|---:|---:|---:|---:|---|---:|---:|"]
    languages: list[str | None] = [None] + sorted({row.language for row in rows})
    for language in languages:
        label = "Overall" if language is None else LANG_NAMES.get(language, language)
        for minimum_pause in (0.2, 0.5, 1.0):
            for threshold in (0.5, 0.7, 0.9):
                for model in models:
                    a_values = category_outcomes(rows, language, "A", model.name, threshold, minimum_pause)
                    c_values = category_outcomes(rows, language, "C", model.name, threshold, minimum_pause)
                    _, a_rate, _ = ci_rate(a_values, f"sweep|{label}|A|{minimum_pause}|{threshold}|{model.name}", 0)
                    _, c_rate, _ = ci_rate(c_values, f"sweep|{label}|C|{minimum_pause}|{threshold}|{model.name}", 0)
                    lines.append(f"| {label} | {minimum_pause:.1f} s | {threshold:.1f} | {len(a_values)} | {len(c_values)} | {model.name} | {fmt_rate(a_rate)} | {fmt_rate(c_rate)} |")
    lines.append("")
    return lines


def agent_interruption_table(counts: dict[str, dict[str, Counter]], category_dir: Path, resamples: int) -> list[str]:
    lines = ["## Agent-interruption finding by agent latency", "", "The denominator is Gemini-labeled rule-complete test rows (A + D), so this is a finding about the fixed TTS agent rather than model performance. D is Gemini incomplete despite the recording rule marking a complete turn, and is excluded from model scoring.", "", "| language | agent latency | A + D replies | D replies | D share (95% CI) |", "|---|---|---:|---:|---|"]
    records_by_language: dict[str, list[dict[str, object]]] = defaultdict(list)
    for language in sorted(counts):
        category_path = category_dir / f"{language}.jsonl"
        with category_path.open() as handle:
            for line in handle:
                row = json.loads(line)
                if row["split"] == "test" and row["category"] in {"A", "D"}:
                    records_by_language[language].append(row)
    for language in ["overall"] + sorted(records_by_language):
        source = [record for values in records_by_language.values() for record in values] if language == "overall" else records_by_language[language]
        display = "Overall" if language == "overall" else LANG_NAMES.get(language, language)
        for bin_name, lower, upper in LATENCY_BINS:
            selected = [record for record in source if np.isfinite(record["gap_agent"]) and lower <= record["gap_agent"] < upper]
            outcomes = [record["category"] == "D" for record in selected]
            count, rate, interval = ci_rate(outcomes, f"agent|{language}|{bin_name}", resamples)
            lines.append(f"| {display} | {bin_name} | {count} | {sum(outcomes)} | {fmt_rate(rate, interval)} |")
    lines.append("")
    return lines


def public_metrics(rows: list[dict[str, object]], model_name: str) -> dict[str, float | int]:
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int8)
    probabilities = np.asarray([float(row[model_name]) for row in rows], dtype=np.float64)
    prediction = probabilities > 0.5
    positives = labels == 1
    negatives = ~positives
    return {
        "n": len(rows),
        "accuracy": float(np.mean(prediction == positives)),
        "auc": float(roc_auc_score(labels, probabilities)) if positives.any() and negatives.any() else float("nan"),
        "recall_incomplete": float(np.mean(~prediction[negatives])) if negatives.any() else float("nan"),
        "recall_complete": float(np.mean(prediction[positives])) if positives.any() else float("nan"),
    }


def public_table(rows: list[dict[str, object]], models: list[Model]) -> list[str]:
    lines = ["## Public-test reference", "", "These are a fresh local scoring pass over `data/built/*.parquet`, split `test`, using the same model files and fixed 0.5 threshold. They are included only as a public-domain reference and were not used to choose a private-data policy.", "", "| public language | n | model | accuracy | AUC | recall incomplete | recall complete |", "|---|---:|---|---:|---:|---:|---:|"]
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["language"])].append(row)
    for language in sorted(grouped):
        for model in models:
            result = public_metrics(grouped[language], model.name)
            auc = "n/a" if not np.isfinite(result["auc"]) else f"{result['auc']:.3f}"
            lines.append(f"| {LANG_NAMES.get(language, language)} | {result['n']:,} | {model.name} | {100 * result['accuracy']:.1f}% | {auc} | {100 * result['recall_incomplete']:.1f}% | {100 * result['recall_complete']:.1f}% |")
    lines.append("")
    return lines


def extraction_summary(private_dir: Path) -> dict[str, dict[str, int | float]]:
    """Recover local session totals without emitting source names, URLs, or call identifiers."""
    load_dotenv(ROOT / ".env")
    salt = os.environ.get("PRIVATE_CALL_SALT")
    if not salt:
        raise SystemExit("PRIVATE_CALL_SALT is required to calculate the local quarantine rate")
    calls = load_calls(private_dir / "additional-data.csv", salt, None, 0)
    by_language: dict[str, list] = defaultdict(list)
    for call in calls:
        by_language[call.language].append(call)
    summary: dict[str, dict[str, int | float]] = {}
    for language, language_calls in by_language.items():
        decoded = sum((private_dir / "raw" / f"{call.call_id}.wav").is_file() for call in language_calls)
        used = len(set(pq.read_table(private_dir / f"{language}.parquet", columns=["call_id"]).column("call_id").to_pylist()))
        quarantined = decoded - used
        failed = len(language_calls) - decoded
        summary[language] = {"source": len(language_calls), "decoded": decoded, "used": used, "quarantined": quarantined, "failed": failed, "quarantine_rate": quarantined / len(language_calls)}
    return summary


def data_tables(counts: dict[str, dict[str, Counter]], extraction: dict[str, dict[str, int | float]]) -> list[str]:
    lines = ["## Data coverage and category join", "", "For Kannada, Malayalam, Marathi, Tamil, and Telugu, the Gemini-labeled test rows are the earliest sessions in file order, not a random sample. Bengali, English, Gujarati, Hindi, and Odia test rows are fully Gemini-labeled. Category A is rule complete/Gemini complete; B is rule incomplete/Gemini incomplete; C is rule incomplete/Gemini complete; D is rule complete/Gemini incomplete; unlabeled has no successful Gemini verdict. Test evaluation uses A, B, and C; D is reporting-only; unlabeled is excluded from test evaluation. Training retains only A and B, dropping C, D, and unlabeled rows.", "", "| language | source sessions | used | quarantined | failed | quarantine rate | test rows | Gemini-labeled | model-scored A+B+C | D, reporting only | unlabeled |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for language in sorted(counts):
        test = counts[language]["test"]
        detail = extraction[language]
        labeled = sum(test[category] for category in ("A", "B", "C", "D"))
        scored = sum(test[category] for category in ("A", "B", "C"))
        total = labeled + test["unlabeled"]
        lines.append(f"| {LANG_NAMES.get(language, language)} | {detail['source']} | {detail['used']} | {detail['quarantined']} | {detail['failed']} | {100 * detail['quarantine_rate']:.1f}% | {total:,} | {labeled:,} | {scored:,} | {test['D']:,} | {test['unlabeled']:,} |")
    lines += ["", "| language | test A, share | test B, share | test C, share | test D, share | test unlabeled, share | train A retained | train B retained | train C dropped | train D dropped | train unlabeled dropped |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for language in sorted(counts):
        train, test = counts[language]["train"], counts[language]["test"]
        total = sum(test[category] for category in CATEGORIES)
        def category_share(category: str) -> str:
            return f"{test[category]:,} ({100 * test[category] / total:.1f}%)" if total else "0 (n/a)"
        lines.append(f"| {LANG_NAMES.get(language, language)} | {category_share('A')} | {category_share('B')} | {category_share('C')} | {category_share('D')} | {category_share('unlabeled')} | {train['A']:,} | {train['B']:,} | {train['C']:,} | {train['D']:,} | {train['unlabeled']:,} |")
    lines += ["", "Odia is indicative only: 2 sessions, 95 test clips. Kannada is low-count. Sessions that failed the pre-registered speaker checks are quarantined, and the roleplay/TTS setting may not represent real customer-call rhythm.", ""]
    return lines


def write_report(path: Path, category_dir: Path, counts: dict[str, dict[str, Counter]], extraction: dict[str, dict[str, int | float]], private_rows: list[ScoredRow], public_test: list[dict[str, object]], models: list[Model], resamples: int) -> None:
    lines = ["# Private production-call baseline", "", "This report contains counts and model metrics only. Private audio, source paths, call identifiers, transcripts, and clips remain local under `data/private/`.", ""]
    lines += data_tables(counts, extraction)
    lines += private_metric_table(private_rows, models, resamples)
    lines += pause_metric_table(private_rows, models, resamples)
    lines += policy_sweep_table(private_rows, models)
    lines += agent_interruption_table(counts, category_dir, resamples)
    lines += public_table(public_test, models)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, default=PRIVATE)
    parser.add_argument("--public", type=Path, default=PUBLIC)
    parser.add_argument("--categories", type=Path, default=DEFAULT_CATEGORIES)
    parser.add_argument("--out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--bootstrap-resamples", type=int, default=1000)
    args = parser.parse_args()
    if args.batch_size < 1 or args.threads < 1 or args.bootstrap_resamples < 0:
        raise SystemExit("--batch-size and --threads must be positive, and --bootstrap-resamples cannot be negative")
    missing_models = [str(path) for path in MODEL_SPECS.values() if not path.is_file()]
    if missing_models:
        raise SystemExit("Missing model file(s): " + ", ".join(missing_models))
    models = [Model(name, str(path), threads=args.threads) for name, path in MODEL_SPECS.items()]
    counts, private_test = join_and_score(args.private, args.categories, models, args.batch_size)
    print(f"scored {len(private_test):,} private A/B/C test rows", flush=True)
    public_test = public_rows(args.public, models, args.batch_size)
    print(f"scored {len(public_test):,} public test rows", flush=True)
    extraction = extraction_summary(args.private)
    write_report(args.out, args.categories, counts, extraction, private_test, public_test, models, args.bootstrap_resamples)
    print(f"wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
