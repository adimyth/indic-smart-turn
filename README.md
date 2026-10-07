# Indic Smart Turn

A [Pipecat Smart Turn v3](https://github.com/pipecat-ai/smart-turn) model for English plus eleven Indian languages, trained from Whisper weights. It drops into Pipecat's `LocalSmartTurnAnalyzerV3` in place of the Smart Turn Analyser v3.2 ONNX file, and into LiveKit through the same adapter.

## Motivation

Smart Turn listens to the user's raw audio and decides whether they have finished speaking or are pausing mid-thought. A fixed silence timeout forces you to choose between slow responses and interruptions; Smart Turn removes that trade-off. Smart Turn Analyser v3.2 supports 23 languages. Among Indian languages it covers Hindi, Marathi and Bengali, trained on data that is about 82% synthetic TTS. On real Tamil phone calls it scores 70% zero-shot ([TamilEOT](https://arxiv.org/abs/2609.05631)). South Indian languages, Gujarati and Punjabi are missing.

This project trains one Indic-focused model so a voice agent serving Indian users loads a single checkpoint instead of per-language files, and keeps English.

## Languages

| Code | Language | In Smart Turn Analyser v3.2? | Data here |
|---|---|---|---|
| eng | English | yes | Pipecat v3.2 (capped) |
| hin | Hindi | yes | IndicVoices + Pipecat v3.2 |
| mar | Marathi | yes | IndicVoices + Pipecat v3.2 |
| tam | Tamil | no | TamilEOT + IndicVoices |
| kan | Kannada | no | IndicVoices |
| mal | Malayalam | no | IndicVoices |
| guj | Gujarati | no | IndicVoices |
| pan | Punjabi | no | IndicVoices |
| tel | Telugu | no | IndicVoices |
| asm | Assamese | no | IndicVoices |
| ori | Odia | no | IndicVoices |
| ben | Bengali | yes | IndicVoices + Pipecat v3.2 |

## Data sources

| Source | License | What it contributes |
|---|---|---|
| [ai4bharat/IndicVoices](https://huggingface.co/datasets/ai4bharat/IndicVoices) | CC BY 4.0 | Real two-party phone conversations, one speaker per recording, split into transcript segments with human transcripts. We use the `Conversation` rows only. |
| [santhosh-005/tamil-eot](https://huggingface.co/datasets/santhosh-005/tamil-eot) | CC BY 4.0 | 18,485 human-validated turn boundaries from 116 Tamil calls (SPRING-INX), pre-cut as 8 s clips. |
| [pipecat-ai/smart-turn-data-v3.2](https://huggingface.co/datasets/pipecat-ai/smart-turn-data-v3.2-train) | CC BY 4.0 | The upstream training mix (mostly TTS) for English, Hindi and Marathi, so the model keeps English and the languages Smart Turn Analyser v3.2 already covers. |

> [!NOTE]
> IndicVoices weighs 30 to 50 GB per language, and only about 17% of it is conversational. `indic_turn/scan.py` reads the metadata columns of each parquet shard over HTTP with pyarrow column projection and picks the conversational rows. `indic_turn/build.py` then downloads only the shards that hold labelled rows, about 2 to 3 GB per language.

## How labels are generated

IndicVoices cuts segments at pauses, not at turn ends, so a segment end does not imply a turn end. Every built clip carries two labels.

### Audio label

`gemini-3.7-flash` hears one clip: the last 8 seconds of audio, ending where the speaker paused. We send the transcript of that clip when we have one, and the audio alone when we do not. Gemini answers complete or incomplete, with a confidence and a one-line reason.

The speaker paused after "market":

```
Audio:      last 8 s, ending at the pause
Transcript: I was going to the market
```

```json
{
    "verdict": "incomplete", 
    "confidence": 0.9, 
    "reason": "sentence still open"
}
```

### Text label

`gpt-6-luna` (`gpt-5.4` for Hindi and Telugu) gets one speaker's whole session in a single request. Every pause-split segment is one line, `[chunk] (duration) text`. We ask whether the speaker had finished at the end of each line. The model returns `1` (complete) or `0` (incomplete) and a confidence for every line. It uses the later lines to decide the earlier ones.

```
[1] (2.1s) I was going to the market
[2] (1.4s) to buy milk
[3] (0.8s) okay thanks
```

```json
{"labels": [[1, 0, 0.9], [2, 1, 0.9], [3, 1, 1.0]]}
```

Line 1 is incomplete because line 2 finishes the sentence. Line 2 is complete. Line 3 is complete because it is a short acknowledgement.

On a 600-clip validation run the text labels agreed with the audio label 89–90% of the time with matching complete rates; the disagreements are mostly prosody the text cannot see. Test clips where the two disagree are reported separately as "ambiguous".

### Pause-cuts

Extra incomplete examples come from cutting a segment at an internal pause ("pause-cut"), the spot where a VAD fires mid-turn in production. The full segment below pauses after "market". We send Gemini only the audio up to that pause, with no transcript.

```
Full segment: I was going to the market [pause] to buy milk
Audio sent:   I was going to the market [pause]
Transcript:   none
```

Only about half of such cuts sound incomplete when heard, so a pause-cut is kept only when the audio label says incomplete. Segments shorter than 1.5 s, almost all one-word acknowledgements, are capped at 20% of each language so they do not crowd out the hard mid-length cases.

## Technique

We keep the upstream Smart Turn v3 architecture and recipe: a Whisper encoder with the decoder discarded, 8 s of 16 kHz audio (the last 8 s, zero-padded at the front), attention pooling, a small MLP classifier, and BCE loss with per-batch positive weighting. We train from Whisper weights with upstream's `train.py` (vendored and patched in `train/`), export to ONNX fp32, and quantise to int8 with static calibration.

We train two sizes on identical data and compare them:

| Encoder | Params | int8 size | CPU latency (1 thread) |
|---|---|---|---|
| whisper-tiny | 8M | ~8 MB | ~80 ms |
| whisper-base | 20M | ~21 MB | ~140 ms |


## Verification

`reports/eval_<run>.md` reports per language, for Smart Turn Analyser v3.2 (cpu/gpu), the public Tamil model, and our tiny/base in fp32/int8:

- Accuracy and ROC-AUC with 95% bootstrap confidence intervals on the clean, speaker-disjoint test split, plus precision and recall of the incomplete class (the one that prevents interruptions).
- The ambiguous subset scored on its own, so label noise stays visible.
- Human-validated sets: TamilEOT test (paper baseline 83.7% tiny / 86.1% base) and Pipecat v3.2 test for English, Hindi and Marathi as a regression check against Smart Turn Analyser v3.2.
- A threshold sweep per language on dev, the int8 versus fp32 gap, and single-thread CPU latency.
- The highest-confidence errors dumped as audio for listening, and a spot-check page that records human agreement with the labels.
- A drop-in test with upstream `inference.py` and Pipecat's `LocalSmartTurnAnalyzerV3`.

Acceptance targets: at least 84% accuracy and 0.90 AUC on each Indic language, int8 within 1 point of fp32, English within 2 points of Smart Turn Analyser v3.2.

## How to use it

### Pipecat

Coming soon, once the model is trained.

### Directly the model

Coming soon, once the model is trained.
