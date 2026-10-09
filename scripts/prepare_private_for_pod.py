#!/usr/bin/env python3
"""Select the usable production clips and write them as FLAC parquet for transfer to the pod.
train split: rows where the recording rule and Gemini agree (A -> complete, B -> incomplete).
test split:  every Gemini-labelled test row; endpoint_bool = Gemini verdict, rule label kept in rule_label.
Output: data/private/pod/<lang>.parquet (same columns as data/built, audio as FLAC bytes)."""
import json, hashlib, io, glob, os, collections, numpy as np, pyarrow as pa, pyarrow.parquet as pq, soundfile as sf
OUT = "data/private/pod"; os.makedirs(OUT, exist_ok=True)
schema = pa.schema([("audio", pa.struct([("bytes", pa.binary()), ("path", pa.string())])), ("endpoint_bool", pa.bool_()), ("language", pa.string()),
                    ("dataset", pa.string()), ("synthetic", pa.bool_()), ("midfiller", pa.bool_()), ("endfiller", pa.bool_()), ("spoken_text", pa.string()),
                    ("speaker_id", pa.string()), ("session", pa.string()), ("chunk", pa.int32()), ("split", pa.string()), ("llm_conf", pa.float32()),
                    ("rule_label", pa.bool_()), ("gemini_label", pa.bool_()), ("pause_s", pa.float32()), ("gap_user", pa.float32()), ("gap_agent", pa.float32())])
summary = {}
for p in sorted(glob.glob("data/private/[a-z][a-z][a-z].parquet")):
    lang = os.path.basename(p)[:3]
    lab = {r["key"]: r for r in map(json.loads, open(f"data/private/labels/{lang}.audio.jsonl")) if r.get("verdict") in ("complete", "incomplete")}
    pf = pq.ParquetFile(p); cols = {n: [] for n in schema.names}; c = collections.Counter()
    for g in range(pf.metadata.num_row_groups):
        d = pf.read_row_group(g).to_pydict()
        for i in range(len(d["session"])):
            key = f"{d['session'][i]}|{d['chunk'][i]}|{d['dataset'][i]}|{hashlib.md5(d['audio'][i]['bytes']).hexdigest()[:10]}"
            if key not in lab: c["unlabelled"] += 1; continue
            gem = lab[key]["verdict"] == "complete"; rule = bool(d["endpoint_bool"][i]); split = d["split"][i]
            if split == "train":
                if gem != rule: c["train_dropped_disagree"] += 1; continue
                label = gem
            else:
                label = gem
            x, sr = sf.read(io.BytesIO(d["audio"][i]["bytes"]), dtype="float32"); b = io.BytesIO(); sf.write(b, x, sr, format="FLAC"); flac = b.getvalue()
            cols["audio"].append({"bytes": flac, "path": f"{d['call_id'][i][:12]}_{d['chunk'][i]}.flac"}); cols["endpoint_bool"].append(label)
            cols["language"].append(lang); cols["dataset"].append("private_calls"); cols["synthetic"].append(False); cols["midfiller"].append(False); cols["endfiller"].append(False)
            cols["spoken_text"].append(""); cols["speaker_id"].append(d["call_id"][i]); cols["session"].append(d["call_id"][i]); cols["chunk"].append(int(d["chunk"][i]))
            cols["split"].append(split); cols["llm_conf"].append(float(lab[key]["confidence"])); cols["rule_label"].append(rule); cols["gemini_label"].append(gem)
            cols["pause_s"].append(float(d["pause_s"][i])); cols["gap_user"].append(float(d["gap_user"][i])); cols["gap_agent"].append(float(d["gap_agent"][i]))
            c[f"{split}_kept"] += 1; c[f"{split}_complete"] += int(label)
    pq.write_table(pa.Table.from_pydict(cols, schema=schema), f"{OUT}/{lang}.parquet", row_group_size=1000)
    summary[lang] = dict(c); print(lang, dict(c), f"{os.path.getsize(f'{OUT}/{lang}.parquet')/1e6:.0f} MB", flush=True)
json.dump(summary, open(f"{OUT}/summary.json", "w"), indent=1)
print("total MB:", round(sum(os.path.getsize(f) for f in glob.glob(f"{OUT}/*.parquet"))/1e6))
