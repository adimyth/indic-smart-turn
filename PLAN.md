# Implementation Plan: Indic Smart Turn

Stage-wise plan to train, with the Pipecat Smart Turn v3 recipe from Whisper weights, one model covering English and 11 Indian languages.

Languages: Hindi, Marathi, Tamil, Kannada, Malayalam, Gujarati, Punjabi, Telugu, plus Assamese, Odia and Bengali (added 2026-10-08; same IndicVoices pipeline, ISO codes `asm`, `ori`, `ben`, scripted in `scripts/add_language.sh`).

A coding agent executes it. Read `README.md` first for motivation, data sources and the technique.

- **Budget:** ≈ $0.50 OpenAI (text labels, spent), ≈ $30 Gemini (audio labels for every clip, approved), ≈ $3 RunPod (GPU). Gemini 3.7 Flash is $0.75 per 1M input tokens and $3.75 per 1M output tokens through 2026-12-31; audio costs about 32 tokens per second, so an 8 s clip plus a 250-token prompt is about 500 tokens.
- **Wall clock:** one day.
- **Credentials:** `.env` at repo root has:
  - `HF_TOKEN` (IndicVoices gated access accepted)
  - `OPENAI_API_KEY`
  - `GEMINI_API_KEY` (verified: `gemini-3.7-flash` accepts audio input)
  - `RUNPOD_API_KEY`

  Never print them.

---

## Current state of the repo

### `indic_turn/common.py`

Language map (IndicVoices config → ISO code), `parse_path()` for `<session>_<part>_chunk_<n>.flac`.

### `indic_turn/scan.py`

**Works.**

- Reads only metadata columns of IndicVoices parquet via `HfFileSystem` + pyarrow column projection (no audio download).
- Writes `data/index/<lang>.parquet` + `<lang>.shards.json`.
- Done for all 11 languages (`data/index/<lang>.parquet`).

### `indic_turn/label.py`

**Works.**

- One LLM request per recording session, JSON `[[chunk, 0/1, conf], ...]`, resumable via `data/labels/<lang>.jsonl`.
- Env: `LABEL_MODEL`, `LABEL_EFFORT`, `LABEL_OUT_SUFFIX`.
- Flags: `--limit-rows`, `--limit-sessions`, `--concurrency`.
- Default model `gpt-6-luna`; sends `reasoning_effort` for `gpt-5*`/`gpt-6*`, `temperature=0` otherwise.
- **Stage 1 is complete:** all 8 `data/labels/<lang>.jsonl` files exist (hin, tel from gpt-5.4; the rest from gpt-6-luna). Row counts: hin 5,009, mar 5,001, tam 3,013, kan 5,008, mal 5,016, guj 5,014, pan 5,010, tel 5,005.

### `indic_turn/build.py`

**Works** (tested on 144 Telugu chunks).

- Downloads only shards that hold labelled rows (`hf_hub_download` into `data/hf_cache`)
- builds:
  - 8 s windows
  - pause-cut negatives
  - speaker-disjoint `split` column
- writes `data/built/<lang>.parquet` (audio as WAV bytes struct, same columns as Pipecat's data + `speaker_id, session, chunk, split, llm_conf`).

### `indic_turn/eval.py`

Written; **untested at scale**.

- `--models name=path.onnx ...`
- `--data` parquet globs with `--split`
- `--hf repo:split[:langs]`
- per-language and per-dataset accuracy / AUC / precision+recall on "incomplete"
- CPU latency
- writes `.md` + `.json`

### `train/`

Vendored copy of upstream `references/smart-turn/{train.py,train_local.py,logger.py,benchmark.py,audio_utils.py}`; `train/train.py` carries the patches listed in Stage 4.

**Nobody has run it yet.**

### `scripts/pod_create.py`

**Works.** Creates/finds/terminates RunPod pod `indic-smart-turn` (A6000 → A40 → 4090 → L40 fallback), writes `.pod_ssh`. Flags `--stop`, `--terminate`.

### `scripts/pod_sync.sh`, `pod_ssh.sh`

**Work.** rsync code+labels to `/workspace/indic-turn`; run remote commands.

### `scripts/pod_setup.sh`

**Works** (deps verified: torch 2.8 cu128, torchcodec 0.7).

- Sources `.env`
- pip installs
- snapshot-downloads v3.2 train/test + TamilEOT
- copies baseline ONNX files to `models/`

### `scripts/pod_pipeline.sh`

Written, not run. build → train → quantize → eval.

### `scripts/label_all.sh`, `scripts/calib_hindi.sh`, `indic_turn/label_report.py`

`label_all.sh` ran to completion. `label_report.py` prints the Stage 1 table with the 80–92% gate. `calib_hindi.sh` is ready for Stage 2.

### `references/`

Upstream clones: `smart-turn` (Pipecat), `tamil-eot` (TamilEOT recipe, prompt in `src/tamileot/labelling.py`). Read-only.

### `data/preview/*.wav`

A few built Telugu samples for listening.

### Local tooling

`uv` project (`pyproject.toml`); run anything with `uv run python -m indic_turn.<module>`. Python 3.12.

---

## Stage 1: Labeler fixes and remaining labels (local, ~45 min, ≈ $0.60)

**Goal:** `data/labels/<lang>.jsonl` complete for all 11 languages.

1. `indic_turn/label.py`
   - Default `MODEL = os.environ.get("LABEL_MODEL", "gpt-6-luna")`.
   - Request kwargs:
     - `{"reasoning_effort": LABEL_EFFORT or "low"}` when the model name starts with `gpt-5` **or** `gpt-6`
     - else `{"temperature": 0}`
   - The second-opinion pass moves to Stage 3 and uses Gemini with audio (see below), so no text-only second pass is needed here.
2. `scripts/label_all.sh`
   - Scan `malayalam gujarati punjabi` first:

     ```bash
     uv run python -m indic_turn.scan --langs malayalam gujarati punjabi --target-rows 10000 --max-shards 12
     ```

   - Primary pass (gpt-6-luna), `--limit-rows`:
     - `mar kan mal guj pan` 5000
     - `tam` 3000
     - skip `hin` and `tel`, which gpt-5.4 covered.
   - Run in background with `nohup`, log to `data/label.log`.
3. **Check:**
   - every `<lang>.jsonl` has ≥ 4,800 rows (tam ≥ 2,900)
   - complete rate 80–92% (short acknowledgement-heavy languages may sit above the general baseline; inspect the report's ≥4 s rate alongside it)
   - Agreement with the Gemini audio pass is checked in Stage 3.

Reference measurement on 179 Telugu chunks: gpt-6-luna agreed with gpt-5.4 on 95.5% and with the 3-model majority on 99.4%, at about 60 input and 30 output tokens per chunk.

## Stage 2: Baselines and evaluation-code validation (done)

**Original goal and why it was replaced.** The first version of this stage used Smart Turn v3.2 as a judge of our Hindi labels, with a gate of complete-recall ≥ 0.85 and AUC ≥ 0.80. The gate failed (AUC 0.63), and the investigation showed the gate was built on a false assumption: Smart Turn v3.2's published 92.8% Hindi accuracy is on its own synthetic TTS test set, and the model is weak on real Hindi phone audio. Evidence:

- Our evaluation code reproduces the TamilEOT paper on its human-validated test set to within 0.1 point: Smart Turn v3.2 cpu 70.2% / AUC 0.749 (paper 70.30 / 0.751) and the public Tamil base model 86.1% / AUC 0.922 (paper 86.13). `reports/tamileot_test_stock.md`. So the numbers are trustworthy.
- Smart Turn v3.2 v3.2 on our Hindi test rows: AUC 0.61–0.64 overall, 0.49 on segments under 1.5 s (one-word acknowledgements), 0.73 on 1.5–4 s, 0.67 on 4 s+. Audio-construction ablations (segment only, no trailing trim, longer trailing silence, no context) move the operating point but not the AUC, so construction is not the cause.
- Reading the model's confident disagreements with our labels in Hindi: segments labelled complete that the model scores below 0.05 are finished questions and statements ("कब से आपको दिक्कत आ रहा है पैर का", "अच्छा नवरात्रि में व्रत हैं क्या", "नमस्ते भैया मैं टोयोटा एजेंसी से बात कर रहा हूँ बोलिए"). The labels are right; the model is wrong on real Hindi.

**Gate (passes):** `eval.py` reproduces the TamilEOT published numbers within 1 point. Label quality is validated by the Gemini audio pass in Stage 3, not by Smart Turn v3.2.

**Recorded baselines to beat** (Smart Turn v3.2 cpu): Hindi IndicVoices test AUC 0.63, accuracy 63%; TamilEOT test 70.2% / 0.749. `reports/calib_hindi_stock.md`, `reports/tamileot_test_stock.md`.

## Stage 3: Build, Gemini audio labels, spot-check page (local, in progress)

**What the validation run showed** (`data/labels/_validation_run/`, 300 segments + 60 pause-cuts each for Hindi and Kannada, gemini-3.7-flash with audio + transcript): text labels agree with the audio verdict 88.9% (Hindi, gpt-5.4) and 89.7% (Kannada, gpt-6-luna), with matching complete rates, so neither text labeler is biased. Where they disagree the audio verdict is usually right, because the text labeler cannot hear prosody ("भइयू से" labelled complete from text, cut off when heard). The serious finding: only 53% (Hindi) and 45% (Kannada) of the 60 sampled **pause-cut** clips per language were incomplete when heard; the full run later confirmed the range at 39% to 50% across all eleven languages (`reports/label_agreement.md`). A pause inside a segment is often a natural stopping point. TamilEOT found the same (44%) for rule-based negatives. Decision (approved): **Gemini audio is the primary label for every clip; the text label is kept as the second opinion.**

1. `indic_turn/build.py` (done): `--short-cap 0.2` downsamples segments under 1.5 s to at most 20% of a language's labelled chunks (deterministic, seeded), and `--pausecut-frac 1.0` creates a pause-cut candidate for every segment ≥ 2 s with an internal pause. Build all 11 languages: `scripts/audio_label_all.sh` does build + labelling per language.
2. `indic_turn/label_audio.py` (done): sends each built clip (WAV bytes) plus its transcript (none for pause-cuts) to `gemini-3.7-flash`, JSON response, `thinkingLevel: low`, temperature 0, 24 workers, resumable. Cache `data/labels/<lang>.audio.jsonl`, keyed by `session|chunk|dataset|md5(audio)[:10]` so a rebuilt pause-cut never reuses a stale verdict. Measured cost: about 490 input + 40 output tokens per clip, about $0.0005; all languages about $30.
3. `indic_turn/build.py --apply-audio-labels` (to implement): rewrite `data/built/<lang>.parquet` with
   - `endpoint_bool` = Gemini verdict (primary); `text_label` = the original text/LLM label; `audio_conf`, `audio_reason`; `ambiguous` = (verdict ≠ text_label) for original segments.
   - Pause-cut rows: keep only those Gemini judged `incomplete` with confidence ≥ 0.7 (`endpoint_bool=False`); drop the rest. They have no text label; `ambiguous=False`.
   - Test rows with `ambiguous=True` move to `split="test_ambiguous"`. Train and dev keep every row with the audio label.
   - Rows whose Gemini call errored (`verdict="error"`) are dropped; report the count.
   - Print per language: segments, pause-cuts kept/dropped, final positive rate (expect roughly 55–65%), split sizes, text-vs-audio agreement.
   - Write `reports/label_agreement.md` from `scripts/audio_agreement.py` output.
4. Spot-check page: new `indic_turn/spotcheck.py` that samples 15 built clips per language (balanced labels, test split, plus 5 ambiguous) into `data/spotcheck/<lang>/*.wav` + `index.json` (transcript, audio label, text label, Gemini reason); publish as a single-file HTML artifact (mp3 via ffmpeg to keep it under 16 MB, or one page per language) with "agree / disagree" buttons writing to the artifact DB (load `artifact-capabilities` skill). The user's judgments feed verification item 9. This page does not gate training.

## Stage 4: Pod bring-up and training smoke test (~30 min, ≈ $0.30)

1. `uv run python scripts/pod_create.py` → `.pod_ssh`. Then `scripts/pod_sync.sh` and:

   ```bash
   scripts/pod_ssh.sh "cd /workspace/indic-turn && nohup bash scripts/pod_setup.sh > logs_setup.log 2>&1 &"
   ```

   Wait for `SETUP DONE`:

   - downloads ~43 GB
   - /workspace is a network volume, 140 GB free
   - 96 vCPU, 500 GB RAM, A40 48 GB
2. Review these patch points in `train/train.py` before running:
   - `CONFIG`:
     - `base_model_name` from `BASE_MODEL` env (default `openai/whisper-base`)
     - `indic_parquets` = `data/built/<lang>.parquet` for 10 langs
     - `v32_train/test`
     - `v32_eng_cap` (40000)
     - `tamil_eot`
     - `indic_repeat` (2)
     - `LR`
     - `EPOCHS`
     - `BATCH` (128)
     - `EVAL_STEPS` (1000)
   - `load_indic()` / `load_tamil_eot()` / `load_v32()` / `prepare_datasets_ondemand()` replace the upstream loader.
   - `_std()` keeps `audio, endpoint_bool, language, dataset, midfiller, endfiller` and casts audio to 16 kHz.
   - Make `load_indic()` use `split in ("train")` for training and `"dev"` for eval, and expose `test` and `test_ambiguous` separately.
   - wandb runs `mode="disabled"` without `WANDB_API_KEY`; `bf16=True` on CUDA; `load_best_model_at_end=True` on `eval_f1`.
   - Known risks:
     - datasets 4.4 returns an `AudioDecoder` for `sample["audio"]`; upstream indexes `["array"]` on it, which works once torchcodec is installed.
     - `ExternalEvaluationCallback` evaluates all test sets every `EVAL_STEPS`; keep test sets ≤ ~15k rows total or raise `EVAL_STEPS`.
3. **Smoke test** on the pod. Every manual command on the pod needs the same environment `pod_pipeline.sh` sets, or the trainer looks for `./data` relative to `train/` and finds nothing:

   ```bash
   cd /workspace/indic-turn && set -a && . .env && set +a
   export HF_HOME=/workspace/hf INDIC_TURN_DATA=/workspace/indic-turn/data PYTHONPATH=/workspace/indic-turn
   python -m indic_turn.build --langs hin tel --pausecut-frac 0.8
   cd train && EPOCHS=0.02 BATCH=32 EVAL_STEPS=20 V32_ENG_CAP=2000 python train_local.py --training-run-name smoke --output-dir /workspace/indic-turn/output
   ```

   `V32_ENG_CAP=2000` keeps the smoke run short; the v3.2 filter over 270k rows still takes a few minutes the first time. Before the smoke test, cap the v3.2 test set used inside training to 3,000 rows in `load_v32()` (`te = te.shuffle(seed=42).select(range(min(3000, len(te))))`); the full v3.2 test is scored by `eval.py` in Stage 6, and the in-training callback only needs a trend.

   The run must finish with `exports/model_fp32.onnx`, and `python train_local.py --quantize <fp32>` must then produce `model_int8_static_calib1024.onnx`. Fix whatever breaks before Stage 5.

## Stage 5: Build all languages and train both sizes (~3.5 h, ≈ $2)

1. `scripts/pod_sync.sh` (ships all labels) then on the pod: `scripts/pod_pipeline.sh` runs `build` for all 11 languages:
   - about 18 GB of shards
   - expect about 7.5k samples per language, Tamil about 4.5k
2. Run the two trainings one after the other with `pod_pipeline.sh <run_name>` and these env vars:
   - `BASE_MODEL=openai/whisper-base` → run `indic-base` (expect ~1.5 h)
   - `BASE_MODEL=openai/whisper-tiny` → run `indic-tiny` (expect ~1 h)

   Hyperparameters:

   - 4 epochs
   - batch 128
   - lr 5e-5
   - warmup 0.2
   - cosine
   - weight decay 0.01
   - BCE with per-batch `pos_weight` (upstream)

   Save `models/<run>/indic-smart-turn-{fp32,int8}.onnx`.
3. Log training to `logs/train_<run>.log`; use `scripts/pod_pull.sh <run>` to copy `output/<run>/final_model/` (the complete PyTorch checkpoint, including `exports/*.onnx`) and `reports/` back with rsync.

## Stage 6: Evaluation (~20 min on the pod)

Run `indic_turn.eval` with:

- **models:**
  - `smartturn_v3.2_cpu`
  - `smartturn_v3.2_gpu`
  - `tamil_base_int8`
  - `base_fp32`
  - `base_int8`
  - `tiny_fp32`
  - `tiny_int8`
- **data:**
  - `data/built/*.parquet --split test`
  - again with `--split test_ambiguous`
  - plus `--hf santhosh-005/tamil-eot:test`
  - and `--hf pipecat-ai/smart-turn-data-v3.2-test:train:eng,hin,mar,ben` (the v3.2 test repo has a single split named `train`; this is the upstream convention, not an error)

Extend `eval.py` with:

- 95% bootstrap CIs on accuracy and AUC (1,000 resamples) per language.
- Threshold sweep on `dev` per language; report threshold maximising balanced accuracy, alongside 0.5.
- `--dump-errors N`: write the N highest-confidence errors per language as wav + transcript to `reports/errors/<run>/<lang>/` (feeds the spot-check page).

Write `reports/eval_<run>.md` (+ `.json`). Then `scripts/pod_create.py --terminate`.

**Acceptance targets** (clean test split):

- accuracy ≥ 84% and AUC ≥ 0.90 on every Indic language
- int8 within 1 point of fp32
- v3.2 English ≤ 2 points below Smart Turn v3.2
- TamilEOT test ≥ 84% (paper: 83.7 tiny / 86.1 base)

Choose the shipped model as follows:

- if both meet all targets, ship `base`
- if only `tiny` meets a latency need under 100 ms CPU and lands within 2 points, ship both and say so in the report.

## Stage 7: Drop-in and integration check (local, ~15 min)

1. `references/smart-turn/inference.py` with `ONNX_MODEL_PATH` pointed at `models/<run>/indic-smart-turn-int8.onnx` on `data/preview/*.wav` → probabilities equal `eval.py`'s within 1e-3.
2. Pipecat:
   - `pip install pipecat-ai[local-smart-turn-v3]`
   - instantiate `LocalSmartTurnAnalyzerV3(smart_turn_model_path=...)`
   - run `analyze_end_of_turn` on the same wavs
   - confirm it loads and agrees.

## Stage 8: Publish to Hugging Face (after the user has seen the report and spot-check)

1. Model repo `adimyth/indic-smart-turn` (rename if you prefer):
   - `indic-smart-turn-base-{fp32,int8}.onnx`
   - `indic-smart-turn-tiny-{fp32,int8}.onnx`
   - `config.json` (input shape (N,80,800), output prob, threshold)
   - model card:
     - languages
     - per-language results table from Stage 6
     - data sources with licenses (IndicVoices CC BY 4.0, TamilEOT CC BY 4.0, Pipecat smart-turn-data-v3.2 CC BY 4.0)
     - labeling method
     - Pipecat usage snippet
     - BSD-2 license (matches upstream)
2. Dataset repo `adimyth/indic-smart-turn-data`:
   - `data/built/*.parquet` with a README (schema, splits, how labels were produced, CC BY 4.0, attribution to AI4Bharat and SPRING Lab via TamilEOT)
   - Upload via `huggingface_hub.upload_folder`.
3. Add a `scripts/publish.py` that does both from local files.

## Stage 9: Production-call test set and domain adaptation (local; test-set labelling approved)

Source: `data/private/additional-data.csv`, 1,618 roleplay sessions (`language, audio_file`), each an MP4 with one mono 16 kHz AAC track where a fixed TTS agent and a trainee are mixed. Verified on 7 sessions (`scripts/analyze_call.py`, `scripts/sample_calls.sh`): speaker clustering separates the two voices cleanly; the agent voice is identical across sessions and always speaks first; the agent replies 2–4.5 s after the trainee stops.

### 9.1 Extraction (local, ~2 h with 4 parallel downloads)

1. Download each MP4, decode to 16 kHz mono WAV, delete the MP4. Keep WAVs under `data/private/raw/` (about 25 GB).
2. Silero VAD on the mixed track (min silence 200 ms, min speech 150 ms, pad 60 ms).
3. Speaker embeddings (resemblyzer) per segment ≥ 0.4 s, two-cluster cosine k-means with 10 restarts.
4. **Agent identification:** the cluster closest to the stored agent-voice reference `data/private/agent_reference.npy` (built from the first session). The first speaker of a session must be the same cluster. If the two checks disagree, or the reference similarity margin is below 0.1, or the trainee speaks less than 30 s in total, **quarantine the session** (counted, not used).
5. Candidate boundary = every end of a trainee segment except the last in the session. For each record: pause length, `gap_user` (time until the trainee speaks again), `gap_agent` (time until the agent speaks), position in the turn.
6. **Rule label** (behavioural, from the recording itself):
   - `complete`: agent starts within 5 s and the trainee does not resume before the agent.
   - `incomplete`: trainee resumes within 2 s and no agent speech before that. The 2 s bracket is kept deliberately: trainees speaking a second language pause longer while thinking.
   - otherwise `ambiguous` (overlap, or silence from both): dropped.
7. Clip = last 8 s of trainee-only audio (agent regions zeroed) ending 0.2 s after the pause, same as `build.py`. Write `data/private/<lang>.parquet` with the public schema plus `call_id` (salted hash, path not stored), `pause_s`, `gap_user`, `gap_agent`, `rule_label`. Split 70/30 by `call_id` into `train` and `test`.
8. Print per language: sessions used/quarantined, boundaries, complete/incomplete/dropped, agent-latency distribution, pause-length distribution. No file names, no transcripts (no STT is run on this data).

### 9.2 Gemini second opinion and the four-category test set

**What the labels showed** (Hindi, English, Bengali, Gujarati, full sets): the recording rule and Gemini's audio verdict agree on only 63 to 67% of clips, and the disagreement has a clear structure, measured on `data/private/labels/<lang>.audio.jsonl` joined to the parquet:

- Rule = incomplete, Gemini = complete (about 35% of mid-monologue pauses): the trainee paused at the end of a grammatically complete sentence with falling pitch and then continued, usually within 0.3 s. From the audio alone the turn sounds finished; from the recording it was not. The base model sides with Gemini on 81% of these.
- Rule = complete, Gemini = incomplete: strongly tied to how fast the agent answered. When the agent replied within 2 s, Gemini calls only 40 to 48% of those pauses complete ("abrupt cut off mid-sentence"); when it took 3.5 to 5 s, 82 to 89%. The current agent's fast replies are often interruptions.
- Pause length is the strongest single signal: pauses of 1 s or more are 71 to 76% complete by both labelers; pauses under 1 s are 7 to 10% complete by the rule but 31 to 37% by Gemini.

"Agree-only" would keep two thirds of the clips and hide exactly the cases that matter, so the test set is split into four categories instead of filtered:

| Category | Definition | What it measures | Metric |
|---|---|---|---|
| A, clear turn end | rule complete and Gemini complete | the agent should answer now | recall (answer promptly) |
| B, unfinished pause | rule incomplete and Gemini incomplete | the agent must stay quiet | specificity (do not interrupt) |
| C, sentence-final pause inside a monologue | rule incomplete and Gemini complete | the hard case: sounds done, trainee continues | interrupt rate at 0.5, and at higher thresholds |
| D, agent interruption | rule complete and Gemini incomplete | the current agent spoke over an unfinished sentence | reported as a finding about the agent; excluded from model scoring |

Labelling: all rows, train and test, all ten languages (approved; about $35). Train rows keep category A as complete and B as incomplete; C and D are dropped from training.

Report per language (`reports/private_baseline.md`), for Smart Turn v3.2 int8, base fp32, base int8 dynamic, tiny int8:

1. Category sizes and share of the test clips.
2. A recall, B specificity, C interrupt rate, each with 95% CIs, at threshold 0.5.
3. The same metrics by pause length (0.2–0.5 s, 0.5–1 s, 1 s and over), since production can choose not to consult the model on the shortest pauses.
4. A policy sweep: for thresholds 0.5, 0.7, 0.9 and minimum pause 0.2, 0.5, 1.0 s, the resulting C interrupt rate and A recall, so the deployment can pick its own trade-off between interrupting a pitch and answering late.
5. The agent-interruption finding: share of the agent's replies that fall in category D, by agent latency bin.
6. Public-test numbers alongside, for reference.

Odia is reported as indicative only (2 sessions); Kannada as low-count. The quarantine rate per language is stated as a limitation.

### 9.3 Human spot-check

`indic_turn/spotcheck.py --source data/private` writes 20 clean and 10 ambiguous test clips per language to a local page (no upload). The user's agreement rate is recorded in the report.

### 9.4 Evaluation and optional adaptation

- `indic_turn.eval` on `data/private/*.parquet --split test` (and `test_ambiguous`) for Smart Turn v3.2, ours base, ours tiny. Report per class (recall on `incomplete` = not interrupting mid-pitch, recall on `complete` = answering promptly), plus the subset of pauses ≥ 0.5 s, plus bootstrap CIs. Plain accuracy is not a target here: the set is roughly 90% incomplete.
- `scripts/finetune_local.py` as before: continue from the Stage 5 checkpoint on the private train split mixed 1:1 with public data, 1–2 epochs, lr 1e-5; ship only if it beats the Stage 5 model on the private test and stays within 1 point on the public test.

Known limits, stated in the report: completes reflect the agent's decisions; sessions with a near-silent trainee are excluded; this is roleplay audio (long trainee monologues), so real customer calls may differ in rhythm.

## Verification checklist

- [ ] `data/labels/*.jsonl` and `*.audio.jsonl` complete; text-vs-audio agreement table in `reports/label_agreement.md`; built parquet carries both labels.
- [x] Stage 2: `eval.py` reproduces TamilEOT published numbers; Smart Turn v3.2 baselines recorded in `reports/`.
- [x] Smoke-test run exported fp32 + int8 ONNX (Stage 4).
- [x] `reports/eval_all_test.md`, `reports/eval_all_test_ambiguous.md`, `reports/eval_base_int8_variants.md`, `reports/thresholds.md`, summarised in `reports/STAGE6_REPORT.md`.
- [x] `reports/STAGE6_REPORT.md` states targets, results and the shipping recommendation (base dynamic int8 default; base fp32 on Apple Silicon/GPU; tiny int8 for constrained CPUs).
- [x] Drop-in check passed (Stage 7): upstream `inference.py` and Pipecat `LocalSmartTurnAnalyzerV3` agree with `eval.py` to 3 decimals.
- [ ] Spot-check page published; the report records the user's agreement rate.
- [ ] Hugging Face model + dataset repos published; `README.md` links them.
- [ ] Pod terminated; final spend noted in the report.
- [ ] (Stage 9, optional) private extraction counts printed, adapted model compared on private and public test, nothing from `data/private/` leaves the machine.
