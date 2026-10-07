"""Step 1: remotely scan IndicVoices parquet metadata (no audio download) and
index the conversational rows per language.

Reads only the non-audio columns via HTTP range requests, so a 0.5 GB shard costs
a few MB. Output: data/index/<lang>.parquet with one row per conversational chunk.
"""
from __future__ import annotations
import argparse, collections, json, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyarrow as pa, pyarrow.parquet as pq
from huggingface_hub import HfApi, HfFileSystem
from .common import DATA, HF_DATASET, LANGS, hf_token, parse_path

COLS = ["audio_filepath.path", "speaker_id", "task_name", "duration", "text", "samples", "gender", "age_group"]

def list_shards(api: HfApi, config: str):
    info = api.dataset_info(HF_DATASET, files_metadata=True)
    files = [(f.rfilename, f.size or 0) for f in info.siblings
             if f.rfilename.startswith(config + "/") and f.rfilename.endswith(".parquet")]
    # valid shards first (denser in conversation), then train in order
    files.sort(key=lambda x: (0 if "/valid-" in x[0] else 1, x[0]))
    return files

def scan_shard(fs: HfFileSystem, shard: str):
    with fs.open(f"datasets/{HF_DATASET}/{shard}", "rb") as f:
        pf = pq.ParquetFile(f)
        t = pf.read(columns=COLS)
    d = t.to_pydict()
    pathcol = next(c for c in t.column_names if c.startswith("audio_filepath"))
    rows = []
    for i in range(t.num_rows):
        if d["task_name"][i] != "Conversation":
            continue
        p = d[pathcol][i]
        p = p["path"] if isinstance(p, dict) else p
        parsed = parse_path(p)
        if not parsed:
            continue
        session, part, chunk = parsed
        rows.append({
            "shard": shard, "row": i, "path": p, "session": session, "chunk": chunk,
            "speaker_id": d["speaker_id"][i], "duration": float(d["duration"][i] or 0),
            "text": d["text"][i] or "", "gender": d["gender"][i], "age_group": d["age_group"][i],
        })
    return shard, t.num_rows, rows

def scan_language(config: str, target_rows: int, max_shards: int, workers: int):
    lang = LANGS[config]
    out = DATA / "index"; out.mkdir(parents=True, exist_ok=True)
    api, fs = HfApi(token=hf_token()), HfFileSystem(token=hf_token())
    shards = list_shards(api, config)[:max_shards]
    print(f"[{lang}] {len(shards)} candidate shards, target {target_rows} conversational rows", flush=True)
    all_rows, stats, t0 = [], [], time.time()
    # scan in waves of `workers` shards, stop once target reached
    for w in range(0, len(shards), workers):
        wave = shards[w:w + workers]
        with ThreadPoolExecutor(workers) as ex:
            futs = {ex.submit(scan_shard, fs, s): (s, sz) for s, sz in wave}
            for fut in as_completed(futs):
                s, sz = futs[fut]
                try:
                    shard, n, rows = fut.result()
                except Exception as e:
                    print(f"[{lang}]   {s}: ERROR {e}", flush=True); continue
                stats.append({"shard": shard, "size_bytes": sz, "rows": n, "conv_rows": len(rows),
                              "conv_sessions": len({r['session'] for r in rows})})
                all_rows.extend(rows)
                print(f"[{lang}]   {shard}: {len(rows)}/{n} conv rows, {sz/1e9:.2f} GB  (total {len(all_rows)}, {time.time()-t0:.0f}s)", flush=True)
        if len(all_rows) >= target_rows:
            break
    tbl = pa.Table.from_pylist(all_rows)
    pq.write_table(tbl, out / f"{lang}.parquet")
    (out / f"{lang}.shards.json").write_text(json.dumps(stats, indent=1))
    sess = collections.Counter(r["session"] for r in all_rows)
    dl = sum(s["size_bytes"] for s in stats if s["conv_rows"] > 0) / 1e9
    print(f"[{lang}] DONE: {len(all_rows)} conv rows, {len(sess)} sessions, {len({r['speaker_id'] for r in all_rows})} speakers, "
          f"{sum(r['duration'] for r in all_rows)/3600:.2f} h, download needed {dl:.1f} GB over {sum(1 for s in stats if s['conv_rows']>0)} shards", flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=list(LANGS), help="IndicVoices config names")
    ap.add_argument("--target-rows", type=int, default=9000)
    ap.add_argument("--max-shards", type=int, default=40)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    for cfg in a.langs:
        scan_language(cfg, a.target_rows, a.max_shards, a.workers)

if __name__ == "__main__":
    main()
