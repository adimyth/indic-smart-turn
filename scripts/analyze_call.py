#!/usr/bin/env python3
"""Analyze one mixed-channel call: VAD, 2-speaker clustering, agent/user assignment, turn-boundary rule labels.
usage: analyze_call.py <wav16k_mono> [--preview-dir DIR] [--n-preview 10]"""
import argparse, json, sys, numpy as np, soundfile as sf
from pathlib import Path
import torch
from silero_vad import load_silero_vad, get_speech_timestamps
from resemblyzer import VoiceEncoder
SR = 16000
ap = argparse.ArgumentParser(); ap.add_argument("wav"); ap.add_argument("--preview-dir", default=None); ap.add_argument("--n-preview", type=int, default=10)
ap.add_argument("--min-silence-ms", type=int, default=200)
ap.add_argument("--agent-ref", default="data/private/agent_reference.npy"); a = ap.parse_args()
x, sr = sf.read(a.wav, dtype="float32"); assert sr == SR
if x.ndim > 1: x = x.mean(1)
dur = len(x) / SR
vad = load_silero_vad()
ts = get_speech_timestamps(torch.from_numpy(x), vad, sampling_rate=SR, min_silence_duration_ms=a.min_silence_ms, min_speech_duration_ms=150, speech_pad_ms=60, return_seconds=True)
segs = [(t["start"], t["end"]) for t in ts]
print(f"duration {dur:.1f}s, speech segments {len(segs)}, speech {sum(e-s for s,e in segs):.1f}s ({100*sum(e-s for s,e in segs)/dur:.0f}%)")
# speaker embeddings per segment (>=0.4 s)
enc = VoiceEncoder(verbose=False)
emb, idx = [], []
for i, (s, e) in enumerate(segs):
    if e - s >= 0.4:
        emb.append(enc.embed_utterance(x[int(s*SR):int(e*SR)])); idx.append(i)
emb = np.stack(emb); emb /= np.linalg.norm(emb, axis=1, keepdims=True)
# 2-means with cosine, several restarts
best = None
for seed in range(10):
    rng = np.random.default_rng(seed); c = emb[rng.choice(len(emb), 2, replace=False)]
    for _ in range(30):
        lab = np.argmax(emb @ c.T, axis=1)
        if min((lab == k).sum() for k in range(2)) == 0: break
        c = np.stack([emb[lab == k].mean(0) for k in range(2)]); c /= np.linalg.norm(c, axis=1, keepdims=True)
    score = float(np.mean(np.max(emb @ c.T, axis=1)))
    if best is None or score > best[0]: best = (score, lab.copy(), c.copy())
score, lab, c = best
sim = emb @ c.T
# agent = the cluster closest to the stored agent-voice reference (same TTS voice in every session);
# the first speaker of a session is the agent, used as a check and as the bootstrap for the reference.
cons = [float(sim[lab == k, k].mean()) for k in range(2)]
REF = Path(a.agent_ref)
first_k = int(lab[0])
if REF.exists():
    ref = np.load(REF); ref_sim = [float(ref @ c[k]) for k in range(2)]
    agent_k = int(np.argmax(ref_sim))
    flag = "" if agent_k == first_k else "  WARNING: reference and first-speaker disagree"
    print(f"agent by reference: cluster{agent_k} (sim {ref_sim[agent_k]:.2f} vs {ref_sim[1-agent_k]:.2f}); first speaker cluster{first_k}{flag}")
else:
    agent_k = first_k; np.save(REF, c[agent_k]); print(f"agent by first speaker: cluster{agent_k}; saved reference to {REF}")
user_k = 1 - agent_k
spk = {}
for j, i in enumerate(idx): spk[i] = "agent" if lab[j] == agent_k else "user"
# short segments: assign to nearest centroid using a tiny embedding if possible, else to previous speaker
for i, (s, e) in enumerate(segs):
    if i not in spk:
        try:
            v = enc.embed_utterance(x[int(s*SR):int(e*SR)]); v /= np.linalg.norm(v); spk[i] = "agent" if np.argmax(v @ c.T) == agent_k else "user"
        except Exception: spk[i] = spk.get(i-1, "user")
margin = np.abs(sim[:, 0] - sim[:, 1])
print(f"clusters: agent={sum(1 for v in spk.values() if v=='agent')} segs / {sum(e-s for i,(s,e) in enumerate(segs) if spk[i]=='agent'):.0f}s, "
      f"user={sum(1 for v in spk.values() if v=='user')} segs / {sum(e-s for i,(s,e) in enumerate(segs) if spk[i]=='user'):.0f}s; "
      f"self-consistency agent={cons[agent_k]:.2f} user={cons[user_k]:.2f}; low-margin (<0.05) segments={int((margin<0.05).sum())}/{len(margin)}")
print("timeline (first 24):")
for i, (s, e) in enumerate(segs[:24]): print(f"  {s:7.1f}-{e:7.1f} {e-s:5.1f}s {spk[i]}")
# rule labels on user boundaries
user = [(s, e) for i, (s, e) in enumerate(segs) if spk[i] == "user"]; agent = [(s, e) for i, (s, e) in enumerate(segs) if spk[i] == "agent"]
def next_start(regs, t): 
    n = [s for s, e in regs if s >= t]; return min(n) if n else None
rows = []
for k, (s, e) in enumerate(user):
    nu = next_start(user, e + 1e-3); na = next_start(agent, e - 0.3)  # agent may start slightly before VAD closes
    gap_u = (nu - e) if nu is not None else 99; gap_a = (na - e) if na is not None else 99
    AGENT_WIN = 5.0  # the agent in these sessions answers 1-4.5 s after the user stops
    if gap_a <= AGENT_WIN and gap_u > gap_a + 1.5: lab_ = "complete"
    elif gap_u <= 2.0 and gap_a > gap_u: lab_ = "incomplete"
    elif gap_a <= AGENT_WIN and gap_u <= gap_a + 1.5: lab_ = "ambiguous_overlap"
    else: lab_ = "ambiguous_silence"
    rows.append({"end": e, "start": s, "gap_user": gap_u, "gap_agent": gap_a, "label": lab_})
from collections import Counter
print("boundary labels:", dict(Counter(r["label"] for r in rows)))
lat = [r["gap_agent"] for r in rows if r["label"] == "complete"]
if lat: print(f"agent response latency on complete turns: median {np.median(lat):.1f}s, max {max(lat):.1f}s")
if a.preview_dir:
    out = Path(a.preview_dir); out.mkdir(parents=True, exist_ok=True)
    y = x.copy()
    for s, e in agent: y[int(s*SR):int(e*SR)] = 0  # keep user channel only
    comp = [r for r in rows if r["label"] == "complete"]; inc = [r for r in rows if r["label"] == "incomplete"]
    picks = comp + inc[: a.n_preview]  # every complete boundary plus a sample of incompletes
    for r in picks:
        end = int((r["end"] + 0.2) * SR); clip = y[max(0, end - 8*SR):end]
        sf.write(out / f"{r['end']:07.1f}s_{r['label']}.wav", clip, SR)
    (out / "boundaries.json").write_text(json.dumps(rows, indent=1))
    print(f"wrote {len(picks)} preview clips to {out}")
