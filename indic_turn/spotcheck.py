"""Create deterministic, self-contained spot-check pages for Gemini-primary built samples."""
from __future__ import annotations

import argparse
import base64
import gc
import json
import random
import shutil
import subprocess
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

from .common import DATA

REQUIRED_COLUMNS = {"audio", "endpoint_bool", "text_label", "audio_conf", "audio_reason", "ambiguous", "dataset", "language", "session", "chunk", "split", "spoken_text"}
PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Indic Smart Turn spot-check — __LANG__</title>
<style>
:root { color-scheme: light dark; font-family: ui-sans-serif, system-ui, sans-serif; }
body { margin: 0 auto; max-width: 950px; padding: 24px; background: Canvas; color: CanvasText; }
h1 { margin-bottom: 4px; } .note { color: #667085; margin-top: 0; }
.toolbar { position: sticky; top: 0; display: flex; gap: 10px; flex-wrap: wrap; padding: 12px 0; background: Canvas; border-bottom: 1px solid #d0d5dd; }
button { padding: 7px 11px; border: 1px solid #98a2b3; border-radius: 7px; font: inherit; cursor: pointer; background: ButtonFace; color: ButtonText; }
button.active { background: #175cd3; color: white; border-color: #175cd3; }
.card { margin: 18px 0; padding: 16px; border: 1px solid #d0d5dd; border-radius: 10px; }
.card.ambiguous { border-left: 5px solid #f79009; }.meta { color: #475467; font-size: .9rem; }.labels { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
.pill { padding: 3px 7px; border-radius: 999px; background: #eef4ff; color: #175cd3; font-size: .85rem; }.incomplete { background: #fef3f2; color: #b42318; }.amb { background: #fffaeb; color: #b54708; }
audio { width: 100%; margin: 8px 0; }.transcript { white-space: pre-wrap; line-height: 1.45; }.reason { color: #475467; font-size: .94rem; }.votes { display: flex; gap: 8px; margin-top: 12px; }
</style>
<h1>__LANG__ spot-check</h1>
<p class="note">15 balanced non-ambiguous test samples plus up to 5 text-vs-audio disagreements. Judgments remain in this browser's local storage; use Download judgments after review.</p>
<div class="toolbar"><button id="download">Download judgments</button><button id="clear">Clear local judgments</button><span id="progress"></span></div>
<main id="cards"></main>
<script>
const records = __RECORDS__;
const storagePrefix = 'indic-smart-turn-spotcheck:';
const byId = new Map(records.map(record => [record.id, record]));
function loadVote(id) { try { return JSON.parse(localStorage.getItem(storagePrefix + id)); } catch { return null; } }
function setVote(id, verdict) { localStorage.setItem(storagePrefix + id, JSON.stringify({id, verdict, reviewed_at: new Date().toISOString(), sample: byId.get(id)})); render(); }
function label(value) { return value ? 'complete' : 'incomplete'; }
function pill(text, extra = '') { const el = document.createElement('span'); el.className = 'pill ' + extra; el.textContent = text; return el; }
function render() {
  const cards = document.getElementById('cards'); cards.replaceChildren(); let reviewed = 0;
  for (const record of records) {
    const vote = loadVote(record.id); if (vote) reviewed += 1;
    const card = document.createElement('section'); card.className = 'card' + (record.ambiguous ? ' ambiguous' : '');
    const heading = document.createElement('div'); heading.className = 'meta'; heading.textContent = `${record.kind} · ${record.id} · ${record.session} / chunk ${record.chunk}`; card.append(heading);
    const labels = document.createElement('div'); labels.className = 'labels'; labels.append(pill(`audio: ${record.audio_label}`, record.endpoint_bool ? '' : 'incomplete'));
    if (record.text_label !== null) labels.append(pill(`text: ${label(record.text_label)}`, record.text_label ? '' : 'incomplete'));
    if (record.ambiguous) labels.append(pill('ambiguous', 'amb')); labels.append(pill(`Gemini confidence: ${record.audio_conf.toFixed(1)}`)); card.append(labels);
    const audio = document.createElement('audio'); audio.controls = true; audio.preload = 'none'; audio.src = record.audio_data; card.append(audio);
    const transcript = document.createElement('div'); transcript.className = 'transcript'; transcript.textContent = record.spoken_text || '(pause-cut; no transcript)'; card.append(transcript);
    const reason = document.createElement('p'); reason.className = 'reason'; reason.textContent = `Gemini: ${record.audio_reason || '(no reason supplied)'}`; card.append(reason);
    const votes = document.createElement('div'); votes.className = 'votes';
    for (const verdict of ['agree', 'disagree']) { const button = document.createElement('button'); button.textContent = verdict; if (vote?.verdict === verdict) button.classList.add('active'); button.onclick = () => setVote(record.id, verdict); votes.append(button); }
    card.append(votes); cards.append(card);
  }
  document.getElementById('progress').textContent = `${reviewed}/${records.length} reviewed`;
}
document.getElementById('download').onclick = () => { const votes = records.map(record => loadVote(record.id)).filter(Boolean); const blob = new Blob([JSON.stringify(votes, null, 2)], {type: 'application/json'}); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = '__LANG___judgments.json'; link.click(); URL.revokeObjectURL(link.href); };
document.getElementById('clear').onclick = () => { if (confirm('Clear all local judgments for this language?')) { for (const record of records) localStorage.removeItem(storagePrefix + record.id); render(); } };
render();
</script>
</html>
"""


def label_name(value: bool) -> str:
    return "complete" if value else "incomplete"


def read_candidates(path: Path):
    columns = sorted(REQUIRED_COLUMNS)
    normal = {True: [], False: []}
    ambiguous = []
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=128, columns=columns):
        values = batch.to_pydict()
        for i in range(batch.num_rows):
            split = values["split"][i]
            row = {name: values[name][i] for name in columns}
            if split == "test":
                normal[bool(row["endpoint_bool"])].append(row)
            elif split == "test_ambiguous" and bool(row["ambiguous"]):
                ambiguous.append(row)
    return normal, ambiguous


def sample_normal(candidates, count: int, rng: random.Random):
    complete_target = (count + 1) // 2
    incomplete_target = count // 2
    selected = []
    for label, target in ((True, complete_target), (False, incomplete_target)):
        selected.extend(rng.sample(candidates[label], min(target, len(candidates[label]))))
    leftovers = [row for label in (True, False) for row in candidates[label] if row not in selected]
    if len(selected) < count:
        selected.extend(rng.sample(leftovers, min(count - len(selected), len(leftovers))))
    rng.shuffle(selected)
    return selected


def audio_as_mp3(wav_path: Path) -> bytes:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to keep each self-contained spot-check page under 16 MB")
    run = subprocess.run([ffmpeg, "-v", "error", "-i", str(wav_path), "-ac", "1", "-ar", "16000", "-b:a", "48k", "-f", "mp3", "pipe:1"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if run.returncode:
        raise RuntimeError(f"ffmpeg failed for {wav_path}: {run.stderr.decode(errors='replace').strip()}")
    return run.stdout


def write_language(lang: str, source: Path, destination: Path, normal_count: int, ambiguous_count: int, seed: int):
    schema_names = set(pq.ParquetFile(source).schema_arrow.names)
    missing = REQUIRED_COLUMNS - schema_names
    if missing:
        print(f"[{lang}] skipping: Gemini-primary columns are absent ({', '.join(sorted(missing))})", flush=True)
        return None
    normal, ambiguous = read_candidates(source)
    rng = random.Random(f"{seed}:{lang}")
    selected = sample_normal(normal, normal_count, rng)
    selected.extend(rng.sample(ambiguous, min(ambiguous_count, len(ambiguous))))
    if not selected:
        print(f"[{lang}] skipping: no test rows", flush=True)
        return None
    lang_dir = destination / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for index, row in enumerate(selected, 1):
        kind = "ambiguous" if row["ambiguous"] else "test"
        file_name = f"{index:02d}_{kind}_{label_name(bool(row['endpoint_bool']))}.wav"
        wav_path = lang_dir / file_name
        wav_path.write_bytes(row["audio"]["bytes"])
        mp3 = audio_as_mp3(wav_path)
        sample_id = f"{lang}:{row['session']}:{row['chunk']}:{row['dataset']}:{index}"
        records.append({
            "id": sample_id,
            "kind": kind,
            "file": file_name,
            "session": row["session"],
            "chunk": row["chunk"],
            "dataset": row["dataset"],
            "split": row["split"],
            "spoken_text": row["spoken_text"],
            "endpoint_bool": bool(row["endpoint_bool"]),
            "audio_label": label_name(bool(row["endpoint_bool"])),
            "text_label": None if row["text_label"] is None else bool(row["text_label"]),
            "audio_conf": float(row["audio_conf"]),
            "audio_reason": row["audio_reason"],
            "ambiguous": bool(row["ambiguous"]),
            "audio_data": f"data:audio/mpeg;base64,{base64.b64encode(mp3).decode('ascii')}",
        })
    index_records = [{key: value for key, value in row.items() if key != "audio_data"} for row in records]
    (lang_dir / "index.json").write_text(json.dumps(index_records, ensure_ascii=False, indent=2) + "\n")
    page_records = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    (lang_dir / "spotcheck.html").write_text(PAGE_TEMPLATE.replace("__LANG__", lang).replace("__RECORDS__", page_records))
    labels = Counter(record["audio_label"] for record in records)
    page_size = (lang_dir / "spotcheck.html").stat().st_size / 1_000_000
    print(f"[{lang}] wrote {len(records)} samples ({dict(labels)}; {sum(record['ambiguous'] for record in records)} ambiguous) to {lang_dir} ({page_size:.1f} MB page)", flush=True)
    del normal, ambiguous, selected, records
    gc.collect()
    return {"lang": lang, "samples": len(index_records), "labels": dict(labels), "ambiguous": sum(record["ambiguous"] for record in index_records)}


def write_landing_page(destination: Path, summaries):
    links = "\n".join(f'<li><a href="{summary["lang"]}/spotcheck.html">{summary["lang"]}</a> — {summary["samples"]} samples, {summary["ambiguous"]} ambiguous</li>' for summary in summaries)
    destination.joinpath("index.html").write_text(f"<!doctype html><meta charset=\"utf-8\"><title>Indic Smart Turn spot-checks</title><h1>Indic Smart Turn spot-checks</h1><p>Each page is self-contained and stores reviewer judgments in browser-local storage.</p><ul>{links}</ul>\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", nargs="+", help="Gemini-applied languages to sample; default: every compatible built parquet")
    parser.add_argument("--output", type=Path, default=DATA / "spotcheck")
    parser.add_argument("--test-count", type=int, default=15)
    parser.add_argument("--ambiguous-count", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.test_count < 1 or args.ambiguous_count < 0:
        parser.error("--test-count must be positive and --ambiguous-count must be non-negative")
    languages = args.langs or [path.stem for path in sorted((DATA / "built").glob("*.parquet"))]
    summaries = []
    for lang in languages:
        summary = write_language(lang, DATA / "built" / f"{lang}.parquet", args.output, args.test_count, args.ambiguous_count, args.seed)
        if summary:
            summaries.append(summary)
    if summaries:
        write_landing_page(args.output, summaries)


if __name__ == "__main__":
    main()
