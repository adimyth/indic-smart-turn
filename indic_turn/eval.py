"""Evaluate one or more smart-turn style ONNX models on parquet test data, per language
and per source dataset. Also measures single-sample CPU latency.

usage: python -m indic_turn.eval --models stock=path/a.onnx ours=path/b.onnx \
          --data data/built/*.parquet --split test --out reports/eval.md
"""
from __future__ import annotations
import argparse, glob, io, json, time
from collections import defaultdict
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
        rows.append({"wav": wav, "label": int(bool(r["endpoint_bool"])), "language": r["language"],
                     "dataset": f"{repo.split('/')[-1]}:{split}"})
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
            rows.append({"wav": wav, "label": int(bool(d["endpoint_bool"][i])), "language": d["language"][i],
                         "dataset": d.get("dataset", [None]*t.num_rows)[i] or p})
            if limit and len(rows) >= limit:
                return rows
    return rows

class Model:
    def __init__(self, name, path, threads=1):
        so = ort.SessionOptions(); so.intra_op_num_threads = threads; so.inter_op_num_threads = 1
        self.name, self.sess = name, ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        inp = self.sess.get_inputs()[0]
        self.input_name, self.shape = inp.name, inp.shape
        self.raw_audio = not (len(self.shape) == 3 and self.shape[1] == 80)
    def run(self, wavs):
        x = np.stack([last8(w) for w in wavs]).astype(np.float32) if self.raw_audio else features(wavs)
        out = self.sess.run(None, {self.input_name: x})[0]
        out = np.asarray(out, dtype=np.float64).reshape(len(wavs), -1)
        p = out[:, -1] if out.shape[1] > 1 else out[:, 0]
        if p.min() < 0 or p.max() > 1:  # logits -> prob
            p = 1 / (1 + np.exp(-p))
        return p
    def latency_ms(self, wav, n=30):
        for _ in range(5): self.run([wav])
        ts = []
        for _ in range(n):
            t = time.perf_counter(); self.run([wav]); ts.append((time.perf_counter() - t) * 1000)
        return float(np.median(ts))

def metrics(p, y):
    p, y = np.asarray(p), np.asarray(y)
    pred = (p > 0.5).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    auc = float(roc_auc_score(y, p)) if len(set(y.tolist())) > 1 else float("nan")
    return {"n": int(len(y)), "acc": (tp + tn) / max(len(y), 1), "auc": auc,
            "prec_inc": tn / max(tn + fn, 1), "rec_inc": tn / max(tn + fp, 1),   # 'incomplete' = the class that prevents interruptions
            "prec_comp": tp / max(tp + fp, 1), "rec_comp": tp / max(tp + fn, 1), "pos_rate": float(y.mean())}

def evaluate(models, rows, bs=64):
    res = {}
    for m in models:
        probs = []
        for i in range(0, len(rows), bs):
            probs.extend(m.run([r["wav"] for r in rows[i:i + bs]]).tolist())
        res[m.name] = probs
    return res

def report(models, rows, res, out_path, latency):
    groups = {"language": defaultdict(list), "dataset": defaultdict(list)}
    for i, r in enumerate(rows):
        groups["language"][r["language"]].append(i); groups["dataset"][r["dataset"]].append(i)
    y = [r["label"] for r in rows]
    L = ["# Evaluation report", "", f"rows: {len(rows)}; models: {', '.join(m.name for m in models)}", ""]
    L += ["| model | CPU latency (ms, 1 thread, batch 1) |", "|---|---|"] + [f"| {k} | {v:.1f} |" for k, v in latency.items()] + [""]
    summary = {}
    for gname, g in groups.items():
        L += [f"## By {gname}", "", "| " + gname + " | n | pos% | model | acc | AUC | prec(inc) | rec(inc) | rec(comp) |", "|---|---|---|---|---|---|---|---|---|"]
        for key in sorted(g):
            idx = g[key]
            for m in models:
                mt = metrics([res[m.name][i] for i in idx], [y[i] for i in idx])
                summary[(gname, key, m.name)] = mt
                label = LANG_NAMES.get(key, key) if gname == "language" else key
                L.append(f"| {label} | {mt['n']} | {100*mt['pos_rate']:.0f} | {m.name} | {100*mt['acc']:.1f} | {mt['auc']:.3f} | {100*mt['prec_inc']:.1f} | {100*mt['rec_inc']:.1f} | {100*mt['rec_comp']:.1f} |")
        L.append("")
    L += ["## Overall", "", "| model | acc | AUC |", "|---|---|---|"]
    for m in models:
        mt = metrics(res[m.name], y); L.append(f"| {m.name} | {100*mt['acc']:.1f} | {mt['auc']:.3f} |")
    txt = "\n".join(L)
    if out_path:
        from pathlib import Path
        Path(out_path).parent.mkdir(parents=True, exist_ok=True); Path(out_path).write_text(txt)
        Path(out_path).with_suffix(".json").write_text(json.dumps({"|".join(k): v for k, v in summary.items()}, indent=1))
    print(txt)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True, help="name=path.onnx")
    ap.add_argument("--data", nargs="*", default=[], help="parquet files/globs from indic_turn.build")
    ap.add_argument("--hf", nargs="*", default=[], help="HF datasets as repo:split[:lang,lang]")
    ap.add_argument("--split", default="test")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    paths = [p for pat in a.data for p in sorted(glob.glob(pat))]
    rows = load_rows(paths, a.split, a.limit)
    for spec in a.hf:
        rows += load_hf_rows(spec, a.limit)
    models = [Model(*m.split("=", 1)) for m in a.models]
    print(f"{len(rows)} rows from {len(paths)} files; evaluating {[m.name for m in models]}", flush=True)
    res = evaluate(models, rows)
    latency = {m.name: m.latency_ms(rows[0]["wav"]) for m in models}
    report(models, rows, res, a.out, latency)

if __name__ == "__main__":
    main()
