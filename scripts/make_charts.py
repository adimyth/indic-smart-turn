#!/usr/bin/env python3
"""Four per-group result charts as hand-drawn SVG (light and dark), ours vs Smart Turn v3.2, from the Stage 6 reports.
SVGs render in GitHub and Hugging Face READMEs without any JavaScript; docs/charts.html is the interactive version."""
import re, csv, json, collections, numpy as np
LANGS = ["English","Hindi","Marathi","Bengali","Tamil","Telugu","Kannada","Malayalam","Gujarati","Punjabi","Odia","Assamese"]
rows = {}
sec = open("reports/eval_all_test.md").read().split("## Clean test split")[1].split("### By dataset")[0]
for line in sec.splitlines():
    m = re.match(r"\| ([^|]+) \| (\d+) \| (\d+) \| (\S+) \| ([\d.]+) \[", line)
    if m: rows[(m[1].strip(), m[4])] = float(m[5])
probs = collections.defaultdict(list)
for r in csv.DictReader(open("reports/test_probs.csv")):
    probs[r["language"]].append((float(r["base_int8_dynamic"]) > 0.5) == (r["label"] == "1"))
code = {"eng":"English","hin":"Hindi","mar":"Marathi","ben":"Bengali","tam":"Tamil","tel":"Telugu","kan":"Kannada","mal":"Malayalam","guj":"Gujarati","pan":"Punjabi","ori":"Odia","asm":"Assamese"}
for c, v in probs.items(): rows[(code.get(c, c), "base_int8_dynamic")] = 100 * np.mean(v)
# Pipecat ships Smart Turn v3.2 as two whisper-tiny files: int8 (CPU) and fp32 (GPU). Each group is paired with the same-precision file.
GROUPS = [("group1_tiny_int8", "Tiny int8 (8.7 MB)", "tiny_int8", "Indic Smart Turn tiny int8", "stock_v3.2_cpu", "Smart Turn v3.2 int8"),
          ("group2_base_int8", "Base int8 (24 MB)", "base_int8_dynamic", "Indic Smart Turn base int8", "stock_v3.2_cpu", "Smart Turn v3.2 int8"),
          ("group3_tiny_fp32", "Tiny fp32 (32 MB)", "tiny_fp32", "Indic Smart Turn tiny fp32", "stock_v3.2_gpu", "Smart Turn v3.2 fp32"),
          ("group4_base_fp32", "Base fp32 (81 MB)", "base_fp32", "Indic Smart Turn base fp32", "stock_v3.2_gpu", "Smart Turn v3.2 fp32")]
THEMES = {"light": dict(bg="#fcfcfb", ink="#141412", ink2="#55534d", ink3="#8a877f", grid="#e6e5df", ours="#2a78d6", base="#eb6834"),
          "dark":  dict(bg="#1a1a19", ink="#f3f2ee", ink2="#c3c2b7", ink3="#8f8d85", grid="#2f2f2c", ours="#3987e5", base="#d95926")}
FONT = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
def svg(d, t):
    W, L, R, T, rowH, bar, gap = 920, 104, 120, 76, 40, 13, 3
    n = len(d["languages"]); H = T + n * rowH + 44
    lo = min(d["ours"] + d["baseline"]); x0 = int(lo // 10 * 10) - (10 if lo % 10 < 2 else 0); x1 = 100
    sx = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="{t["bg"]}" rx="6"/>',
         f'<text x="{L}" y="26" font-size="17" font-weight="600" fill="{t["ink"]}">{d["ours_label"]} vs {d["baseline_label"]}</text>',
         f'<rect x="{L}" y="40" width="14" height="10" rx="2" fill="{t["ours"]}"/><text x="{L+20}" y="49" font-size="12.5" fill="{t["ink2"]}">{d["ours_label"]}</text>',
         f'<rect x="{L+240}" y="40" width="14" height="10" rx="2" fill="{t["base"]}"/><text x="{L+260}" y="49" font-size="12.5" fill="{t["ink2"]}">{d["baseline_label"]}</text>',
         f'<text x="{L}" y="66" font-size="11.5" fill="{t["ink3"]}">Accuracy on the clean test split, %. The number after each pair is the difference in points.</text>']
    for g in range(x0, x1 + 1, 10):
        o.append(f'<line x1="{sx(g):.1f}" x2="{sx(g):.1f}" y1="{T}" y2="{H-30}" stroke="{t["grid"]}" stroke-width="1"/>')
        o.append(f'<text x="{sx(g):.1f}" y="{H-12}" font-size="11.5" fill="{t["ink3"]}" text-anchor="middle" font-family="{MONO}">{g}</text>')
    for i, lang in enumerate(d["languages"]):
        y = T + i * rowH; a, b = d["ours"][i], d["baseline"][i]; dl = a - b
        o.append(f'<text x="{L-12}" y="{y + rowH/2 + 4.5:.1f}" font-size="13.5" fill="{t["ink"]}" text-anchor="end">{lang}</text>')
        for v, col, yy in ((a, t["ours"], y + 5), (b, t["base"], y + 5 + bar + gap)):
            w = max(sx(v) - sx(x0), 4)
            o.append(f'<path d="M{sx(x0):.1f},{yy} h{w-4:.1f} a4,4 0 0 1 4,4 v{bar-8} a4,4 0 0 1 -4,4 h-{w-4:.1f} z" fill="{col}"/>')
        o.append(f'<text x="{sx(max(a,b)) + 8:.1f}" y="{y + rowH/2 + 4.5:.1f}" font-size="12.5" fill="{t["ink2"]}" font-family="{MONO}">{dl:+.1f}</text>')
    o.append("</svg>"); return "\n".join(o)
export = {}
for fname, short, key, label, bkey, blabel in GROUPS:
    d = {"title": short, "ours_label": label, "baseline_label": blabel, "languages": LANGS,
         "ours": [round(rows[(l, key)], 1) for l in LANGS], "baseline": [round(rows[(l, bkey)], 1) for l in LANGS]}
    export[fname] = d
    for theme, t in THEMES.items():
        open(f"docs/figures/{fname}-{theme}.svg", "w").write(svg(d, t))
    print(fname, "mean Δ %+.1f" % (np.mean(d["ours"]) - np.mean(d["baseline"])))
json.dump(export, open("docs/figures/chart_data.json", "w"), indent=1)
