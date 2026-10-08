#!/usr/bin/env python3
"""Per-language decision thresholds from dev probabilities, applied to test probabilities.
usage: tune_thresholds.py reports/dev_probs.csv reports/test_probs.csv reports/thresholds.md
Threshold = argmax of balanced accuracy on dev (mean of recall on complete and recall on incomplete),
searched on a 0.05..0.95 grid; the default 0.5 is reported alongside."""
import csv, sys, json, collections, numpy as np
dev_path, test_path, out_path = sys.argv[1:4]
def load(p):
    rows = list(csv.DictReader(open(p)))
    models = [k for k in rows[0] if k not in ("language", "dataset", "label")]
    return rows, models
dev, models = load(dev_path); test, _ = load(test_path)
def by_lang(rows): 
    d = collections.defaultdict(list); [d[r["language"]].append(r) for r in rows]; return d
dl, tl = by_lang(dev), by_lang(test)
def metrics(p, y, t):
    pred = p > t; tp = ((pred) & (y == 1)).sum(); tn = ((~pred) & (y == 0)).sum()
    rec_c = tp / max((y == 1).sum(), 1); rec_i = tn / max((y == 0).sum(), 1)
    return (tp + tn) / len(y), rec_c, rec_i, (rec_c + rec_i) / 2
grid = np.round(np.arange(0.05, 0.96, 0.025), 3)
thr = {m: {} for m in models}; L = ["# Per-language thresholds (tuned on dev for balanced accuracy, applied to test)", ""]
for m in models:
    L += [f"## {m}", "", "| language | n test | thr | acc@0.5 | acc@thr | rec(comp)@0.5 → @thr | rec(inc)@0.5 → @thr | bal.acc@0.5 → @thr |", "|---|---:|---:|---:|---:|---|---|---|"]
    for lang in sorted(tl):
        if lang not in dl: continue
        pd_, yd = np.array([float(r[m]) for r in dl[lang]]), np.array([int(r["label"]) for r in dl[lang]])
        best = max(grid, key=lambda t: metrics(pd_, yd, t)[3]); thr[m][lang] = float(best)
        pt, yt = np.array([float(r[m]) for r in tl[lang]]), np.array([int(r["label"]) for r in tl[lang]])
        a0, c0, i0, b0 = metrics(pt, yt, 0.5); a1, c1, i1, b1 = metrics(pt, yt, best)
        L.append(f"| {lang} | {len(yt)} | {best:.3f} | {100*a0:.1f} | {100*a1:.1f} | {100*c0:.1f} → {100*c1:.1f} | {100*i0:.1f} → {100*i1:.1f} | {100*b0:.1f} → {100*b1:.1f} |")
    L.append("")
open(out_path, "w").write("\n".join(L)); json.dump(thr, open(out_path.replace(".md", ".json"), "w"), indent=1)
print("\n".join(L))
