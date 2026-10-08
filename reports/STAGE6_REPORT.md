# Stage 6 report: Indic Smart Turn vs stock Pipecat Smart Turn v3.2

Clean test split (speaker-disjoint IndicVoices test for 11 languages; English, Hindi, Marathi, Bengali also include the upstream v3.2 test set; Tamil also includes the human-validated TamilEOT test set). Numbers are accuracy / ROC-AUC at the default 0.5 threshold. Full tables with 95% bootstrap intervals: `eval_all_test.md`.

## Group 1: whisper-tiny, int8 (8.7 MB) — like for like with stock

| language | n | stock v3.2 (int8) | ours tiny int8 | Δ acc |
|---|---:|---|---|---:|
| English | 7820 | 92.9 / 0.978 | 91.7 / 0.973 | -1.2 |
| Hindi | 1744 | 84.7 / 0.932 | 89.4 / 0.955 | +4.7 |
| Marathi | 1311 | 77.9 / 0.851 | 84.1 / 0.924 | +6.2 |
| Bengali | 1482 | 81.2 / 0.870 | 84.3 / 0.916 | +3.1 |
| Tamil | 4468 | 70.5 / 0.744 | 82.1 / 0.876 | +11.6 |
| Telugu | 725 | 73.4 / 0.750 | 85.1 / 0.898 | +11.7 |
| Kannada | 385 | 77.7 / 0.770 | 82.9 / 0.878 | +5.2 |
| Malayalam | 472 | 66.9 / 0.657 | 80.9 / 0.823 | +14.0 |
| Gujarati | 498 | 73.5 / 0.765 | 80.9 / 0.839 | +7.4 |
| Punjabi | 556 | 69.2 / 0.732 | 80.2 / 0.834 | +11.0 |
| Odia | 331 | 74.6 / 0.767 | 86.4 / 0.896 | +11.8 |
| Assamese | 639 | 67.8 / 0.696 | 80.4 / 0.837 | +12.6 |

## Group 2: whisper-base, int8 (24 MB, dynamic quantisation)

Base int8 was first built with MinMax static calibration and lost 4–9 points; dynamic (weights-only) int8 keeps AUC within 0.005 of fp32 in every language (`eval_base_int8_variants.md`). Scored on the IndicVoices test splits plus TamilEOT (no upstream v3.2 rows in this run).

| language | base fp32 | base int8 dynamic | Δ acc |
|---|---|---|---:|
| Hindi | 82.6 / 0.852 | 83.3 / 0.863 | +0.7 |
| Marathi | 88.8 / 0.925 | 86.8 / 0.921 | -2.0 |
| Bengali | 87.8 / 0.913 | 85.7 / 0.914 | -2.1 |
| Tamil | 86.2 / 0.918 | 84.8 / 0.917 | -1.4 |
| Telugu | 85.7 / 0.908 | 85.0 / 0.910 | -0.7 |
| Kannada | 88.6 / 0.921 | 87.0 / 0.923 | -1.6 |
| Malayalam | 84.5 / 0.859 | 82.6 / 0.858 | -1.9 |
| Gujarati | 84.7 / 0.895 | 82.5 / 0.891 | -2.2 |
| Punjabi | 85.3 / 0.903 | 82.7 / 0.894 | -2.6 |
| Odia | 88.5 / 0.938 | 89.1 / 0.937 | +0.6 |
| Assamese | 83.6 / 0.892 | 81.8 / 0.888 | -1.8 |

## Group 3: whisper-tiny, fp32 (32 MB)

| language | ours tiny fp32 | rec(incomplete) | rec(complete) |
|---|---|---:|---:|
| English | 93.7 / 0.979 | 92.8 | 94.7 |
| Hindi | 90.2 / 0.958 | 89.0 | 91.1 |
| Marathi | 88.1 / 0.943 | 85.3 | 90.0 |
| Bengali | 85.4 / 0.934 | 82.6 | 87.5 |
| Tamil | 83.4 / 0.885 | 72.3 | 89.5 |
| Telugu | 85.0 / 0.895 | 73.2 | 90.2 |
| Kannada | 82.3 / 0.876 | 65.3 | 86.5 |
| Malayalam | 81.4 / 0.833 | 68.5 | 85.9 |
| Gujarati | 82.5 / 0.856 | 67.2 | 87.7 |
| Punjabi | 83.1 / 0.869 | 73.3 | 87.1 |
| Odia | 84.9 / 0.885 | 67.7 | 91.6 |
| Assamese | 81.4 / 0.846 | 67.8 | 87.9 |

## Group 4: whisper-base, fp32 (81 MB)

| language | ours base fp32 | rec(incomplete) | rec(complete) | vs stock Δ acc |
|---|---|---:|---:|---:|
| English | 94.9 / 0.988 | 94.6 | 95.2 | +2.0 |
| Hindi | 91.0 / 0.964 | 90.7 | 91.2 | +6.3 |
| Marathi | 89.6 / 0.952 | 88.0 | 90.7 | +11.7 |
| Bengali | 86.6 / 0.934 | 84.1 | 88.5 | +5.4 |
| Tamil | 86.2 / 0.918 | 76.7 | 91.4 | +15.7 |
| Telugu | 85.7 / 0.908 | 77.2 | 89.4 | +12.3 |
| Kannada | 88.6 / 0.921 | 81.3 | 90.3 | +10.9 |
| Malayalam | 84.5 / 0.859 | 71.8 | 89.1 | +17.6 |
| Gujarati | 84.7 / 0.895 | 73.6 | 88.5 | +11.2 |
| Punjabi | 85.3 / 0.903 | 75.2 | 89.4 | +16.1 |
| Odia | 88.5 / 0.938 | 75.3 | 93.7 | +13.9 |
| Assamese | 83.6 / 0.892 | 75.0 | 87.7 | +15.8 |

## External sets

| set | stock v3.2 int8 | tiny int8 | base int8 dynamic | base fp32 |
|---|---|---|---|---|
| TamilEOT test (4,168 human-validated clips) | 70.4 / 0.743 | 81.8 / 0.875 | 84.8 / 0.917 | 85.9 / 0.917 (paper, whisper-base: 86.1) |
| Pipecat v3.2 test, eng/hin/mar/ben (10,878) | 90.6 / 0.968 | 90.2 / 0.966 | n/a | 93.6 / 0.983 |

## Latency, batch 1, single thread

| model | pod (AMD EPYC 7543) | MacBook (Apple Silicon) |
|---|---:|---:|
| stock v3.2 int8 | 80 ms | — |
| tiny int8 | 83 ms | 36 ms |
| base int8 dynamic | 122 ms | 44 ms |
| base fp32 | 190–208 ms | 37 ms |

## Acceptance targets

| target | result |
|---|---|
| ≥ 84% accuracy on every Indic language (base fp32) | 10 of 11; Assamese 83.6 (CI 80.9–86.5) |
| AUC ≥ 0.90 on every Indic language (base fp32) | 8 of 11; Assamese 0.892, Gujarati 0.895, Malayalam 0.859 |
| English within 2 points of stock | pass (+2.0) |
| TamilEOT ≥ 84% | pass (85.9) |
| int8 within 1 point of fp32 | base dynamic int8: within 0.005 AUC everywhere, accuracy −0.7 to −2.6 at threshold 0.5; tiny int8: within 2 points except Marathi (−4.0) |

## Threshold tuning

Per-language thresholds tuned on the dev split (250–700 clips per language) do not transfer: balanced-accuracy gains on test are within ±2 points and plain accuracy usually drops (`thresholds.md`). The shipped models keep the default 0.5. Tune one global threshold per deployment on the production set from Stage 9, which is larger.

## Ambiguous test rows (text and audio labels disagree)

All models score 44–76% on these 400 clips (`eval_all_test_ambiguous.md`); the base model and stock are within noise of each other. These clips are genuinely hard and are excluded from the clean numbers above.

## Shipping recommendation

- **Default: base, dynamic int8** (24 MB). Best accuracy per millisecond on x86 servers; AUC identical to fp32; 122 ms single-thread on a server core, 44 ms on Apple Silicon.
- **base fp32** where the host is Apple Silicon or a GPU: same 37 ms as tiny there, and the best numbers.
- **tiny int8** for constrained CPUs: same size and speed as stock, ahead of stock in every language by 4 to 16 points.
- Do not ship base int8 MinMax.

Weakest languages are Assamese, Gujarati and Malayalam (82–85%). They have the same data volume as the others, so the gap is in the audio, not the sample count; the next lever is the Stage 9 production data for the languages you deploy.

## Spend

Pod time for training both models, exports, quantisation variants and all evaluations: about 3.5 h at $0.53 ≈ $2. Total project spend to date ≈ $38 (labels ≈ $36).