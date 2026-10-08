"""Stage 3: audio second opinion with Gemini. Sends a built 8 s clip (plus transcript when
present) to gemini-3.7-flash and records a complete/incomplete verdict.

usage: python -m indic_turn.label_audio --lang hin --split test --limit 300 [--pausecut 50]
Output: data/labels/<lang>.audio.jsonl (resumable; key = session, chunk, dataset).
"""
from __future__ import annotations
import argparse, base64, json, os, random, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
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

Judge prosody and pitch at the final 300-500 ms. Code-mixing with English is normal.
{transcript}
Reply with JSON only: {{"verdict": "complete" or "incomplete", "confidence": 0.0 to 1.0, "reason": "under 8 words"}}"""

def gemini(key, wav_bytes, lang, text="", audio_only=False):
    transcript = "" if audio_only else (f"\nTranscript: {text.strip()}\n" if text and text.strip() else "\n(No transcript available.)\n")
    body = {"contents": [{"parts": [{"text": PROMPT.format(lang=LANG_NAMES[lang], transcript=transcript)},
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
    ap.add_argument("--batch-size", type=int, default=128, help="parquet rows retained in memory at once")
    ap.add_argument("--parquet", default=None)
    ap.add_argument("--out", default=None, help="resumable JSONL destination")
    ap.add_argument("--audio-only", action="store_true", help="omit transcript from both the prompt and result")
    a = ap.parse_args()
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env"); key = os.environ["GEMINI_API_KEY"]
    if a.batch_size < 1:
        raise SystemExit("--batch-size must be at least one")
    source = pq.ParquetFile(a.parquet or DATA / "built" / f"{a.lang}.parquet")
    import hashlib
    def key_of(data, i): return f"{data['session'][i]}|{data['chunk'][i]}|{data['dataset'][i]}|{hashlib.md5(data['audio'][i]['bytes']).hexdigest()[:10]}"
    out = Path(a.out) if a.out else DATA / "labels" / f"{a.lang}.audio.jsonl"; out.parent.mkdir(parents=True, exist_ok=True); done = set()
    if out.exists():
        done = {r["key"] for r in map(json.loads, out.open()) if r.get("verdict") in ("complete", "incomplete")}
    print(f"[{a.lang}] streaming labels with {MODEL} ({len(done)} cached)", flush=True)
    tin = tout = processed = original = pausecuts = 0; t0 = time.time()
    with out.open("a") as fh, ThreadPoolExecutor(a.workers) as ex:
        for batch in source.iter_batches(batch_size=a.batch_size):
            data = batch.to_pydict(); futs = {}
            for i in range(batch.num_rows):
                if a.split and data["split"][i] != a.split:
                    continue
                key_id = key_of(data, i); pausecut = data["dataset"][i].endswith("_pausecut")
                if key_id in done or (pausecut and a.pausecut >= 0 and pausecuts >= a.pausecut) or (not pausecut and a.limit > 0 and original >= a.limit):
                    continue
                if pausecut:
                    pausecuts += 1
                else:
                    original += 1
                futs[ex.submit(gemini, key, data["audio"][i]["bytes"], a.lang, data["spoken_text"][i], a.audio_only)] = (key_id, i)
            for f in as_completed(futs):
                key_id, i = futs[f]; r = f.result(); processed += 1; tin += r["tokens_in"] or 0; tout += r["tokens_out"] or 0
                result = {"key": key_id, "split": data["split"][i], "text_label": bool(data["endpoint_bool"][i]), "text_conf": float(data["llm_conf"][i]), "audio_model": MODEL, **r}
                if not a.audio_only:
                    result.update({"session": data["session"][i], "chunk": data["chunk"][i], "dataset": data["dataset"][i], "spoken_text": data["spoken_text"][i]})
                fh.write(json.dumps(result, ensure_ascii=False) + "\n"); fh.flush()
                if processed % 200 == 0:
                    print(f"[{a.lang}]   {processed} tokens in={tin} out={tout} {time.time()-t0:.0f}s ({processed/(time.time()-t0):.2f} clips/s) retries={dict(STATS)}", flush=True)
    print(f"[{a.lang}] complete: {processed} new labels, tokens in={tin} out={tout}", flush=True)

if __name__ == "__main__":
    main()
