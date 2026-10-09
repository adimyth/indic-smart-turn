# How Indic Smart Turn was built

This is the record of the work, stage by stage: what each stage set out to do, what it found, and what came out of it. The README describes the finished model; this file describes the path to it.

## 1. Finding and labelling the data

**Goal.** Real conversational speech in eleven Indian languages, with a label at every pause saying whether the speaker had finished.

**What was done.**

- IndicVoices (AI4Bharat) holds real two-person phone calls, one speaker per recording, cut into transcript segments. The full set is 30 to 50 GB per language, and only about 17% of it is conversational. Instead of downloading it, the metadata columns of each parquet shard were read over HTTP, the conversational rows picked out, and only the shards holding them fetched: 2 to 3 GB per language.
- Each segment end was labelled twice. A text model (`gpt-6-luna`; `gpt-5.4` for the first two languages) read the ordered transcript of a whole session and marked every segment end complete or incomplete. Then `gemini-3.7-flash` listened to each 8-second clip and gave its own verdict. The audio verdict is the primary label; the text label is kept as a second opinion.
- Extra incomplete examples were made by cutting a segment at an internal pause, the moment a voice-activity detector would fire mid-turn in production.
- Three languages, Assamese, Odia and Bengali, were added part-way through with the same pipeline.

**What was found.**

- Text and audio labels agree 89 to 93% of the time per language. The disagreements are mostly prosody the text cannot show.
- Pause-cut negatives were a trap: only 39 to 50% of them sound incomplete when heard, because a pause inside a segment is often a natural stopping point. They are kept only when the audio label says incomplete.
- Short one-word acknowledgements dominated some languages and were capped at 20% of each language's clips.

**Outcome.** 50,421 clips across eleven languages, split by speaker into train, dev and test, with the test clips where the two labels disagree held out as "ambiguous". Published as `adimyth/indic-smart-turn-data`.

## 2. Checking the measuring stick

**Goal.** Know that the evaluation code is right before trusting any number from it.

**What was done.** Pipecat's Smart Turn v3.2 and the public TamilEOT model were scored on the human-validated TamilEOT test set with this repository's evaluator.

**What was found.** Both published results were reproduced to within 0.1 point: 70.4% / AUC 0.743 against the paper's 70.3 / 0.751, and 86.1% / 0.922 against 86.13. A second check that had been planned, using Smart Turn v3.2 as a judge of the Hindi labels, turned out to be invalid: v3.2's published Hindi accuracy comes from its own synthetic test set, and on real Hindi calls it scores an AUC of 0.63, so it cannot judge anything. That finding became part of the case for the project.

## 3. Training

**Goal.** One model for English plus the eleven languages, in a size that runs on a CPU.

**What was done.** The Smart Turn v3 recipe was followed from Whisper weights: encoder only, attention pooling, a small classifier head, trained on the last 8 seconds of audio before each pause. Two sizes, whisper-base and whisper-tiny, on the same mix: the Indic clips oversampled twice, the TamilEOT training split, and Pipecat's own data for English, Hindi, Marathi and Bengali so those languages do not regress. Four epochs on one RTX A6000: 19 minutes for base, 24 for tiny.

**What went wrong and was fixed.**

- The first int8 export was the same size as fp32. The legacy ONNX exporter had stored the weights as constant nodes, which the quantiser skips. Constant folding at export fixed it.
- Static int8 calibration cost the base model 4 to 9 points of accuracy. Dynamic (weights-only) int8 kept its AUC within 0.005 of fp32, so that is what ships for base. Tiny keeps static int8.
- The first evaluation run took hours because every model ran on a single thread and features were recomputed per model. Sharing features and using more threads brought it under an hour.

## 4. Evaluation on the public test set

**Goal.** A like-for-like comparison with Smart Turn v3.2, and a check against the acceptance targets set at the start.

**What was done.** Seven models were scored on the same 20,431 test clips: Smart Turn v3.2 in its int8 and fp32 files, the public Tamil model, and our base and tiny in both precisions. Each group in the README pairs our model with the v3.2 file of the same precision, since v3.2 only exists at tiny size.

**What was found.**

- Base fp32 is ahead of Smart Turn v3.2 in every language, by 2 points on English and 5 to 18 on the Indian languages, and matches the published TamilEOT result.
- Tiny int8, the same size and speed as v3.2's shipped file, is ahead in eleven of twelve languages.
- Smart Turn v3.2's int8 file outscores its own fp32 file on accuracy in eleven languages while their AUC is nearly equal. That is a threshold effect, not a quality difference, and the README explains it so readers do not stumble on it.
- Per-language thresholds tuned on the dev splits did not transfer to the test splits; the dev sets are too small. The default 0.5 was kept.
- Of the original targets, two were missed narrowly: 84% accuracy in every language (Assamese at 83.6) and AUC 0.90 in every language (three languages short). Both are stated in the README.

## 5. Integration check and release

Pipecat's `LocalSmartTurnAnalyzerV3` loads the files and returns the same probabilities as the evaluator to three decimals; the upstream `inference.py` does the same. Published to `adimyth/indic-smart-turn` with the model card, charts and reports.

## 6. Testing on production calls

**Goal.** Numbers on the audio the model would actually face: 1,618 roleplay sessions from a voice-agent product, each a trainee and a TTS agent mixed into one mono track.

**What was done.**

- Trainee and agent were separated by voice, using the fact that the agent voice is the same in every session. Sessions where the two could not be separated with confidence, about a quarter, were left out. A check on the kept clips found no agent voice in them.
- Every trainee pause of 200 ms or more became a clip, cut exactly as the training data. The recording itself gave a first label: the agent replied, or the trainee carried on. Gemini then listened to the clips and gave the second label, so the production test could be scored the same way as the public one. Labelling was capped for cost, so for five languages the scored clips are the earliest sessions in each file rather than a random sample.
- The production data stays on the operator's machine. It was copied once, over SSH, to a rented GPU for the fine-tune in stage 7 and deleted with that machine. It is not published in any form.

**What was found.**

- On 12,710 labelled test clips, Indic Smart Turn base int8 scores 77.1% / AUC 0.859 against 66.6% / 0.771 for Smart Turn v3.2, ahead in every language by 8 to 18 points. Tiny int8 is ahead by 4 to 12 points.
- Everything scores lower than on the public set because a sales pitch is full of mid-sentence and sentence-final pauses. About a third of all pauses are sentence ends where the speaker continues within a fraction of a second; no audio-only model separates those from real turn ends. For this kind of speech the practical fix is a longer minimum pause in front of the model, and the report gives the trade-off per setting.

## 7. Fine-tuning on production data

**Goal.** Adapt the base model to the production audio without losing what it learned from the public data.

**What was done.** Training continued from the stage 3 checkpoint for one pass over 48,649 clips: the 20,649 production clips on which the recording and Gemini agree, mixed one-to-one with 20,000 public Indic clips plus small English and TamilEOT samples, at a learning rate five times lower than the original. The tuned model's probabilities sit lower across the board, so its best decision line, chosen on the production training split only, was 0.13. That shift was baked into the exported graph as a constant before the final sigmoid, so the shipped file works at the usual 0.5 and the ranking of clips is unchanged.

**What was found.** Int8, accuracy / AUC: production calls 80.0 / 0.876 against 78.0 / 0.855 before tuning; public test 90.0 / 0.957 against 88.6 / 0.953. Ahead in eleven of twelve public languages. The tuned files replaced the originals on Hugging Face, with the originals kept under a `-v1` suffix.

## Costs

| Item | Spend |
|---|---|
| Text labels, public data (OpenAI) | about $6.50 |
| Audio labels, public data (Gemini) | about $29 |
| Audio labels, production calls (Gemini) | about $25 |
| GPU time (RunPod), all stages | about $4 |

## Rules kept throughout

- Nothing that cost money ran before the step before it had passed and the spend was approved.
- Every number in the README comes from a report in `reports/`, produced by code in this repository.
- The production data is never committed, uploaded anywhere, or sent to a third-party API beyond the Gemini labelling approved for it.
