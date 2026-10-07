"""Stage 3: audio second opinion with Gemini. Sends a built 8 s clip (plus transcript when
present) to gemini-3.7-flash and records a complete/incomplete verdict.

usage: python -m indic_turn.label_audio --lang hin --split test --limit 300 [--pausecut 50]
Output: data/labels/<lang>.audio.jsonl (resumable; key = session, chunk, dataset).
"""
from __future__ import annotations
import argparse, base64, json, os, random, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request, urllib.error
import pyarrow.parquet as pq
from .common import DATA, LANG_NAMES, ROOT

MODEL = os.environ.get("AUDIO_LABEL_MODEL", "gemini-3.7-flash")
import collections
STATS = collections.Counter()

PROMPT = """You are an expert in spoken {lang} dialogue and end-of-turn detection for voice AI.

You hear the last few seconds of ONE speaker's side of a real {lang} phone call (the other person is silent in this audio), ending where the speaker paused. Decide whether, at the END of this audio, the speaker has finished their turn.

- "complete": the speaker finished and yielded the floor. The other person could reply now without interrupting. Cues: finished sentence with a finite verb, a direct question, a short answer or acknowledgement, a closing idiom, falling pitch at the end.
- "incomplete": the speaker is mid-thought or holding the floor. Cues: ends on a conjunction or connective, a dependent/conditional/temporal clause, a verbal participle, an open list, a self-correction, a lead-in ("I wanted to say that..."), a trailing filler, or a flat/rising continuation tone and audible intake of breath.

Judge the audio first (prosody and pitch at the final 300-500 ms), and use the transcript, if given, only to resolve the words. Code-mixing with English is normal.
{transcript}
Reply with JSON only: {{"verdict": "complete" or "incomplete", "confidence": 0.0 to 1.0, "reason": "under 8 words"}}"""

def gemini(key, wav_bytes, lang, text):
    tr = f"\nTranscript: {text.strip()}\n" if text and text.strip() else "\n(No transcript available.)\n"
    body = {"contents": [{"parts": [{"text": PROMPT.format(lang=LANG_NAMES[lang], transcript=tr)},
                                    {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(wav_bytes).decode()}}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0,
                                 "thinkingConfig": {"thinkingLevel": "low"}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                 data=json.dumps(body).encode(), headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    for attempt in range(5):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            txt = r["candidates"][0]["content"]["parts"][0]["text"]
            obj = json.loads(txt); u = r.get("usageMetadata", {})
            return {"verdict": obj.get("verdict"), "confidence": float(obj.get("confidence", 0.5)), "reason": obj.get("reason", ""),
                    "tokens_in": u.get("promptTokenCount"), "tokens_out": u.get("candidatesTokenCount")}
        except Exception as e:  # HTTP 429/503, dropped connections, timeouts, bad JSON: retry with backoff
            STATS[type(e).__name__ + (f" {e.code}" if isinstance(e, urllib.error.HTTPError) else "")] += 1
            if attempt == 4:
                return {"verdict": "error", "confidence": 0.0, "reason": str(e)[:80], "tokens_in": 0, "tokens_out": 0}
            time.sleep(2 ** attempt + random.random())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True); ap.add_argument("--split", default="test")
    ap.add_argument("--limit", type=int, default=0, help="original (non pause-cut) clips; 0 = all")
    ap.add_argument("--pausecut", type=int, default=-1, help="pause-cut clips to include; -1 = all")
    ap.add_argument("--workers", type=int, default=24); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--parquet", default=None)
    a = ap.parse_args()
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env"); key = os.environ["GEMINI_API_KEY"]
    t = pq.read_table(a.parquet or DATA / "built" / f"{a.lang}.parquet")
    d = t.to_pydict(); rng = random.Random(a.seed)
    import hashlib
    def key_of(i): return f"{d['session'][i]}|{d['chunk'][i]}|{d['dataset'][i]}|{hashlib.md5(d['audio'][i]['bytes']).hexdigest()[:10]}"
    out = DATA / "labels" / f"{a.lang}.audio.jsonl"; done = set()
    if out.exists():
        done = {r["key"] for r in map(json.loads, out.open()) if r.get("verdict") in ("complete", "incomplete")}
    cand = [i for i in range(t.num_rows) if (not a.split or d["split"][i] == a.split)]
    orig = [i for i in cand if not d["dataset"][i].endswith("_pausecut") and key_of(i) not in done]
    pc = [i for i in cand if d["dataset"][i].endswith("_pausecut") and key_of(i) not in done]
    rng.shuffle(orig); rng.shuffle(pc)
    todo = (orig[:a.limit] if a.limit > 0 else orig) + (pc[:a.pausecut] if a.pausecut >= 0 else pc)
    print(f"[{a.lang}] {len(todo)} clips to label with {MODEL} ({len(done)} cached)", flush=True)
    tin = tout = 0; t0 = time.time()
    with out.open("a") as fh, ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(gemini, key, d["audio"][i]["bytes"], a.lang, d["spoken_text"][i]): i for i in todo}
        for k, f in enumerate(as_completed(futs), 1):
            i = futs[f]; r = f.result(); tin += r["tokens_in"] or 0; tout += r["tokens_out"] or 0
            fh.write(json.dumps({"key": key_of(i), "session": d["session"][i], "chunk": d["chunk"][i], "dataset": d["dataset"][i],
                                 "split": d["split"][i], "text_label": bool(d["endpoint_bool"][i]), "text_conf": float(d["llm_conf"][i]),
                                 "spoken_text": d["spoken_text"][i], "audio_model": MODEL, **r}, ensure_ascii=False) + "\n"); fh.flush()
            if k % 200 == 0 or k == len(todo):
                print(f"[{a.lang}]   {k}/{len(todo)} tokens in={tin} out={tout} {time.time()-t0:.0f}s ({k/(time.time()-t0):.2f} clips/s) retries={dict(STATS)}", flush=True)

if __name__ == "__main__":
    main()
