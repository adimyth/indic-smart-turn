#!/usr/bin/env python3
"""Head-to-head on the production test clips, like the IndicVoices evaluation: per language, accuracy / AUC / per-class recall
for Smart Turn v3.2 and the Indic Smart Turn models, with (a) Gemini's audio verdict as the label and (b) the recording rule as the label."""
import json, hashlib, io, glob, os, csv, numpy as np, pyarrow.parquet as pq, soundfile as sf
from sklearn.metrics import roc_auc_score
from indic_turn.eval import Model
MODELS = [("Smart Turn v3.2 int8", "models/smart-turn-v3.2-cpu.onnx"), ("Indic base fp32", "models/indic-base/indic-smart-turn-fp32.onnx"),
          ("Indic base int8", "models/indic-base/indic-smart-turn-int8-dynamic.onnx"), ("Indic tiny int8", "models/indic-tiny/indic-smart-turn-int8.onnx")]
NAMES = {"ben":"Bengali","eng":"English","guj":"Gujarati","hin":"Hindi","kan":"Kannada","mal":"Malayalam","mar":"Marathi","ori":"Odia","tam":"Tamil","tel":"Telugu"}
models = [Model(n, p, threads=8) for n, p in MODELS]
out_rows = []
for p in sorted(glob.glob("data/private/*.parquet")):
    lang = os.path.basename(p)[:3]
    lab = {r["key"]: r["verdict"] for r in map(json.loads, open(f"data/private/labels/{lang}.audio.jsonl")) if r.get("verdict") in ("complete", "incomplete")}
    pf = pq.ParquetFile(p); wavs, gem, rule = [], [], []
    for g in range(pf.metadata.num_row_groups):
        d = pf.read_row_group(g, columns=["audio", "session", "chunk", "dataset", "endpoint_bool", "split"]).to_pydict()
        for i in range(len(d["session"])):
            if d["split"][i] != "test": continue
            key = f"{d['session'][i]}|{d['chunk'][i]}|{d['dataset'][i]}|{hashlib.md5(d['audio'][i]['bytes']).hexdigest()[:10]}"
            if key not in lab: continue
            wavs.append(sf.read(io.BytesIO(d["audio"][i]["bytes"]), dtype="float32")[0]); gem.append(int(lab[key] == "complete")); rule.append(int(bool(d["endpoint_bool"][i])))
    gem, rule = np.array(gem), np.array(rule)
    for m in models:
        pr = np.concatenate([m.run(wavs[i:i + 64]) for i in range(0, len(wavs), 64)])
        for lname, y in (("gemini", gem), ("rule", rule)):
            pred = pr > 0.5; acc = (pred == y).mean(); auc = roc_auc_score(y, pr) if len(set(y)) > 1 else float("nan")
            rc = (pred & (y == 1)).sum() / max((y == 1).sum(), 1); ri = ((~pred) & (y == 0)).sum() / max((y == 0).sum(), 1)
            out_rows.append(dict(language=NAMES[lang], n=len(y), label=lname, pos=100 * y.mean(), model=m.name, acc=100 * acc, auc=auc, rec_comp=100 * rc, rec_inc=100 * ri))
    print(f"{lang}: {len(wavs)} scored test clips", flush=True)
with open("reports/private_headtohead.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out_rows[0])); w.writeheader(); w.writerows(out_rows)
for lname, title in (("gemini", "Label = Gemini audio verdict (same labeler as the IndicVoices test set)"), ("rule", "Label = what happened in the recording (agent replied = complete; trainee resumed = incomplete)")):
    print(f"\n### {title}\n\n| language | n | complete% | model | accuracy | AUC | recall(complete) | recall(incomplete) |\n|---|---:|---:|---|---:|---:|---:|---:|")
    for r in out_rows:
        if r["label"] == lname: print(f"| {r['language']} | {r['n']} | {r['pos']:.0f} | {r['model']} | {r['acc']:.1f} | {r['auc']:.3f} | {r['rec_comp']:.1f} | {r['rec_inc']:.1f} |")
    tot = sum(r["n"] for r in out_rows if r["label"] == lname and r["model"] == models[0].name)
    print("\nWeighted overall:")
    for m in models:
        rs = [r for r in out_rows if r["label"] == lname and r["model"] == m.name]
        print(f"  {m.name:22s} accuracy {sum(r['acc']*r['n'] for r in rs)/tot:.1f}  AUC {sum(r['auc']*r['n'] for r in rs)/tot:.3f}  recall(complete) {sum(r['rec_comp']*r['n'] for r in rs)/tot:.1f}  recall(incomplete) {sum(r['rec_inc']*r['n'] for r in rs)/tot:.1f}")
