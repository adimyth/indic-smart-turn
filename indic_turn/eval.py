"""Evaluate one or more smart-turn style ONNX models on endpointing datasets.

Reports per-language and per-dataset metrics, 95% bootstrap confidence intervals, dev-split threshold sweeps, error clips, and single-sample CPU latency.

usage: python -m indic_turn.eval --models stock=path/a.onnx ours=path/b.onnx \
          --data data/built/*.parquet --split test --out reports/eval.md
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import time
from collections import defaultdict
from pathlib import Path
import numpy as np, pyarrow.parquet as pq, soundfile as sf
import onnxruntime as ort
from sklearn.metrics import roc_auc_score
from transformers import WhisperFeatureExtractor
from .common import LANG_NAMES, SR

FE = WhisperFeatureExtractor(chunk_length=8)

def last8(x):
    n = 8 * SR
    return x[-n:] if len(x) > n else np.pad(x, (n - len(x), 0))

def features(batch_wavs):
    f = FE([last8(w) for w in batch_wavs], sampling_rate=SR, return_tensors="np", padding="max_length",
           max_length=8 * SR, truncation=True, do_normalize=True)
    return f.input_features.astype(np.float32)

def load_hf_rows(spec, limit=0):
    """spec = 'repo:split[:lang1,lang2]' -> rows (audio bytes decoded with soundfile)."""
    from datasets import load_dataset, Audio
    parts = spec.split(":"); repo, split = parts[0], parts[1]
    langs = set(parts[2].split(",")) if len(parts) > 2 else None
    ds = load_dataset(repo)[split].cast_column("audio", Audio(decode=False))
    if langs:
        ds = ds.filter(lambda r: r["language"] in langs, num_proc=4)
    rows = []
    for r in ds:
        wav, sr = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32")
        if wav.ndim > 1: wav = wav.mean(1)
        if sr != SR:
            import librosa; wav = librosa.resample(wav, orig_sr=sr, target_sr=SR)
        rows.append({
            "wav": wav,
            "label": int(bool(r["endpoint_bool"])),
            "language": r["language"],
            "dataset": f"{repo.split('/')[-1]}:{split}",
            "transcript": r.get("spoken_text") or r.get("text") or r.get("transcript") or "",
            "sample_id": str(r.get("id") or r.get("session") or len(rows)),
        })
        if limit and len(rows) >= limit: break
    return rows

def load_rows(paths, split, limit=0):
    rows = []
    for p in paths:
        t = pq.read_table(p)
        d = t.to_pydict()
        for i in range(t.num_rows):
            if split and "split" in d and d["split"][i] != split:
                continue
            a = d["audio"][i]
            wav, sr = sf.read(io.BytesIO(a["bytes"]), dtype="float32")
            if wav.ndim > 1: wav = wav.mean(1)
            assert sr == SR, sr
            def value(name, default):
                column = d.get(name)
                return column[i] if column is not None else default
            rows.append({
                "wav": wav,
                "label": int(bool(d["endpoint_bool"][i])),
                "language": d["language"][i],
                "dataset": value("dataset", None) or p,
                "transcript": value("spoken_text", "") or "",
                "sample_id": f"{value('session', '')}_{value('chunk', i)}",
            })
            if limit and len(rows) >= limit:
                return rows
    return rows

class Model:
    def __init__(self, name, path, threads=None):
        threads = threads or int(os.environ.get("EVAL_THREADS", "16"))
        so = ort.SessionOptions(); so.intra_op_num_threads = threads; so.inter_op_num_threads = 1
        self.name, self.path = name, path
        self.sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        inp = self.sess.get_inputs()[0]
        self.input_name, self.shape = inp.name, inp.shape
        self.raw_audio = not (len(self.shape) == 3 and self.shape[1] == 80)
    def run(self, wavs, feats=None):
        if self.raw_audio:
            x = np.stack([last8(w) for w in wavs]).astype(np.float32)
        else:
            x = feats if feats is not None else features(wavs)
        out = self.sess.run(None, {self.input_name: x})[0]
        out = np.asarray(out, dtype=np.float64).reshape(len(wavs), -1)
        p = out[:, -1] if out.shape[1] > 1 else out[:, 0]
        if p.min() < 0 or p.max() > 1:  # logits -> prob
            p = 1 / (1 + np.exp(-p))
        return p
    def latency_ms(self, wav, n=30):
        """Single-sample latency on a separate 1-thread session (the production setting)."""
        m1 = Model(self.name, self.path, threads=1)
        for _ in range(5): m1.run([wav])
        ts = []
        for _ in range(n):
            t = time.perf_counter(); m1.run([wav]); ts.append((time.perf_counter() - t) * 1000)
        return float(np.median(ts))

def metrics(p, y, threshold=0.5):
    p, y = np.asarray(p), np.asarray(y)
    pred = (p > threshold).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    auc = float(roc_auc_score(y, p)) if len(set(y.tolist())) > 1 else float("nan")
    return {"n": int(len(y)), "acc": (tp + tn) / max(len(y), 1), "auc": auc,
            "prec_inc": tn / max(tn + fn, 1), "rec_inc": tn / max(tn + fp, 1),   # 'incomplete' = the class that prevents interruptions
            "prec_comp": tp / max(tp + fp, 1), "rec_comp": tp / max(tp + fn, 1), "pos_rate": float(y.mean())}


def balanced_accuracy(p, y, threshold):
    p, y = np.asarray(p), np.asarray(y)
    pred = (p > threshold).astype(int)
    pos = y == 1
    neg = ~pos
    if not pos.any() or not neg.any():
        return float("nan")
    return float(((pred[pos] == 1).mean() + (pred[neg] == 0).mean()) / 2)


def _weighted_auc(prob, labels, counts, order, group_starts):
    pos = counts * labels
    neg = counts * (1 - labels)
    total_pos, total_neg = pos.sum(), neg.sum()
    if not total_pos or not total_neg:
        return float("nan")
    pos_groups = np.add.reduceat(pos[order], group_starts)
    neg_groups = np.add.reduceat(neg[order], group_starts)
    neg_before = np.cumsum(neg_groups) - neg_groups
    return float((pos_groups * (neg_before + 0.5 * neg_groups)).sum() / (total_pos * total_neg))


def bootstrap_ci(prob, labels, resamples, seed):
    """Return 95% percentile bootstrap intervals for accuracy and AUC at threshold 0.5."""
    prob = np.asarray(prob, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    if not resamples or not len(labels):
        return {"acc": [float("nan"), float("nan")], "auc": [float("nan"), float("nan")]}
    rng = np.random.default_rng(seed)
    correct = ((prob > 0.5).astype(np.int64) == labels).astype(np.int64)
    order = np.argsort(prob, kind="stable")
    sorted_prob = prob[order]
    group_starts = np.r_[0, np.flatnonzero(np.diff(sorted_prob)) + 1]
    acc_samples, auc_samples = [], []
    n = len(labels)
    for _ in range(resamples):
        counts = np.bincount(rng.integers(0, n, size=n), minlength=n)
        acc_samples.append(float((counts * correct).sum() / n))
        auc_samples.append(_weighted_auc(prob, labels, counts, order, group_starts))
    def interval(values):
        values = np.asarray(values, dtype=np.float64)
        values = values[np.isfinite(values)]
        if not len(values):
            return [float("nan"), float("nan")]
        return [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]
    return {"acc": interval(acc_samples), "auc": interval(auc_samples)}


def threshold_sweep(prob, labels):
    """Select the dev threshold that maximizes balanced accuracy, preferring 0.5 on ties."""
    thresholds = np.round(np.arange(0.05, 0.951, 0.01), 2)
    scores = [(threshold, balanced_accuracy(prob, labels, threshold)) for threshold in thresholds]
    best_threshold, best_score = max(scores, key=lambda item: (item[1], -abs(item[0] - 0.5)))
    return {
        "threshold": float(best_threshold),
        "balanced_accuracy": float(best_score),
        "balanced_accuracy_at_0_5": balanced_accuracy(prob, labels, 0.5),
    }

def evaluate(models, rows, bs=64):
    """Log-mel features are computed once per batch and shared across all mel-input models."""
    from tqdm import tqdm
    res = {m.name: [] for m in models}
    bar = tqdm(total=len(rows), unit="clip", desc=f"scoring {len(models)} models", dynamic_ncols=True, mininterval=5)
    for i in range(0, len(rows), bs):
        wavs = [r["wav"] for r in rows[i:i + bs]]
        feats = features(wavs) if any(not m.raw_audio for m in models) else None
        for m in models:
            res[m.name].extend(m.run(wavs, feats).tolist())
        bar.update(len(wavs))
    bar.close()
    return res

def _format_ci(value, interval, percent=False):
    scale = 100 if percent else 1
    if not np.isfinite(value):
        return "n/a"
    if not interval or not all(np.isfinite(interval)):
        return f"{scale * value:.1f}" if percent else f"{value:.3f}"
    if percent:
        return f"{scale * value:.1f} [{scale * interval[0]:.1f}, {scale * interval[1]:.1f}]"
    return f"{value:.3f} [{interval[0]:.3f}, {interval[1]:.3f}]"


def _groups(rows):
    groups = {"language": defaultdict(list), "dataset": defaultdict(list)}
    for i, row in enumerate(rows):
        groups["language"][row["language"]].append(i)
        groups["dataset"][row["dataset"]].append(i)
    return groups


def _section_report(models, rows, res, title, bootstrap_resamples, bootstrap_seed):
    groups = _groups(rows)
    labels = [row["label"] for row in rows]
    lines = [f"## {title}", "", f"rows: {len(rows)}", ""]
    summary = {}
    for group_name, group in groups.items():
        lines += [f"### By {group_name}", "", "| " + group_name + " | n | pos% | model | acc 95% CI | AUC 95% CI | prec(inc) | rec(inc) | rec(comp) |", "|---|---:|---:|---|---|---|---:|---:|---:|"]
        for key in sorted(group):
            index = group[key]
            truth = [labels[i] for i in index]
            display_key = LANG_NAMES.get(key, key) if group_name == "language" else key
            for model_index, model in enumerate(models):
                probability = [res[model.name][i] for i in index]
                result = metrics(probability, truth)
                result["ci"] = bootstrap_ci(probability, truth, bootstrap_resamples, bootstrap_seed + model_index * 1009 + len(index))
                summary[group_name, key, model.name] = result
                lines.append(
                    f"| {display_key} | {result['n']} | {100 * result['pos_rate']:.0f} | {model.name} | "
                    f"{_format_ci(result['acc'], result['ci']['acc'], percent=True)} | "
                    f"{_format_ci(result['auc'], result['ci']['auc'])} | {100 * result['prec_inc']:.1f} | "
                    f"{100 * result['rec_inc']:.1f} | {100 * result['rec_comp']:.1f} |"
                )
        lines.append("")
    lines += ["### Overall", "", "| model | acc | AUC |", "|---|---:|---:|"]
    overall = {}
    for model in models:
        result = metrics(res[model.name], labels)
        overall[model.name] = result
        lines.append(f"| {model.name} | {100 * result['acc']:.1f} | {result['auc']:.3f} |")
    lines.append("")
    return lines, {"groups": {"|".join(key): value for key, value in summary.items()}, "overall": overall}


def _threshold_report(models, rows, res):
    groups = _groups(rows)["language"]
    labels = [row["label"] for row in rows]
    lines = ["## Dev threshold sweep", "", "Thresholds maximize per-language balanced accuracy on dev data; test metrics above remain at the fixed 0.5 threshold.", "", "| language | n | model | best threshold | balanced acc | balanced acc @ 0.5 |", "|---|---:|---|---:|---:|---:|"]
    summary = {}
    for language in sorted(groups):
        index = groups[language]
        truth = [labels[i] for i in index]
        for model in models:
            result = threshold_sweep([res[model.name][i] for i in index], truth)
            summary[language, model.name] = result
            lines.append(f"| {LANG_NAMES.get(language, language)} | {len(index)} | {model.name} | {result['threshold']:.2f} | {100 * result['balanced_accuracy']:.1f} | {100 * result['balanced_accuracy_at_0_5']:.1f} |")
    lines.append("")
    return lines, {"|".join(key): value for key, value in summary.items()}


def dump_errors(rows, probability, model_name, count, out_path):
    """Write the highest-confidence fixed-threshold errors per language as WAV and transcript sidecars."""
    if not count:
        return {}
    root = Path(out_path)
    root.mkdir(parents=True, exist_ok=True)
    per_language = defaultdict(list)
    for index, (row, prob) in enumerate(zip(rows, probability)):
        prediction = int(prob > 0.5)
        if prediction != row["label"]:
            per_language[row["language"]].append((abs(float(prob) - 0.5), index, float(prob), prediction))
    summary = {}
    for language, errors in sorted(per_language.items()):
        language_dir = root / language
        language_dir.mkdir(parents=True, exist_ok=True)
        selected = sorted(errors, reverse=True)[:count]
        records = []
        for rank, (_, index, prob, prediction) in enumerate(selected, start=1):
            row = rows[index]
            stem = f"{rank:02d}_{row['sample_id'] or index}_p{prob:.4f}".replace("/", "_")
            wav_path = language_dir / f"{stem}.wav"
            txt_path = language_dir / f"{stem}.txt"
            sf.write(wav_path, row["wav"], SR, subtype="PCM_16")
            txt_path.write_text(
                f"model: {model_name}\nprobability_complete: {prob:.6f}\nlabel_complete: {row['label']}\nprediction_complete: {prediction}\ndataset: {row['dataset']}\ntranscript: {row['transcript']}\n"
            )
            records.append({"wav": str(wav_path), "transcript": str(txt_path), "probability": prob, "label": row["label"], "prediction": prediction, "dataset": row["dataset"]})
        summary[language] = records
    return summary


def json_safe(value):
    """Convert numpy values and non-finite metrics to portable JSON values."""
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def report(models, rows, res, out_path, latency, bootstrap_resamples, bootstrap_seed, ambiguous_rows=None, ambiguous_res=None, dev_rows=None, dev_res=None, dump_error_count=0, error_model="", error_dir=""):
    lines = ["# Evaluation report", "", f"Models: {', '.join(model.name for model in models)}", "", "## CPU latency", "", "| model | latency (ms, 1 thread, batch 1) |", "|---|---:|"]
    lines += [f"| {name} | {value:.1f} |" for name, value in latency.items()] + [""]
    clean_lines, clean_summary = _section_report(models, rows, res, "Clean test split", bootstrap_resamples, bootstrap_seed)
    lines += clean_lines
    summary = {"latency_ms": latency, "clean_test": clean_summary}
    if ambiguous_rows is not None:
        ambiguous_lines, ambiguous_summary = _section_report(models, ambiguous_rows, ambiguous_res, "Ambiguous test split", bootstrap_resamples, bootstrap_seed + 100_000)
        lines += ambiguous_lines
        summary["ambiguous_test"] = ambiguous_summary
    if dev_rows is not None:
        threshold_lines, threshold_summary = _threshold_report(models, dev_rows, dev_res)
        lines += threshold_lines
        summary["dev_thresholds"] = threshold_summary
    if dump_error_count:
        selected_model = error_model or models[-1].name
        if selected_model not in res:
            raise SystemExit(f"--error-model {selected_model!r} is not in --models")
        if error_dir:
            target_dir = error_dir
        elif out_path:
            run_name = Path(out_path).stem.removeprefix("eval_")
            target_dir = str(Path(out_path).parent / "errors" / run_name)
        else:
            target_dir = "reports/errors/eval"
        summary["error_dumps"] = dump_errors(rows, res[selected_model], selected_model, dump_error_count, target_dir)
        lines += ["## Error clips", "", f"Wrote up to {dump_error_count} highest-confidence errors per language for `{selected_model}` to `{target_dir}`.", ""]
    text = "\n".join(lines)
    if out_path:
        output = Path(out_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text)
        output.with_suffix(".json").write_text(json.dumps(json_safe(summary), indent=1, allow_nan=False))
    print(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True, help="name=path.onnx")
    ap.add_argument("--data", nargs="*", default=[], help="parquet files/globs from indic_turn.build")
    ap.add_argument("--hf", nargs="*", default=[], help="HF datasets as repo:split[:lang,lang]")
    ap.add_argument("--split", default="test")
    ap.add_argument("--ambiguous-split", default="", help="Optional local split to report separately, without HF rows")
    ap.add_argument("--dev-data", nargs="*", default=[], help="Parquet files/globs used for the dev threshold sweep")
    ap.add_argument("--dev-split", default="dev")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--bootstrap-resamples", type=int, default=1000)
    ap.add_argument("--bootstrap-seed", type=int, default=42)
    ap.add_argument("--dump-errors", type=int, default=0, metavar="N")
    ap.add_argument("--error-model", default="", help="Model name used for --dump-errors; defaults to the last model")
    ap.add_argument("--error-dir", default="", help="Directory for error WAVs and transcript sidecars")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    paths = [p for pat in a.data for p in sorted(glob.glob(pat))]
    rows = load_rows(paths, a.split, a.limit)
    for spec in a.hf:
        rows += load_hf_rows(spec, a.limit)
    if not rows:
        raise SystemExit("No evaluation rows found")
    ambiguous_rows = None
    if a.ambiguous_split:
        ambiguous_rows = load_rows(paths, a.ambiguous_split, a.limit)
        if not ambiguous_rows:
            print(f"No rows found for ambiguous split {a.ambiguous_split!r}; omitting that report section", flush=True)
            ambiguous_rows = None
    dev_rows = None
    if a.dev_data:
        dev_paths = [p for pat in a.dev_data for p in sorted(glob.glob(pat))]
        dev_rows = load_rows(dev_paths, a.dev_split, a.limit)
        if not dev_rows:
            print(f"No rows found for dev split {a.dev_split!r}; omitting threshold sweep", flush=True)
            dev_rows = None
    models = [Model(*m.split("=", 1)) for m in a.models]
    print(f"{len(rows)} rows from {len(paths)} files; evaluating {[m.name for m in models]}", flush=True)
    res = evaluate(models, rows, a.batch_size)
    latency = {m.name: m.latency_ms(rows[0]["wav"]) for m in models}
    ambiguous_res = evaluate(models, ambiguous_rows, a.batch_size) if ambiguous_rows is not None else None
    dev_res = evaluate(models, dev_rows, a.batch_size) if dev_rows is not None else None
    report(
        models,
        rows,
        res,
        a.out,
        latency,
        a.bootstrap_resamples,
        a.bootstrap_seed,
        ambiguous_rows,
        ambiguous_res,
        dev_rows,
        dev_res,
        a.dump_errors,
        a.error_model,
        a.error_dir,
    )

if __name__ == "__main__":
    main()
