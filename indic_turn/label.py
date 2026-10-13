"""Step 2: label each conversational chunk end as complete / incomplete using a text LLM over the human transcripts, one request per recording session.

IndicVoices chunks are transcript segments split at pauses, so a chunk end is NOT necessarily a turn end. We show the model the ordered chunks of one speaker's side of the call and ask, for every chunk, whether the speaker has yielded the floor at its end. Output: data/labels/<lang>.jsonl, one line per chunk, cached and resumable.
"""
from __future__ import annotations
import argparse, asyncio, json, os, random, re, time
from collections import defaultdict
import pyarrow.parquet as pq
from dotenv import load_dotenv
from openai import AsyncOpenAI
from .common import DATA, LANG_NAMES, ROOT

load_dotenv(ROOT / ".env")
MODEL = os.environ.get("LABEL_MODEL", "gpt-6-luna")

SYSTEM = """You are an expert in spoken {lang} dialogue and end-of-turn (EOT) detection for voice AI.

You will see ONE speaker's side of a real two-person {lang} phone conversation, as an ordered list of transcript segments. The segments were cut automatically at pauses, so a segment boundary is often in the MIDDLE of a turn. The other speaker's words are not shown. Segment numbers may have gaps (dropped segments).

For EVERY segment decide what is true at the END of that segment:
- "complete": the speaker finished their turn and yielded the floor. The other person could start a full reply now without interrupting. Typical: finished sentence with a finite verb, direct question, short answer/acknowledgement ("okay", "yes"), closing idiom.
- "incomplete": the speaker was mid-thought or still holding the floor. Typical: ends on a conjunction/connective ("and", "but", "then", "so", "because"), a dependent/conditional/temporal clause, a verbal participle, a list that is still open, a self-correction, a lead-in like "I wanted to say that", trailing filler ("umm", "like"), or the NEXT segment clearly continues the same sentence.

Use what the next segments say as evidence of intent (if segment N+1 plainly continues the sentence of N, then N is incomplete), but remember the other person may have spoken between segments, so a natural, self-contained statement is "complete" even if the speaker continues on the same topic later. Judge the transcript as spoken {lang} (code-mixing with English is normal); ignore spelling errors.

Reply with JSON only, no prose: {{"labels": [[<segment number>, <1 if complete else 0>, <confidence 0-1 with one decimal>], ...]}} covering every segment number exactly once."""

def build_user(chunks):
    lines = []
    for c in chunks:
        lines.append(f"[{c['chunk']}] ({c['duration']:.1f}s) {c['text'].strip()}")
    return "Segments:\n" + "\n".join(lines)

def parse_labels(txt: str):
    m = re.search(r"\{.*\}", txt, re.S)
    obj = json.loads(m.group(0) if m else txt)
    out = {}
    for it in obj["labels"]:
        if isinstance(it, dict):
            i, v, c = it.get("i"), it.get("v"), it.get("c", 0.5)
        else:
            i, v, c = (list(it) + [0.5])[:3]
        if isinstance(v, str):
            v = {"complete": 1, "incomplete": 0}.get(v.lower())
        if v is None or i is None:
            continue
        out[int(i)] = (int(v), float(c))
    return out

def request_kwargs(model: str) -> dict[str, str | int]:
    """Return provider-safe generation options for a text labeling request."""
    if model.startswith(("gpt-5", "gpt-6")):
        return {"reasoning_effort": os.environ.get("LABEL_EFFORT") or "low"}
    return {"temperature": 0}

async def label_session(client, sem, lang, session, chunks, max_chunks=60):
    """Returns list of dict rows. Long sessions are labelled in overlapping windows."""
    rows, usage = [], {"in": 0, "out": 0}
    windows = [chunks[i:i + max_chunks] for i in range(0, len(chunks), max_chunks)] or [chunks]
    for win in windows:
        async with sem:
            for attempt in range(4):
                try:
                    r = await client.chat.completions.create(
                        model=MODEL, response_format={"type": "json_object"},
                        messages=[{"role": "system", "content": SYSTEM.format(lang=LANG_NAMES[lang])},
                                  {"role": "user", "content": build_user(win)}], **request_kwargs(MODEL))
                    labs = parse_labels(r.choices[0].message.content)
                    usage["in"] += r.usage.prompt_tokens; usage["out"] += r.usage.completion_tokens
                    break
                except Exception as e:
                    if attempt == 3:
                        print(f"[{lang}] session {session}: FAILED {e}", flush=True); labs = {}
                    else:
                        await asyncio.sleep(2 ** attempt + random.random())
        for c in win:
            if c["chunk"] in labs:
                v, conf = labs[c["chunk"]]
                rows.append({**c, "endpoint_bool": bool(v), "llm_conf": conf, "label_model": MODEL})
    return rows, usage

async def run(lang, limit_sessions, concurrency, limit_rows=0):
    idx = pq.read_table(DATA / "index" / f"{lang}.parquet").to_pylist()
    sessions = defaultdict(list)
    for r in idx:
        sessions[r["session"]].append(r)
    for s in sessions.values():
        s.sort(key=lambda r: r["chunk"])
    out = DATA / "labels"; out.mkdir(parents=True, exist_ok=True)
    path = out / f"{lang}{os.environ.get('LABEL_OUT_SUFFIX','')}.jsonl"
    done = set()
    if path.exists():
        for line in path.open():
            done.add(json.loads(line)["session"])
    todo = [s for s in sessions if s not in done]
    if limit_sessions:
        todo = todo[:limit_sessions]
    if limit_rows:
        have = sum(len(sessions[s]) for s in done); keep = []
        for s in todo:
            if have >= limit_rows: break
            keep.append(s); have += len(sessions[s])
        todo = keep
    print(f"[{lang}] {len(sessions)} sessions, {len(done)} already labelled, labelling {len(todo)} with {MODEL}", flush=True)
    client, sem = AsyncOpenAI(), asyncio.Semaphore(concurrency)
    tot = {"in": 0, "out": 0}; n_rows = 0; t0 = time.time()
    with path.open("a") as fh:
        tasks = [label_session(client, sem, lang, s, sessions[s]) for s in todo]
        for k, fut in enumerate(asyncio.as_completed(tasks), 1):
            rows, usage = await fut
            tot["in"] += usage["in"]; tot["out"] += usage["out"]; n_rows += len(rows)
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            fh.flush()
            if k % 20 == 0 or k == len(tasks):
                print(f"[{lang}]   {k}/{len(tasks)} sessions, {n_rows} rows, tokens in={tot['in']} out={tot['out']}, {time.time()-t0:.0f}s", flush=True)
    pos = sum(1 for line in path.open() if json.loads(line)["endpoint_bool"])
    n = sum(1 for _ in path.open())
    print(f"[{lang}] DONE: {n} labelled rows, {pos} complete ({100*pos/max(n,1):.1f}%), tokens in={tot['in']} out={tot['out']}", flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", required=True, help="ISO codes e.g. tel hin")
    ap.add_argument("--limit-sessions", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--limit-rows", type=int, default=0, help="stop once this many chunks are labelled")
    a = ap.parse_args()
    for lang in a.langs:
        asyncio.run(run(lang, a.limit_sessions, a.concurrency, a.limit_rows))

if __name__ == "__main__":
    main()
