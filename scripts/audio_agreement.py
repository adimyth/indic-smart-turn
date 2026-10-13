#!/usr/bin/env python3
"""Agreement between text labels and the Gemini audio verdicts. usage: audio_agreement.py hin [kan ...]"""
import json, sys, collections
import pyarrow.parquet as pq
from pathlib import Path
for lang in sys.argv[1:]:
    rows=[json.loads(l) for l in open(f"data/labels/{lang}.audio.jsonl")]
    rows=[r for r in rows if r["verdict"] in ("complete","incomplete")]
    errs=sum(1 for l in open(f"data/labels/{lang}.audio.jsonl") if json.loads(l)["verdict"]=="error")
    # durations of the original segment from the label file (chunk duration)
    dur={}
    for f in [f"data/labels/{lang}.jsonl"]:
        for l in open(f):
            r=json.loads(l); dur[(r["session"],r["chunk"])]=r["duration"]
    orig=[r for r in rows if not r["dataset"].endswith("_pausecut")]
    pc=[r for r in rows if r["dataset"].endswith("_pausecut")]
    def agree(rs): return sum((r["verdict"]=="complete")==r["text_label"] for r in rs)
    print(f"=== {lang}: {len(orig)} segments, {len(pc)} pause-cuts, {errs} errors ===")
    n=len(orig); a=agree(orig)
    tc=sum(r["text_label"] for r in orig); ac=sum(r["verdict"]=="complete" for r in orig)
    print(f"overall agreement: {a}/{n} = {100*a/n:.1f}%   text complete-rate {100*tc/n:.0f}%  audio complete-rate {100*ac/n:.0f}%")
    # confusion
    cm=collections.Counter((r["text_label"], r["verdict"]=="complete") for r in orig)
    print(f"  text=complete & audio=complete {cm[(True,True)]} | text=complete & audio=incomplete {cm[(True,False)]} | text=incomplete & audio=incomplete {cm[(False,False)]} | text=incomplete & audio=complete {cm[(False,True)]}")
    for lo,hi in [(0,1.5),(1.5,4),(4,99)]:
        rs=[r for r in orig if lo<=dur.get((r["session"],r["chunk"]),0)<hi]
        if rs: print(f"  dur {lo}-{hi}s: n={len(rs)} agreement {100*agree(rs)/len(rs):.1f}%  text-complete {100*sum(r['text_label'] for r in rs)/len(rs):.0f}%  audio-complete {100*sum(r['verdict']=='complete' for r in rs)/len(rs):.0f}%")
    hi=[r for r in orig if r["confidence"]>=0.8]
    if hi: print(f"  audio-confident (>=0.8): n={len(hi)} agreement {100*agree(hi)/len(hi):.1f}%")
    if pc: print(f"pause-cuts judged incomplete by audio: {sum(r['verdict']=='incomplete' for r in pc)}/{len(pc)} = {100*sum(r['verdict']=='incomplete' for r in pc)/len(pc):.0f}%")
    print("--- disagreements (text / audio, audio conf, reason) ---")
    for r in [r for r in orig if (r["verdict"]=="complete")!=r["text_label"]][:14]:
        print(f"  T={'C' if r['text_label'] else 'I'} A={'C' if r['verdict']=='complete' else 'I'} ({r['confidence']:.1f}) {r['spoken_text'][:70]}  | {r['reason']}")
