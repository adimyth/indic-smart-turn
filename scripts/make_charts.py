#!/usr/bin/env python3
"""Four per-group charts: accuracy per language, ours vs Smart Turn v3.2, from the Stage 6 reports."""
import re, csv, collections, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
OURS, V32 = "#2a78d6", "#eb6834"; SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
LANGS = ["English","Hindi","Marathi","Bengali","Tamil","Telugu","Kannada","Malayalam","Gujarati","Punjabi","Odia","Assamese"]
rows = {}
sec = open("reports/eval_all_test.md").read().split("## Clean test split")[1].split("### By dataset")[0]
for line in sec.splitlines():
    m = re.match(r"\| ([^|]+) \| (\d+) \| (\d+) \| (\S+) \| ([\d.]+) \[", line)
    if m: rows[(m[1].strip(), m[4])] = float(m[5])
# base dynamic int8 from the per-clip probabilities on the same test rows
probs = collections.defaultdict(list)
for r in csv.DictReader(open("reports/test_probs.csv")):
    probs[r["language"]].append((float(r["base_int8_dynamic"]) > 0.5) == (r["label"] == "1"))
code = {"eng":"English","hin":"Hindi","mar":"Marathi","ben":"Bengali","tam":"Tamil","tel":"Telugu","kan":"Kannada","mal":"Malayalam","guj":"Gujarati","pan":"Punjabi","ori":"Odia","asm":"Assamese"}
for c, v in probs.items(): rows[(code.get(c, c), "base_int8_dynamic")] = 100 * np.mean(v)
groups = [("group1_tiny_int8", "Group 1: whisper-tiny, int8 (8.7 MB) vs Smart Turn v3.2 (int8, same size)", "tiny_int8", "Indic Smart Turn tiny int8"),
          ("group2_base_int8", "Group 2: whisper-base, dynamic int8 (24 MB) vs Smart Turn v3.2", "base_int8_dynamic", "Indic Smart Turn base int8"),
          ("group3_tiny_fp32", "Group 3: whisper-tiny, fp32 (32 MB) vs Smart Turn v3.2", "tiny_fp32", "Indic Smart Turn tiny fp32"),
          ("group4_base_fp32", "Group 4: whisper-base, fp32 (81 MB) vs Smart Turn v3.2", "base_fp32", "Indic Smart Turn base fp32")]
for fname, title, key, label in groups:
    ours = [rows[(l, key)] for l in LANGS]; v32 = [rows[(l, "stock_v3.2_cpu")] for l in LANGS]
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=160); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    y = np.arange(len(LANGS)); h = 0.34
    ax.barh(y - h/2 - 0.02, ours, height=h, color=OURS, label=label, zorder=3)
    ax.barh(y + h/2 + 0.02, v32, height=h, color=V32, label="Smart Turn v3.2 (Pipecat)", zorder=3)
    for i, (o, s) in enumerate(zip(ours, v32)):
        ax.text(max(o, s) + 0.8, y[i], f"{o - s:+.1f}", va="center", ha="left", fontsize=9, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(LANGS, color=INK, fontsize=10); ax.invert_yaxis()
    ax.set_xlim(50, 100); ax.set_xlabel("Accuracy on the clean test split (%)", color=INK2, fontsize=9)
    ax.xaxis.grid(True, color="#e6e5e1", zorder=0); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#cfcec9"); ax.tick_params(colors=INK2, length=0)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=30)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=9, labelcolor=INK)
    ax.text(0, -0.09, "Δ = accuracy difference in points. English/Hindi/Marathi/Bengali include Pipecat's own test set; Tamil includes the human-validated TamilEOT test set.", transform=ax.transAxes, fontsize=7.5, color=INK2)
    fig.tight_layout(); fig.savefig(f"docs/figures/{fname}.png", facecolor=SURF); plt.close(fig)
    print(fname, "mean Δ %+.1f" % (np.mean(ours) - np.mean(v32)))
