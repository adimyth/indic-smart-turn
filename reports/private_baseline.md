# Private production-call baseline

This report contains counts and model metrics only. Private audio, source paths, call identifiers, transcripts, and clips remain local under `data/private/`.

## Data coverage and category join

For Kannada, Malayalam, Marathi, Tamil, and Telugu, the Gemini-labeled test rows are the earliest sessions in file order, not a random sample. Bengali, English, Gujarati, Hindi, and Odia test rows are fully Gemini-labeled. Category A is rule complete/Gemini complete; B is rule incomplete/Gemini incomplete; C is rule incomplete/Gemini complete; D is rule complete/Gemini incomplete; unlabeled has no successful Gemini verdict. Test evaluation uses A, B, and C; D is reporting-only; unlabeled is excluded from test evaluation. Training retains only A and B, dropping C, D, and unlabeled rows.

| language | source sessions | used | quarantined | failed | quarantine rate | test rows | Gemini-labeled | model-scored A+B+C | D, reporting only | unlabeled |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Bengali | 200 | 152 | 48 | 0 | 24.0% | 2,116 | 2,116 | 2,002 | 114 | 0 |
| English | 200 | 147 | 53 | 0 | 26.5% | 2,486 | 2,486 | 2,330 | 156 | 0 |
| Gujarati | 146 | 110 | 36 | 0 | 24.7% | 2,006 | 2,006 | 1,920 | 86 | 0 |
| Hindi | 200 | 140 | 60 | 0 | 30.0% | 2,165 | 2,165 | 2,013 | 152 | 0 |
| Kannada | 83 | 56 | 27 | 0 | 32.5% | 718 | 367 | 355 | 12 | 351 |
| Malayalam | 200 | 150 | 50 | 0 | 25.0% | 1,043 | 462 | 433 | 29 | 581 |
| Marathi | 200 | 159 | 41 | 0 | 20.5% | 2,423 | 925 | 881 | 44 | 1,498 |
| Odia | 3 | 2 | 1 | 0 | 33.3% | 95 | 95 | 79 | 16 | 0 |
| Tamil | 186 | 135 | 51 | 0 | 27.4% | 2,027 | 991 | 925 | 66 | 1,036 |
| Telugu | 200 | 156 | 39 | 5 | 19.5% | 2,598 | 1,097 | 1,043 | 54 | 1,501 |

| language | test A, share | test B, share | test C, share | test D, share | test unlabeled, share | train A retained | train B retained | train C dropped | train D dropped | train unlabeled dropped |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Bengali | 268 (12.7%) | 1,089 (51.5%) | 645 (30.5%) | 114 (5.4%) | 0 (0.0%) | 788 | 3,196 | 1,977 | 332 | 0 |
| English | 392 (15.8%) | 1,285 (51.7%) | 653 (26.3%) | 156 (6.3%) | 0 (0.0%) | 849 | 3,049 | 1,700 | 444 | 0 |
| Gujarati | 283 (14.1%) | 1,018 (50.7%) | 619 (30.9%) | 86 (4.3%) | 0 (0.0%) | 464 | 1,741 | 1,028 | 174 | 0 |
| Hindi | 390 (18.0%) | 1,059 (48.9%) | 564 (26.1%) | 152 (7.0%) | 0 (0.0%) | 775 | 2,407 | 1,297 | 300 | 0 |
| Kannada | 48 (6.7%) | 206 (28.7%) | 101 (14.1%) | 12 (1.7%) | 351 (48.9%) | 145 | 493 | 284 | 51 | 886 |
| Malayalam | 105 (10.1%) | 192 (18.4%) | 136 (13.0%) | 29 (2.8%) | 581 (55.7%) | 393 | 1,035 | 734 | 101 | 2,144 |
| Marathi | 142 (5.9%) | 450 (18.6%) | 289 (11.9%) | 44 (1.8%) | 1,498 (61.8%) | 445 | 1,406 | 1,025 | 150 | 2,453 |
| Odia | 11 (11.6%) | 48 (50.5%) | 20 (21.1%) | 16 (16.8%) | 0 (0.0%) | 5 | 27 | 12 | 1 | 0 |
| Tamil | 163 (8.0%) | 500 (24.7%) | 262 (12.9%) | 66 (3.3%) | 1,036 (51.1%) | 341 | 943 | 614 | 111 | 1,965 |
| Telugu | 136 (5.2%) | 595 (22.9%) | 312 (12.0%) | 54 (2.1%) | 1,501 (57.8%) | 396 | 1,751 | 863 | 171 | 2,778 |

Odia is indicative only: 2 sessions, 95 test clips. Kannada is low-count. Sessions that failed the pre-registered speaker checks are quarantined, and the roleplay/TTS setting may not represent real customer-call rhythm.

## Private test metrics at threshold 0.5

Category A recall is the rate of answering on clear turn ends. Category B specificity is the rate of staying quiet on jointly unfinished pauses. Category C interrupt rate is the rate of answering on sentence-final pauses where the trainee resumed.

| language | category | n | model | metric (95% CI) |
|---|---|---:|---|---|
| Bengali | A | 268 | smartturn_v3.2 | A recall: 93.7% [90.7, 96.3] |
| Bengali | A | 268 | base_fp32 | A recall: 93.3% [89.9, 96.3] |
| Bengali | A | 268 | base_int8_dynamic | A recall: 93.3% [89.9, 96.3] |
| Bengali | A | 268 | tiny_int8 | A recall: 90.3% [86.6, 93.7] |
| Bengali | B | 1089 | smartturn_v3.2 | B specificity: 45.3% [42.2, 48.1] |
| Bengali | B | 1089 | base_fp32 | B specificity: 69.3% [66.7, 72.1] |
| Bengali | B | 1089 | base_int8_dynamic | B specificity: 69.9% [67.3, 72.8] |
| Bengali | B | 1089 | tiny_int8 | B specificity: 59.0% [56.1, 61.9] |
| Bengali | C | 645 | smartturn_v3.2 | C interrupt rate: 91.3% [89.0, 93.3] |
| Bengali | C | 645 | base_fp32 | C interrupt rate: 86.2% [83.7, 88.8] |
| Bengali | C | 645 | base_int8_dynamic | C interrupt rate: 86.5% [84.0, 89.0] |
| Bengali | C | 645 | tiny_int8 | C interrupt rate: 85.4% [82.6, 88.2] |
| English | A | 392 | smartturn_v3.2 | A recall: 76.3% [71.9, 80.1] |
| English | A | 392 | base_fp32 | A recall: 84.7% [80.9, 88.3] |
| English | A | 392 | base_int8_dynamic | A recall: 85.2% [81.6, 88.5] |
| English | A | 392 | tiny_int8 | A recall: 84.9% [81.4, 88.3] |
| English | B | 1285 | smartturn_v3.2 | B specificity: 66.1% [63.3, 68.8] |
| English | B | 1285 | base_fp32 | B specificity: 77.4% [75.1, 79.8] |
| English | B | 1285 | base_int8_dynamic | B specificity: 77.6% [75.3, 79.8] |
| English | B | 1285 | tiny_int8 | B specificity: 68.6% [66.1, 71.1] |
| English | C | 653 | smartturn_v3.2 | C interrupt rate: 68.9% [65.4, 72.6] |
| English | C | 653 | base_fp32 | C interrupt rate: 70.9% [67.2, 74.4] |
| English | C | 653 | base_int8_dynamic | C interrupt rate: 70.9% [67.1, 74.3] |
| English | C | 653 | tiny_int8 | C interrupt rate: 72.7% [69.5, 76.1] |
| Gujarati | A | 283 | smartturn_v3.2 | A recall: 88.0% [84.1, 91.5] |
| Gujarati | A | 283 | base_fp32 | A recall: 90.1% [86.6, 93.3] |
| Gujarati | A | 283 | base_int8_dynamic | A recall: 89.8% [86.6, 93.3] |
| Gujarati | A | 283 | tiny_int8 | A recall: 91.2% [87.6, 94.3] |
| Gujarati | B | 1018 | smartturn_v3.2 | B specificity: 58.6% [55.5, 61.4] |
| Gujarati | B | 1018 | base_fp32 | B specificity: 73.7% [70.9, 76.4] |
| Gujarati | B | 1018 | base_int8_dynamic | B specificity: 73.8% [71.0, 76.5] |
| Gujarati | B | 1018 | tiny_int8 | B specificity: 70.0% [67.2, 73.0] |
| Gujarati | C | 619 | smartturn_v3.2 | C interrupt rate: 79.5% [76.3, 82.7] |
| Gujarati | C | 619 | base_fp32 | C interrupt rate: 77.1% [73.7, 80.3] |
| Gujarati | C | 619 | base_int8_dynamic | C interrupt rate: 78.0% [74.6, 81.3] |
| Gujarati | C | 619 | tiny_int8 | C interrupt rate: 81.4% [78.5, 84.3] |
| Hindi | A | 390 | smartturn_v3.2 | A recall: 91.5% [89.0, 94.1] |
| Hindi | A | 390 | base_fp32 | A recall: 92.6% [89.7, 94.9] |
| Hindi | A | 390 | base_int8_dynamic | A recall: 92.3% [89.5, 94.9] |
| Hindi | A | 390 | tiny_int8 | A recall: 89.5% [86.2, 92.3] |
| Hindi | B | 1059 | smartturn_v3.2 | B specificity: 56.4% [53.4, 59.7] |
| Hindi | B | 1059 | base_fp32 | B specificity: 70.8% [68.2, 73.7] |
| Hindi | B | 1059 | base_int8_dynamic | B specificity: 70.4% [67.8, 73.1] |
| Hindi | B | 1059 | tiny_int8 | B specificity: 65.5% [62.5, 68.4] |
| Hindi | C | 564 | smartturn_v3.2 | C interrupt rate: 83.9% [81.0, 87.1] |
| Hindi | C | 564 | base_fp32 | C interrupt rate: 87.4% [84.7, 89.9] |
| Hindi | C | 564 | base_int8_dynamic | C interrupt rate: 87.4% [84.6, 90.1] |
| Hindi | C | 564 | tiny_int8 | C interrupt rate: 86.2% [83.2, 88.8] |
| Kannada | A | 48 | smartturn_v3.2 | A recall: 91.7% [83.3, 97.9] |
| Kannada | A | 48 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Kannada | A | 48 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Kannada | A | 48 | tiny_int8 | A recall: 91.7% [83.3, 97.9] |
| Kannada | B | 206 | smartturn_v3.2 | B specificity: 47.6% [40.8, 53.9] |
| Kannada | B | 206 | base_fp32 | B specificity: 61.7% [54.9, 68.4] |
| Kannada | B | 206 | base_int8_dynamic | B specificity: 63.1% [56.3, 69.9] |
| Kannada | B | 206 | tiny_int8 | B specificity: 53.9% [47.1, 60.7] |
| Kannada | C | 101 | smartturn_v3.2 | C interrupt rate: 88.1% [82.2, 94.1] |
| Kannada | C | 101 | base_fp32 | C interrupt rate: 84.2% [77.2, 91.1] |
| Kannada | C | 101 | base_int8_dynamic | C interrupt rate: 84.2% [75.2, 90.1] |
| Kannada | C | 101 | tiny_int8 | C interrupt rate: 87.1% [80.2, 93.1] |
| Malayalam | A | 105 | smartturn_v3.2 | A recall: 83.8% [76.2, 90.5] |
| Malayalam | A | 105 | base_fp32 | A recall: 95.2% [90.5, 99.0] |
| Malayalam | A | 105 | base_int8_dynamic | A recall: 97.1% [94.3, 100.0] |
| Malayalam | A | 105 | tiny_int8 | A recall: 91.4% [85.7, 96.2] |
| Malayalam | B | 192 | smartturn_v3.2 | B specificity: 43.2% [36.5, 50.0] |
| Malayalam | B | 192 | base_fp32 | B specificity: 66.7% [59.9, 73.4] |
| Malayalam | B | 192 | base_int8_dynamic | B specificity: 65.6% [58.9, 71.9] |
| Malayalam | B | 192 | tiny_int8 | B specificity: 63.0% [56.2, 69.8] |
| Malayalam | C | 136 | smartturn_v3.2 | C interrupt rate: 83.1% [76.5, 89.0] |
| Malayalam | C | 136 | base_fp32 | C interrupt rate: 87.5% [81.6, 91.9] |
| Malayalam | C | 136 | base_int8_dynamic | C interrupt rate: 89.0% [83.8, 94.1] |
| Malayalam | C | 136 | tiny_int8 | C interrupt rate: 87.5% [81.6, 92.6] |
| Marathi | A | 142 | smartturn_v3.2 | A recall: 91.5% [86.6, 95.8] |
| Marathi | A | 142 | base_fp32 | A recall: 90.8% [85.9, 95.8] |
| Marathi | A | 142 | base_int8_dynamic | A recall: 92.3% [87.3, 96.5] |
| Marathi | A | 142 | tiny_int8 | A recall: 89.4% [83.8, 93.7] |
| Marathi | B | 450 | smartturn_v3.2 | B specificity: 48.7% [44.2, 53.6] |
| Marathi | B | 450 | base_fp32 | B specificity: 73.1% [69.3, 77.6] |
| Marathi | B | 450 | base_int8_dynamic | B specificity: 72.7% [68.4, 76.7] |
| Marathi | B | 450 | tiny_int8 | B specificity: 67.8% [63.5, 72.2] |
| Marathi | C | 289 | smartturn_v3.2 | C interrupt rate: 85.5% [81.3, 89.3] |
| Marathi | C | 289 | base_fp32 | C interrupt rate: 78.9% [74.0, 83.4] |
| Marathi | C | 289 | base_int8_dynamic | C interrupt rate: 78.9% [74.0, 83.7] |
| Marathi | C | 289 | tiny_int8 | C interrupt rate: 77.9% [73.0, 82.0] |
| Odia | A | 11 | smartturn_v3.2 | A recall: 81.8% [54.5, 100.0] |
| Odia | A | 11 | base_fp32 | A recall: 90.9% [72.7, 100.0] |
| Odia | A | 11 | base_int8_dynamic | A recall: 90.9% [72.7, 100.0] |
| Odia | A | 11 | tiny_int8 | A recall: 90.9% [72.7, 100.0] |
| Odia | B | 48 | smartturn_v3.2 | B specificity: 58.3% [43.8, 70.8] |
| Odia | B | 48 | base_fp32 | B specificity: 75.0% [62.5, 87.5] |
| Odia | B | 48 | base_int8_dynamic | B specificity: 75.0% [62.5, 85.5] |
| Odia | B | 48 | tiny_int8 | B specificity: 50.0% [37.5, 64.6] |
| Odia | C | 20 | smartturn_v3.2 | C interrupt rate: 90.0% [75.0, 100.0] |
| Odia | C | 20 | base_fp32 | C interrupt rate: 95.0% [85.0, 100.0] |
| Odia | C | 20 | base_int8_dynamic | C interrupt rate: 95.0% [85.0, 100.0] |
| Odia | C | 20 | tiny_int8 | C interrupt rate: 90.0% [75.0, 100.0] |
| Tamil | A | 163 | smartturn_v3.2 | A recall: 92.6% [88.3, 96.3] |
| Tamil | A | 163 | base_fp32 | A recall: 95.1% [91.4, 98.2] |
| Tamil | A | 163 | base_int8_dynamic | A recall: 95.1% [92.0, 98.2] |
| Tamil | A | 163 | tiny_int8 | A recall: 89.6% [84.7, 93.9] |
| Tamil | B | 500 | smartturn_v3.2 | B specificity: 41.6% [36.8, 46.0] |
| Tamil | B | 500 | base_fp32 | B specificity: 72.2% [68.4, 76.6] |
| Tamil | B | 500 | base_int8_dynamic | B specificity: 70.6% [66.8, 74.6] |
| Tamil | B | 500 | tiny_int8 | B specificity: 60.8% [56.4, 65.4] |
| Tamil | C | 262 | smartturn_v3.2 | C interrupt rate: 88.9% [85.1, 92.4] |
| Tamil | C | 262 | base_fp32 | C interrupt rate: 91.6% [88.2, 95.0] |
| Tamil | C | 262 | base_int8_dynamic | C interrupt rate: 90.5% [86.6, 93.9] |
| Tamil | C | 262 | tiny_int8 | C interrupt rate: 84.7% [80.5, 88.9] |
| Telugu | A | 136 | smartturn_v3.2 | A recall: 90.4% [85.3, 94.9] |
| Telugu | A | 136 | base_fp32 | A recall: 94.9% [91.2, 98.5] |
| Telugu | A | 136 | base_int8_dynamic | A recall: 94.1% [90.4, 97.8] |
| Telugu | A | 136 | tiny_int8 | A recall: 92.6% [88.2, 96.3] |
| Telugu | B | 595 | smartturn_v3.2 | B specificity: 51.6% [47.9, 56.0] |
| Telugu | B | 595 | base_fp32 | B specificity: 67.9% [64.0, 71.4] |
| Telugu | B | 595 | base_int8_dynamic | B specificity: 67.4% [63.4, 71.1] |
| Telugu | B | 595 | tiny_int8 | B specificity: 62.9% [58.8, 66.6] |
| Telugu | C | 312 | smartturn_v3.2 | C interrupt rate: 88.1% [84.3, 91.4] |
| Telugu | C | 312 | base_fp32 | C interrupt rate: 90.4% [86.9, 93.3] |
| Telugu | C | 312 | base_int8_dynamic | C interrupt rate: 91.7% [88.5, 94.6] |
| Telugu | C | 312 | tiny_int8 | C interrupt rate: 84.6% [80.8, 88.1] |

## Metrics by pause length

| language | pause length | category | n | model | metric (95% CI) |
|---|---|---|---:|---|---|
| Bengali | under 0.2 s | A | 1 | smartturn_v3.2 | A recall: 0.0% [0.0, 0.0] |
| Bengali | under 0.2 s | A | 1 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Bengali | under 0.2 s | A | 1 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Bengali | under 0.2 s | A | 1 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Bengali | under 0.2 s | B | 140 | smartturn_v3.2 | B specificity: 37.1% [29.3, 45.7] |
| Bengali | under 0.2 s | B | 140 | base_fp32 | B specificity: 75.7% [68.6, 82.9] |
| Bengali | under 0.2 s | B | 140 | base_int8_dynamic | B specificity: 76.4% [69.3, 83.6] |
| Bengali | under 0.2 s | B | 140 | tiny_int8 | B specificity: 61.4% [52.9, 69.3] |
| Bengali | under 0.2 s | C | 40 | smartturn_v3.2 | C interrupt rate: 95.0% [87.5, 100.0] |
| Bengali | under 0.2 s | C | 40 | base_fp32 | C interrupt rate: 72.5% [57.5, 85.0] |
| Bengali | under 0.2 s | C | 40 | base_int8_dynamic | C interrupt rate: 72.5% [57.5, 85.0] |
| Bengali | under 0.2 s | C | 40 | tiny_int8 | C interrupt rate: 85.0% [72.5, 95.0] |
| Bengali | 0.2–0.5 s | A | 26 | smartturn_v3.2 | A recall: 96.2% [88.5, 100.0] |
| Bengali | 0.2–0.5 s | A | 26 | base_fp32 | A recall: 84.6% [69.2, 96.2] |
| Bengali | 0.2–0.5 s | A | 26 | base_int8_dynamic | A recall: 80.8% [65.4, 96.2] |
| Bengali | 0.2–0.5 s | A | 26 | tiny_int8 | A recall: 84.6% [69.2, 96.2] |
| Bengali | 0.2–0.5 s | B | 638 | smartturn_v3.2 | B specificity: 47.2% [43.6, 51.1] |
| Bengali | 0.2–0.5 s | B | 638 | base_fp32 | B specificity: 68.0% [64.4, 71.8] |
| Bengali | 0.2–0.5 s | B | 638 | base_int8_dynamic | B specificity: 68.3% [64.9, 71.9] |
| Bengali | 0.2–0.5 s | B | 638 | tiny_int8 | B specificity: 59.2% [55.3, 62.9] |
| Bengali | 0.2–0.5 s | C | 405 | smartturn_v3.2 | C interrupt rate: 90.6% [87.7, 93.3] |
| Bengali | 0.2–0.5 s | C | 405 | base_fp32 | C interrupt rate: 85.4% [81.7, 88.6] |
| Bengali | 0.2–0.5 s | C | 405 | base_int8_dynamic | C interrupt rate: 85.2% [81.7, 88.6] |
| Bengali | 0.2–0.5 s | C | 405 | tiny_int8 | C interrupt rate: 85.7% [82.2, 88.9] |
| Bengali | 0.5–1.0 s | A | 17 | smartturn_v3.2 | A recall: 94.1% [82.4, 100.0] |
| Bengali | 0.5–1.0 s | A | 17 | base_fp32 | A recall: 94.1% [82.4, 100.0] |
| Bengali | 0.5–1.0 s | A | 17 | base_int8_dynamic | A recall: 94.1% [82.4, 100.0] |
| Bengali | 0.5–1.0 s | A | 17 | tiny_int8 | A recall: 70.6% [52.9, 88.2] |
| Bengali | 0.5–1.0 s | B | 232 | smartturn_v3.2 | B specificity: 47.4% [41.4, 54.3] |
| Bengali | 0.5–1.0 s | B | 232 | base_fp32 | B specificity: 71.6% [65.5, 77.6] |
| Bengali | 0.5–1.0 s | B | 232 | base_int8_dynamic | B specificity: 72.4% [66.8, 78.0] |
| Bengali | 0.5–1.0 s | B | 232 | tiny_int8 | B specificity: 62.1% [56.0, 68.5] |
| Bengali | 0.5–1.0 s | C | 140 | smartturn_v3.2 | C interrupt rate: 89.3% [84.3, 93.6] |
| Bengali | 0.5–1.0 s | C | 140 | base_fp32 | C interrupt rate: 88.6% [82.9, 93.6] |
| Bengali | 0.5–1.0 s | C | 140 | base_int8_dynamic | C interrupt rate: 90.7% [85.7, 95.0] |
| Bengali | 0.5–1.0 s | C | 140 | tiny_int8 | C interrupt rate: 83.6% [77.1, 89.3] |
| Bengali | 1.0 s and over | A | 224 | smartturn_v3.2 | A recall: 93.8% [90.6, 96.9] |
| Bengali | 1.0 s and over | A | 224 | base_fp32 | A recall: 94.2% [91.1, 96.9] |
| Bengali | 1.0 s and over | A | 224 | base_int8_dynamic | A recall: 94.6% [92.0, 97.3] |
| Bengali | 1.0 s and over | A | 224 | tiny_int8 | A recall: 92.4% [88.8, 96.0] |
| Bengali | 1.0 s and over | B | 79 | smartturn_v3.2 | B specificity: 38.0% [27.8, 49.4] |
| Bengali | 1.0 s and over | B | 79 | base_fp32 | B specificity: 62.0% [50.6, 73.4] |
| Bengali | 1.0 s and over | B | 79 | base_int8_dynamic | B specificity: 63.3% [53.2, 73.4] |
| Bengali | 1.0 s and over | B | 79 | tiny_int8 | B specificity: 44.3% [34.2, 55.7] |
| Bengali | 1.0 s and over | C | 60 | smartturn_v3.2 | C interrupt rate: 98.3% [95.0, 100.0] |
| Bengali | 1.0 s and over | C | 60 | base_fp32 | C interrupt rate: 95.0% [88.3, 100.0] |
| Bengali | 1.0 s and over | C | 60 | base_int8_dynamic | C interrupt rate: 95.0% [90.0, 100.0] |
| Bengali | 1.0 s and over | C | 60 | tiny_int8 | C interrupt rate: 88.3% [80.0, 95.0] |
| English | under 0.2 s | A | 4 | smartturn_v3.2 | A recall: 75.0% [25.0, 100.0] |
| English | under 0.2 s | A | 4 | base_fp32 | A recall: 75.0% [25.0, 100.0] |
| English | under 0.2 s | A | 4 | base_int8_dynamic | A recall: 75.0% [25.0, 100.0] |
| English | under 0.2 s | A | 4 | tiny_int8 | A recall: 75.0% [25.0, 100.0] |
| English | under 0.2 s | B | 152 | smartturn_v3.2 | B specificity: 57.9% [50.0, 65.1] |
| English | under 0.2 s | B | 152 | base_fp32 | B specificity: 80.3% [73.7, 86.2] |
| English | under 0.2 s | B | 152 | base_int8_dynamic | B specificity: 78.9% [72.4, 84.9] |
| English | under 0.2 s | B | 152 | tiny_int8 | B specificity: 71.1% [63.8, 78.3] |
| English | under 0.2 s | C | 40 | smartturn_v3.2 | C interrupt rate: 77.5% [62.5, 90.0] |
| English | under 0.2 s | C | 40 | base_fp32 | C interrupt rate: 70.0% [55.0, 82.5] |
| English | under 0.2 s | C | 40 | base_int8_dynamic | C interrupt rate: 65.0% [50.0, 80.0] |
| English | under 0.2 s | C | 40 | tiny_int8 | C interrupt rate: 67.5% [52.5, 82.5] |
| English | 0.2–0.5 s | A | 36 | smartturn_v3.2 | A recall: 75.0% [58.3, 88.9] |
| English | 0.2–0.5 s | A | 36 | base_fp32 | A recall: 66.7% [50.0, 80.6] |
| English | 0.2–0.5 s | A | 36 | base_int8_dynamic | A recall: 66.7% [52.7, 83.3] |
| English | 0.2–0.5 s | A | 36 | tiny_int8 | A recall: 77.8% [63.9, 91.7] |
| English | 0.2–0.5 s | B | 802 | smartturn_v3.2 | B specificity: 67.3% [64.0, 70.4] |
| English | 0.2–0.5 s | B | 802 | base_fp32 | B specificity: 77.7% [74.8, 80.5] |
| English | 0.2–0.5 s | B | 802 | base_int8_dynamic | B specificity: 78.6% [75.3, 81.7] |
| English | 0.2–0.5 s | B | 802 | tiny_int8 | B specificity: 68.8% [65.8, 72.2] |
| English | 0.2–0.5 s | C | 389 | smartturn_v3.2 | C interrupt rate: 68.4% [63.8, 73.0] |
| English | 0.2–0.5 s | C | 389 | base_fp32 | C interrupt rate: 69.2% [64.5, 73.5] |
| English | 0.2–0.5 s | C | 389 | base_int8_dynamic | C interrupt rate: 69.4% [64.8, 73.8] |
| English | 0.2–0.5 s | C | 389 | tiny_int8 | C interrupt rate: 72.5% [68.4, 76.9] |
| English | 0.5–1.0 s | A | 22 | smartturn_v3.2 | A recall: 63.6% [40.9, 81.8] |
| English | 0.5–1.0 s | A | 22 | base_fp32 | A recall: 81.8% [63.6, 95.5] |
| English | 0.5–1.0 s | A | 22 | base_int8_dynamic | A recall: 81.8% [63.6, 95.5] |
| English | 0.5–1.0 s | A | 22 | tiny_int8 | A recall: 86.4% [68.2, 100.0] |
| English | 0.5–1.0 s | B | 264 | smartturn_v3.2 | B specificity: 67.4% [61.7, 72.7] |
| English | 0.5–1.0 s | B | 264 | base_fp32 | B specificity: 77.7% [73.1, 82.2] |
| English | 0.5–1.0 s | B | 264 | base_int8_dynamic | B specificity: 76.9% [71.6, 81.8] |
| English | 0.5–1.0 s | B | 264 | tiny_int8 | B specificity: 69.7% [64.4, 75.0] |
| English | 0.5–1.0 s | C | 169 | smartturn_v3.2 | C interrupt rate: 66.3% [59.2, 73.4] |
| English | 0.5–1.0 s | C | 169 | base_fp32 | C interrupt rate: 72.8% [66.3, 79.3] |
| English | 0.5–1.0 s | C | 169 | base_int8_dynamic | C interrupt rate: 74.0% [66.9, 81.1] |
| English | 0.5–1.0 s | C | 169 | tiny_int8 | C interrupt rate: 71.0% [64.5, 77.5] |
| English | 1.0 s and over | A | 330 | smartturn_v3.2 | A recall: 77.3% [73.3, 81.5] |
| English | 1.0 s and over | A | 330 | base_fp32 | A recall: 87.0% [83.6, 90.3] |
| English | 1.0 s and over | A | 330 | base_int8_dynamic | A recall: 87.6% [83.9, 91.2] |
| English | 1.0 s and over | A | 330 | tiny_int8 | A recall: 85.8% [81.8, 89.4] |
| English | 1.0 s and over | B | 67 | smartturn_v3.2 | B specificity: 64.2% [52.2, 74.6] |
| English | 1.0 s and over | B | 67 | base_fp32 | B specificity: 67.2% [56.7, 77.6] |
| English | 1.0 s and over | B | 67 | base_int8_dynamic | B specificity: 65.7% [53.7, 76.1] |
| English | 1.0 s and over | B | 67 | tiny_int8 | B specificity: 56.7% [44.8, 68.7] |
| English | 1.0 s and over | C | 55 | smartturn_v3.2 | C interrupt rate: 74.5% [61.8, 85.5] |
| English | 1.0 s and over | C | 55 | base_fp32 | C interrupt rate: 78.2% [67.3, 89.1] |
| English | 1.0 s and over | C | 55 | base_int8_dynamic | C interrupt rate: 76.4% [63.6, 87.3] |
| English | 1.0 s and over | C | 55 | tiny_int8 | C interrupt rate: 83.6% [72.7, 92.7] |
| Gujarati | under 0.2 s | A | 3 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Gujarati | under 0.2 s | A | 3 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Gujarati | under 0.2 s | A | 3 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Gujarati | under 0.2 s | A | 3 | tiny_int8 | A recall: 66.7% [0.0, 100.0] |
| Gujarati | under 0.2 s | B | 109 | smartturn_v3.2 | B specificity: 48.6% [39.4, 57.8] |
| Gujarati | under 0.2 s | B | 109 | base_fp32 | B specificity: 80.7% [73.4, 87.2] |
| Gujarati | under 0.2 s | B | 109 | base_int8_dynamic | B specificity: 80.7% [73.4, 88.1] |
| Gujarati | under 0.2 s | B | 109 | tiny_int8 | B specificity: 67.9% [59.6, 76.1] |
| Gujarati | under 0.2 s | C | 41 | smartturn_v3.2 | C interrupt rate: 92.7% [85.4, 100.0] |
| Gujarati | under 0.2 s | C | 41 | base_fp32 | C interrupt rate: 73.2% [58.5, 85.4] |
| Gujarati | under 0.2 s | C | 41 | base_int8_dynamic | C interrupt rate: 73.2% [58.5, 87.8] |
| Gujarati | under 0.2 s | C | 41 | tiny_int8 | C interrupt rate: 85.4% [73.2, 95.1] |
| Gujarati | 0.2–0.5 s | A | 18 | smartturn_v3.2 | A recall: 77.8% [55.6, 94.4] |
| Gujarati | 0.2–0.5 s | A | 18 | base_fp32 | A recall: 72.2% [50.0, 88.9] |
| Gujarati | 0.2–0.5 s | A | 18 | base_int8_dynamic | A recall: 72.2% [50.0, 88.9] |
| Gujarati | 0.2–0.5 s | A | 18 | tiny_int8 | A recall: 83.3% [66.7, 100.0] |
| Gujarati | 0.2–0.5 s | B | 618 | smartturn_v3.2 | B specificity: 60.2% [56.3, 63.8] |
| Gujarati | 0.2–0.5 s | B | 618 | base_fp32 | B specificity: 73.3% [69.7, 76.7] |
| Gujarati | 0.2–0.5 s | B | 618 | base_int8_dynamic | B specificity: 73.1% [69.7, 76.7] |
| Gujarati | 0.2–0.5 s | B | 618 | tiny_int8 | B specificity: 70.2% [66.7, 73.8] |
| Gujarati | 0.2–0.5 s | C | 399 | smartturn_v3.2 | C interrupt rate: 78.9% [74.7, 83.2] |
| Gujarati | 0.2–0.5 s | C | 399 | base_fp32 | C interrupt rate: 76.9% [72.7, 81.0] |
| Gujarati | 0.2–0.5 s | C | 399 | base_int8_dynamic | C interrupt rate: 78.2% [74.7, 82.2] |
| Gujarati | 0.2–0.5 s | C | 399 | tiny_int8 | C interrupt rate: 80.7% [76.9, 84.0] |
| Gujarati | 0.5–1.0 s | A | 12 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Gujarati | 0.5–1.0 s | A | 12 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Gujarati | 0.5–1.0 s | A | 12 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Gujarati | 0.5–1.0 s | A | 12 | tiny_int8 | A recall: 91.7% [75.0, 100.0] |
| Gujarati | 0.5–1.0 s | B | 226 | smartturn_v3.2 | B specificity: 59.7% [53.5, 65.9] |
| Gujarati | 0.5–1.0 s | B | 226 | base_fp32 | B specificity: 72.1% [66.4, 77.4] |
| Gujarati | 0.5–1.0 s | B | 226 | base_int8_dynamic | B specificity: 73.0% [67.2, 78.3] |
| Gujarati | 0.5–1.0 s | B | 226 | tiny_int8 | B specificity: 69.0% [63.3, 75.2] |
| Gujarati | 0.5–1.0 s | C | 130 | smartturn_v3.2 | C interrupt rate: 77.7% [70.8, 84.6] |
| Gujarati | 0.5–1.0 s | C | 130 | base_fp32 | C interrupt rate: 81.5% [73.8, 87.7] |
| Gujarati | 0.5–1.0 s | C | 130 | base_int8_dynamic | C interrupt rate: 81.5% [74.6, 87.7] |
| Gujarati | 0.5–1.0 s | C | 130 | tiny_int8 | C interrupt rate: 82.3% [75.4, 88.5] |
| Gujarati | 1.0 s and over | A | 250 | smartturn_v3.2 | A recall: 88.0% [84.0, 92.0] |
| Gujarati | 1.0 s and over | A | 250 | base_fp32 | A recall: 90.8% [87.2, 94.0] |
| Gujarati | 1.0 s and over | A | 250 | base_int8_dynamic | A recall: 90.4% [86.4, 93.6] |
| Gujarati | 1.0 s and over | A | 250 | tiny_int8 | A recall: 92.0% [88.4, 95.2] |
| Gujarati | 1.0 s and over | B | 65 | smartturn_v3.2 | B specificity: 56.9% [44.6, 69.2] |
| Gujarati | 1.0 s and over | B | 65 | base_fp32 | B specificity: 70.8% [58.5, 80.0] |
| Gujarati | 1.0 s and over | B | 65 | base_int8_dynamic | B specificity: 70.8% [60.0, 83.1] |
| Gujarati | 1.0 s and over | B | 65 | tiny_int8 | B specificity: 75.4% [64.6, 86.2] |
| Gujarati | 1.0 s and over | C | 49 | smartturn_v3.2 | C interrupt rate: 77.6% [67.3, 89.8] |
| Gujarati | 1.0 s and over | C | 49 | base_fp32 | C interrupt rate: 69.4% [57.1, 81.6] |
| Gujarati | 1.0 s and over | C | 49 | base_int8_dynamic | C interrupt rate: 71.4% [59.2, 83.7] |
| Gujarati | 1.0 s and over | C | 49 | tiny_int8 | C interrupt rate: 81.6% [71.4, 91.8] |
| Hindi | under 0.2 s | A | 4 | smartturn_v3.2 | A recall: 75.0% [25.0, 100.0] |
| Hindi | under 0.2 s | A | 4 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Hindi | under 0.2 s | A | 4 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Hindi | under 0.2 s | A | 4 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Hindi | under 0.2 s | B | 103 | smartturn_v3.2 | B specificity: 51.5% [41.7, 61.2] |
| Hindi | under 0.2 s | B | 103 | base_fp32 | B specificity: 77.7% [69.9, 85.4] |
| Hindi | under 0.2 s | B | 103 | base_int8_dynamic | B specificity: 74.8% [66.0, 82.5] |
| Hindi | under 0.2 s | B | 103 | tiny_int8 | B specificity: 71.8% [63.1, 80.6] |
| Hindi | under 0.2 s | C | 33 | smartturn_v3.2 | C interrupt rate: 81.8% [66.7, 93.9] |
| Hindi | under 0.2 s | C | 33 | base_fp32 | C interrupt rate: 87.9% [75.8, 97.0] |
| Hindi | under 0.2 s | C | 33 | base_int8_dynamic | C interrupt rate: 87.9% [75.8, 97.0] |
| Hindi | under 0.2 s | C | 33 | tiny_int8 | C interrupt rate: 87.9% [75.8, 97.0] |
| Hindi | 0.2–0.5 s | A | 37 | smartturn_v3.2 | A recall: 86.5% [75.7, 97.3] |
| Hindi | 0.2–0.5 s | A | 37 | base_fp32 | A recall: 89.2% [78.4, 97.3] |
| Hindi | 0.2–0.5 s | A | 37 | base_int8_dynamic | A recall: 86.5% [75.7, 97.3] |
| Hindi | 0.2–0.5 s | A | 37 | tiny_int8 | A recall: 81.1% [67.6, 91.9] |
| Hindi | 0.2–0.5 s | B | 629 | smartturn_v3.2 | B specificity: 58.3% [54.5, 62.2] |
| Hindi | 0.2–0.5 s | B | 629 | base_fp32 | B specificity: 71.2% [67.9, 74.7] |
| Hindi | 0.2–0.5 s | B | 629 | base_int8_dynamic | B specificity: 71.1% [67.6, 74.4] |
| Hindi | 0.2–0.5 s | B | 629 | tiny_int8 | B specificity: 65.8% [61.8, 69.6] |
| Hindi | 0.2–0.5 s | C | 299 | smartturn_v3.2 | C interrupt rate: 82.6% [78.6, 86.3] |
| Hindi | 0.2–0.5 s | C | 299 | base_fp32 | C interrupt rate: 84.3% [79.9, 88.6] |
| Hindi | 0.2–0.5 s | C | 299 | base_int8_dynamic | C interrupt rate: 84.3% [79.9, 88.3] |
| Hindi | 0.2–0.5 s | C | 299 | tiny_int8 | C interrupt rate: 86.0% [81.9, 90.0] |
| Hindi | 0.5–1.0 s | A | 31 | smartturn_v3.2 | A recall: 77.4% [61.3, 93.5] |
| Hindi | 0.5–1.0 s | A | 31 | base_fp32 | A recall: 87.1% [74.2, 96.8] |
| Hindi | 0.5–1.0 s | A | 31 | base_int8_dynamic | A recall: 87.1% [74.2, 96.8] |
| Hindi | 0.5–1.0 s | A | 31 | tiny_int8 | A recall: 83.9% [71.0, 96.8] |
| Hindi | 0.5–1.0 s | B | 253 | smartturn_v3.2 | B specificity: 55.3% [49.0, 61.7] |
| Hindi | 0.5–1.0 s | B | 253 | base_fp32 | B specificity: 69.2% [63.2, 74.7] |
| Hindi | 0.5–1.0 s | B | 253 | base_int8_dynamic | B specificity: 69.6% [64.4, 75.1] |
| Hindi | 0.5–1.0 s | B | 253 | tiny_int8 | B specificity: 63.2% [56.9, 69.2] |
| Hindi | 0.5–1.0 s | C | 181 | smartturn_v3.2 | C interrupt rate: 85.6% [80.1, 90.1] |
| Hindi | 0.5–1.0 s | C | 181 | base_fp32 | C interrupt rate: 91.2% [86.7, 95.0] |
| Hindi | 0.5–1.0 s | C | 181 | base_int8_dynamic | C interrupt rate: 90.6% [86.2, 94.5] |
| Hindi | 0.5–1.0 s | C | 181 | tiny_int8 | C interrupt rate: 86.2% [80.7, 91.2] |
| Hindi | 1.0 s and over | A | 318 | smartturn_v3.2 | A recall: 93.7% [90.9, 96.2] |
| Hindi | 1.0 s and over | A | 318 | base_fp32 | A recall: 93.4% [90.3, 95.9] |
| Hindi | 1.0 s and over | A | 318 | base_int8_dynamic | A recall: 93.4% [90.6, 95.9] |
| Hindi | 1.0 s and over | A | 318 | tiny_int8 | A recall: 90.9% [87.7, 94.0] |
| Hindi | 1.0 s and over | B | 74 | smartturn_v3.2 | B specificity: 50.0% [39.2, 60.8] |
| Hindi | 1.0 s and over | B | 74 | base_fp32 | B specificity: 63.5% [52.7, 74.3] |
| Hindi | 1.0 s and over | B | 74 | base_int8_dynamic | B specificity: 62.2% [51.4, 73.0] |
| Hindi | 1.0 s and over | B | 74 | tiny_int8 | B specificity: 62.2% [50.0, 73.0] |
| Hindi | 1.0 s and over | C | 51 | smartturn_v3.2 | C interrupt rate: 86.3% [76.5, 94.1] |
| Hindi | 1.0 s and over | C | 51 | base_fp32 | C interrupt rate: 92.2% [84.3, 98.0] |
| Hindi | 1.0 s and over | C | 51 | base_int8_dynamic | C interrupt rate: 94.1% [86.3, 100.0] |
| Hindi | 1.0 s and over | C | 51 | tiny_int8 | C interrupt rate: 86.3% [76.5, 94.1] |
| Kannada | under 0.2 s | A | 1 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Kannada | under 0.2 s | A | 1 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Kannada | under 0.2 s | A | 1 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Kannada | under 0.2 s | A | 1 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Kannada | under 0.2 s | B | 16 | smartturn_v3.2 | B specificity: 62.5% [37.5, 87.5] |
| Kannada | under 0.2 s | B | 16 | base_fp32 | B specificity: 87.5% [68.8, 100.0] |
| Kannada | under 0.2 s | B | 16 | base_int8_dynamic | B specificity: 87.5% [68.8, 100.0] |
| Kannada | under 0.2 s | B | 16 | tiny_int8 | B specificity: 75.0% [50.0, 93.8] |
| Kannada | under 0.2 s | C | 11 | smartturn_v3.2 | C interrupt rate: 81.8% [54.5, 100.0] |
| Kannada | under 0.2 s | C | 11 | base_fp32 | C interrupt rate: 90.9% [72.7, 100.0] |
| Kannada | under 0.2 s | C | 11 | base_int8_dynamic | C interrupt rate: 90.9% [72.7, 100.0] |
| Kannada | under 0.2 s | C | 11 | tiny_int8 | C interrupt rate: 81.8% [54.5, 100.0] |
| Kannada | 0.2–0.5 s | A | 4 | smartturn_v3.2 | A recall: 75.0% [25.0, 100.0] |
| Kannada | 0.2–0.5 s | A | 4 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Kannada | 0.2–0.5 s | A | 4 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Kannada | 0.2–0.5 s | A | 4 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Kannada | 0.2–0.5 s | B | 123 | smartturn_v3.2 | B specificity: 52.0% [43.1, 61.0] |
| Kannada | 0.2–0.5 s | B | 123 | base_fp32 | B specificity: 59.3% [51.2, 67.5] |
| Kannada | 0.2–0.5 s | B | 123 | base_int8_dynamic | B specificity: 61.0% [52.8, 69.1] |
| Kannada | 0.2–0.5 s | B | 123 | tiny_int8 | B specificity: 60.2% [51.2, 69.1] |
| Kannada | 0.2–0.5 s | C | 75 | smartturn_v3.2 | C interrupt rate: 88.0% [80.0, 94.7] |
| Kannada | 0.2–0.5 s | C | 75 | base_fp32 | C interrupt rate: 81.3% [72.0, 89.3] |
| Kannada | 0.2–0.5 s | C | 75 | base_int8_dynamic | C interrupt rate: 81.3% [72.0, 90.7] |
| Kannada | 0.2–0.5 s | C | 75 | tiny_int8 | C interrupt rate: 86.7% [78.7, 93.3] |
| Kannada | 0.5–1.0 s | A | 4 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Kannada | 0.5–1.0 s | A | 4 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Kannada | 0.5–1.0 s | A | 4 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Kannada | 0.5–1.0 s | A | 4 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Kannada | 0.5–1.0 s | B | 55 | smartturn_v3.2 | B specificity: 34.5% [21.8, 47.3] |
| Kannada | 0.5–1.0 s | B | 55 | base_fp32 | B specificity: 60.0% [47.3, 72.7] |
| Kannada | 0.5–1.0 s | B | 55 | base_int8_dynamic | B specificity: 61.8% [49.1, 74.5] |
| Kannada | 0.5–1.0 s | B | 55 | tiny_int8 | B specificity: 38.2% [25.5, 50.9] |
| Kannada | 0.5–1.0 s | C | 11 | smartturn_v3.2 | C interrupt rate: 90.9% [72.7, 100.0] |
| Kannada | 0.5–1.0 s | C | 11 | base_fp32 | C interrupt rate: 90.9% [72.7, 100.0] |
| Kannada | 0.5–1.0 s | C | 11 | base_int8_dynamic | C interrupt rate: 90.9% [72.7, 100.0] |
| Kannada | 0.5–1.0 s | C | 11 | tiny_int8 | C interrupt rate: 90.9% [72.7, 100.0] |
| Kannada | 1.0 s and over | A | 39 | smartturn_v3.2 | A recall: 92.3% [82.1, 100.0] |
| Kannada | 1.0 s and over | A | 39 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Kannada | 1.0 s and over | A | 39 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Kannada | 1.0 s and over | A | 39 | tiny_int8 | A recall: 89.7% [79.5, 97.4] |
| Kannada | 1.0 s and over | B | 12 | smartturn_v3.2 | B specificity: 41.7% [16.7, 66.7] |
| Kannada | 1.0 s and over | B | 12 | base_fp32 | B specificity: 58.3% [33.3, 83.3] |
| Kannada | 1.0 s and over | B | 12 | base_int8_dynamic | B specificity: 58.3% [33.3, 83.3] |
| Kannada | 1.0 s and over | B | 12 | tiny_int8 | B specificity: 33.3% [8.3, 58.3] |
| Kannada | 1.0 s and over | C | 4 | smartturn_v3.2 | C interrupt rate: 100.0% [100.0, 100.0] |
| Kannada | 1.0 s and over | C | 4 | base_fp32 | C interrupt rate: 100.0% [100.0, 100.0] |
| Kannada | 1.0 s and over | C | 4 | base_int8_dynamic | C interrupt rate: 100.0% [100.0, 100.0] |
| Kannada | 1.0 s and over | C | 4 | tiny_int8 | C interrupt rate: 100.0% [100.0, 100.0] |
| Malayalam | under 0.2 s | A | 0 | smartturn_v3.2 | A recall: n/a |
| Malayalam | under 0.2 s | A | 0 | base_fp32 | A recall: n/a |
| Malayalam | under 0.2 s | A | 0 | base_int8_dynamic | A recall: n/a |
| Malayalam | under 0.2 s | A | 0 | tiny_int8 | A recall: n/a |
| Malayalam | under 0.2 s | B | 30 | smartturn_v3.2 | B specificity: 40.0% [23.3, 56.7] |
| Malayalam | under 0.2 s | B | 30 | base_fp32 | B specificity: 63.3% [46.7, 80.0] |
| Malayalam | under 0.2 s | B | 30 | base_int8_dynamic | B specificity: 60.0% [43.3, 76.7] |
| Malayalam | under 0.2 s | B | 30 | tiny_int8 | B specificity: 56.7% [39.9, 76.7] |
| Malayalam | under 0.2 s | C | 13 | smartturn_v3.2 | C interrupt rate: 61.5% [38.5, 84.6] |
| Malayalam | under 0.2 s | C | 13 | base_fp32 | C interrupt rate: 53.8% [30.8, 76.9] |
| Malayalam | under 0.2 s | C | 13 | base_int8_dynamic | C interrupt rate: 53.8% [23.1, 84.6] |
| Malayalam | under 0.2 s | C | 13 | tiny_int8 | C interrupt rate: 69.2% [46.2, 92.3] |
| Malayalam | 0.2–0.5 s | A | 2 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Malayalam | 0.2–0.5 s | A | 2 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Malayalam | 0.2–0.5 s | A | 2 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Malayalam | 0.2–0.5 s | A | 2 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Malayalam | 0.2–0.5 s | B | 114 | smartturn_v3.2 | B specificity: 39.5% [30.7, 49.1] |
| Malayalam | 0.2–0.5 s | B | 114 | base_fp32 | B specificity: 65.8% [57.9, 74.6] |
| Malayalam | 0.2–0.5 s | B | 114 | base_int8_dynamic | B specificity: 65.8% [57.0, 74.6] |
| Malayalam | 0.2–0.5 s | B | 114 | tiny_int8 | B specificity: 61.4% [51.8, 70.2] |
| Malayalam | 0.2–0.5 s | C | 86 | smartturn_v3.2 | C interrupt rate: 88.4% [81.4, 94.2] |
| Malayalam | 0.2–0.5 s | C | 86 | base_fp32 | C interrupt rate: 89.5% [82.5, 95.3] |
| Malayalam | 0.2–0.5 s | C | 86 | base_int8_dynamic | C interrupt rate: 91.9% [86.0, 97.7] |
| Malayalam | 0.2–0.5 s | C | 86 | tiny_int8 | C interrupt rate: 90.7% [84.9, 96.5] |
| Malayalam | 0.5–1.0 s | A | 7 | smartturn_v3.2 | A recall: 71.4% [42.9, 100.0] |
| Malayalam | 0.5–1.0 s | A | 7 | base_fp32 | A recall: 85.7% [57.1, 100.0] |
| Malayalam | 0.5–1.0 s | A | 7 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Malayalam | 0.5–1.0 s | A | 7 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Malayalam | 0.5–1.0 s | B | 30 | smartturn_v3.2 | B specificity: 56.7% [40.0, 73.3] |
| Malayalam | 0.5–1.0 s | B | 30 | base_fp32 | B specificity: 76.7% [60.0, 90.0] |
| Malayalam | 0.5–1.0 s | B | 30 | base_int8_dynamic | B specificity: 73.3% [56.7, 86.7] |
| Malayalam | 0.5–1.0 s | B | 30 | tiny_int8 | B specificity: 66.7% [50.0, 83.3] |
| Malayalam | 0.5–1.0 s | C | 24 | smartturn_v3.2 | C interrupt rate: 83.3% [66.7, 95.8] |
| Malayalam | 0.5–1.0 s | C | 24 | base_fp32 | C interrupt rate: 91.7% [79.2, 100.0] |
| Malayalam | 0.5–1.0 s | C | 24 | base_int8_dynamic | C interrupt rate: 91.7% [79.2, 100.0] |
| Malayalam | 0.5–1.0 s | C | 24 | tiny_int8 | C interrupt rate: 87.5% [70.8, 100.0] |
| Malayalam | 1.0 s and over | A | 96 | smartturn_v3.2 | A recall: 84.4% [76.0, 91.7] |
| Malayalam | 1.0 s and over | A | 96 | base_fp32 | A recall: 95.8% [91.7, 99.0] |
| Malayalam | 1.0 s and over | A | 96 | base_int8_dynamic | A recall: 96.9% [92.7, 100.0] |
| Malayalam | 1.0 s and over | A | 96 | tiny_int8 | A recall: 90.6% [84.4, 95.8] |
| Malayalam | 1.0 s and over | B | 18 | smartturn_v3.2 | B specificity: 50.0% [27.8, 72.2] |
| Malayalam | 1.0 s and over | B | 18 | base_fp32 | B specificity: 61.1% [38.9, 83.3] |
| Malayalam | 1.0 s and over | B | 18 | base_int8_dynamic | B specificity: 61.1% [38.9, 83.3] |
| Malayalam | 1.0 s and over | B | 18 | tiny_int8 | B specificity: 77.8% [55.6, 94.4] |
| Malayalam | 1.0 s and over | C | 13 | smartturn_v3.2 | C interrupt rate: 69.2% [38.5, 92.3] |
| Malayalam | 1.0 s and over | C | 13 | base_fp32 | C interrupt rate: 100.0% [100.0, 100.0] |
| Malayalam | 1.0 s and over | C | 13 | base_int8_dynamic | C interrupt rate: 100.0% [100.0, 100.0] |
| Malayalam | 1.0 s and over | C | 13 | tiny_int8 | C interrupt rate: 84.6% [61.5, 100.0] |
| Marathi | under 0.2 s | A | 0 | smartturn_v3.2 | A recall: n/a |
| Marathi | under 0.2 s | A | 0 | base_fp32 | A recall: n/a |
| Marathi | under 0.2 s | A | 0 | base_int8_dynamic | A recall: n/a |
| Marathi | under 0.2 s | A | 0 | tiny_int8 | A recall: n/a |
| Marathi | under 0.2 s | B | 72 | smartturn_v3.2 | B specificity: 47.2% [36.1, 59.7] |
| Marathi | under 0.2 s | B | 72 | base_fp32 | B specificity: 77.8% [68.1, 86.1] |
| Marathi | under 0.2 s | B | 72 | base_int8_dynamic | B specificity: 76.4% [66.7, 86.1] |
| Marathi | under 0.2 s | B | 72 | tiny_int8 | B specificity: 76.4% [66.7, 86.1] |
| Marathi | under 0.2 s | C | 18 | smartturn_v3.2 | C interrupt rate: 88.9% [72.2, 100.0] |
| Marathi | under 0.2 s | C | 18 | base_fp32 | C interrupt rate: 66.7% [44.4, 88.9] |
| Marathi | under 0.2 s | C | 18 | base_int8_dynamic | C interrupt rate: 61.1% [38.9, 83.3] |
| Marathi | under 0.2 s | C | 18 | tiny_int8 | C interrupt rate: 72.2% [50.0, 88.9] |
| Marathi | 0.2–0.5 s | A | 13 | smartturn_v3.2 | A recall: 92.3% [76.9, 100.0] |
| Marathi | 0.2–0.5 s | A | 13 | base_fp32 | A recall: 92.3% [76.9, 100.0] |
| Marathi | 0.2–0.5 s | A | 13 | base_int8_dynamic | A recall: 92.3% [76.9, 100.0] |
| Marathi | 0.2–0.5 s | A | 13 | tiny_int8 | A recall: 92.3% [76.9, 100.0] |
| Marathi | 0.2–0.5 s | B | 275 | smartturn_v3.2 | B specificity: 49.8% [44.4, 55.6] |
| Marathi | 0.2–0.5 s | B | 275 | base_fp32 | B specificity: 74.5% [69.4, 80.0] |
| Marathi | 0.2–0.5 s | B | 275 | base_int8_dynamic | B specificity: 74.5% [69.5, 79.6] |
| Marathi | 0.2–0.5 s | B | 275 | tiny_int8 | B specificity: 68.4% [62.9, 73.8] |
| Marathi | 0.2–0.5 s | C | 168 | smartturn_v3.2 | C interrupt rate: 84.5% [78.6, 89.9] |
| Marathi | 0.2–0.5 s | C | 168 | base_fp32 | C interrupt rate: 75.6% [68.5, 82.1] |
| Marathi | 0.2–0.5 s | C | 168 | base_int8_dynamic | C interrupt rate: 75.6% [69.6, 81.5] |
| Marathi | 0.2–0.5 s | C | 168 | tiny_int8 | C interrupt rate: 76.2% [70.2, 82.7] |
| Marathi | 0.5–1.0 s | A | 13 | smartturn_v3.2 | A recall: 84.6% [61.5, 100.0] |
| Marathi | 0.5–1.0 s | A | 13 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Marathi | 0.5–1.0 s | A | 13 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Marathi | 0.5–1.0 s | A | 13 | tiny_int8 | A recall: 92.3% [76.9, 100.0] |
| Marathi | 0.5–1.0 s | B | 76 | smartturn_v3.2 | B specificity: 47.4% [35.5, 57.9] |
| Marathi | 0.5–1.0 s | B | 76 | base_fp32 | B specificity: 69.7% [59.2, 80.3] |
| Marathi | 0.5–1.0 s | B | 76 | base_int8_dynamic | B specificity: 68.4% [57.9, 78.9] |
| Marathi | 0.5–1.0 s | B | 76 | tiny_int8 | B specificity: 60.5% [48.7, 71.1] |
| Marathi | 0.5–1.0 s | C | 70 | smartturn_v3.2 | C interrupt rate: 85.7% [77.1, 92.9] |
| Marathi | 0.5–1.0 s | C | 70 | base_fp32 | C interrupt rate: 81.4% [72.9, 90.0] |
| Marathi | 0.5–1.0 s | C | 70 | base_int8_dynamic | C interrupt rate: 82.9% [74.3, 91.4] |
| Marathi | 0.5–1.0 s | C | 70 | tiny_int8 | C interrupt rate: 75.7% [65.7, 85.7] |
| Marathi | 1.0 s and over | A | 116 | smartturn_v3.2 | A recall: 92.2% [87.1, 96.6] |
| Marathi | 1.0 s and over | A | 116 | base_fp32 | A recall: 89.7% [83.6, 94.8] |
| Marathi | 1.0 s and over | A | 116 | base_int8_dynamic | A recall: 91.4% [85.3, 96.6] |
| Marathi | 1.0 s and over | A | 116 | tiny_int8 | A recall: 88.8% [82.7, 94.8] |
| Marathi | 1.0 s and over | B | 27 | smartturn_v3.2 | B specificity: 44.4% [25.9, 63.0] |
| Marathi | 1.0 s and over | B | 27 | base_fp32 | B specificity: 55.6% [37.0, 74.1] |
| Marathi | 1.0 s and over | B | 27 | base_int8_dynamic | B specificity: 55.6% [37.0, 74.1] |
| Marathi | 1.0 s and over | B | 27 | tiny_int8 | B specificity: 59.3% [40.7, 77.8] |
| Marathi | 1.0 s and over | C | 33 | smartturn_v3.2 | C interrupt rate: 87.9% [75.8, 97.0] |
| Marathi | 1.0 s and over | C | 33 | base_fp32 | C interrupt rate: 97.0% [90.9, 100.0] |
| Marathi | 1.0 s and over | C | 33 | base_int8_dynamic | C interrupt rate: 97.0% [90.9, 100.0] |
| Marathi | 1.0 s and over | C | 33 | tiny_int8 | C interrupt rate: 93.9% [84.8, 100.0] |
| Odia | under 0.2 s | A | 1 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | A | 1 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | A | 1 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | A | 1 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | B | 5 | smartturn_v3.2 | B specificity: 80.0% [40.0, 100.0] |
| Odia | under 0.2 s | B | 5 | base_fp32 | B specificity: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | B | 5 | base_int8_dynamic | B specificity: 80.0% [40.0, 100.0] |
| Odia | under 0.2 s | B | 5 | tiny_int8 | B specificity: 20.0% [0.0, 60.0] |
| Odia | under 0.2 s | C | 1 | smartturn_v3.2 | C interrupt rate: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | C | 1 | base_fp32 | C interrupt rate: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | C | 1 | base_int8_dynamic | C interrupt rate: 100.0% [100.0, 100.0] |
| Odia | under 0.2 s | C | 1 | tiny_int8 | C interrupt rate: 100.0% [100.0, 100.0] |
| Odia | 0.2–0.5 s | A | 4 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Odia | 0.2–0.5 s | A | 4 | base_fp32 | A recall: 75.0% [25.0, 100.0] |
| Odia | 0.2–0.5 s | A | 4 | base_int8_dynamic | A recall: 75.0% [25.0, 100.0] |
| Odia | 0.2–0.5 s | A | 4 | tiny_int8 | A recall: 75.0% [25.0, 100.0] |
| Odia | 0.2–0.5 s | B | 34 | smartturn_v3.2 | B specificity: 52.9% [35.3, 70.6] |
| Odia | 0.2–0.5 s | B | 34 | base_fp32 | B specificity: 67.6% [52.9, 82.4] |
| Odia | 0.2–0.5 s | B | 34 | base_int8_dynamic | B specificity: 70.6% [55.8, 85.3] |
| Odia | 0.2–0.5 s | B | 34 | tiny_int8 | B specificity: 52.9% [35.3, 70.6] |
| Odia | 0.2–0.5 s | C | 14 | smartturn_v3.2 | C interrupt rate: 92.9% [78.6, 100.0] |
| Odia | 0.2–0.5 s | C | 14 | base_fp32 | C interrupt rate: 92.9% [78.6, 100.0] |
| Odia | 0.2–0.5 s | C | 14 | base_int8_dynamic | C interrupt rate: 92.9% [78.6, 100.0] |
| Odia | 0.2–0.5 s | C | 14 | tiny_int8 | C interrupt rate: 92.9% [78.6, 100.0] |
| Odia | 0.5–1.0 s | A | 2 | smartturn_v3.2 | A recall: 0.0% [0.0, 0.0] |
| Odia | 0.5–1.0 s | A | 2 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Odia | 0.5–1.0 s | A | 2 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Odia | 0.5–1.0 s | A | 2 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Odia | 0.5–1.0 s | B | 7 | smartturn_v3.2 | B specificity: 85.7% [57.1, 100.0] |
| Odia | 0.5–1.0 s | B | 7 | base_fp32 | B specificity: 100.0% [100.0, 100.0] |
| Odia | 0.5–1.0 s | B | 7 | base_int8_dynamic | B specificity: 100.0% [100.0, 100.0] |
| Odia | 0.5–1.0 s | B | 7 | tiny_int8 | B specificity: 71.4% [42.9, 100.0] |
| Odia | 0.5–1.0 s | C | 5 | smartturn_v3.2 | C interrupt rate: 80.0% [40.0, 100.0] |
| Odia | 0.5–1.0 s | C | 5 | base_fp32 | C interrupt rate: 100.0% [100.0, 100.0] |
| Odia | 0.5–1.0 s | C | 5 | base_int8_dynamic | C interrupt rate: 100.0% [100.0, 100.0] |
| Odia | 0.5–1.0 s | C | 5 | tiny_int8 | C interrupt rate: 80.0% [40.0, 100.0] |
| Odia | 1.0 s and over | A | 4 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Odia | 1.0 s and over | A | 4 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Odia | 1.0 s and over | A | 4 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Odia | 1.0 s and over | A | 4 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Odia | 1.0 s and over | B | 2 | smartturn_v3.2 | B specificity: 0.0% [0.0, 0.0] |
| Odia | 1.0 s and over | B | 2 | base_fp32 | B specificity: 50.0% [0.0, 100.0] |
| Odia | 1.0 s and over | B | 2 | base_int8_dynamic | B specificity: 50.0% [0.0, 100.0] |
| Odia | 1.0 s and over | B | 2 | tiny_int8 | B specificity: 0.0% [0.0, 0.0] |
| Odia | 1.0 s and over | C | 0 | smartturn_v3.2 | C interrupt rate: n/a |
| Odia | 1.0 s and over | C | 0 | base_fp32 | C interrupt rate: n/a |
| Odia | 1.0 s and over | C | 0 | base_int8_dynamic | C interrupt rate: n/a |
| Odia | 1.0 s and over | C | 0 | tiny_int8 | C interrupt rate: n/a |
| Tamil | under 0.2 s | A | 1 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Tamil | under 0.2 s | A | 1 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Tamil | under 0.2 s | A | 1 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Tamil | under 0.2 s | A | 1 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Tamil | under 0.2 s | B | 54 | smartturn_v3.2 | B specificity: 37.0% [24.1, 50.0] |
| Tamil | under 0.2 s | B | 54 | base_fp32 | B specificity: 70.4% [59.3, 83.3] |
| Tamil | under 0.2 s | B | 54 | base_int8_dynamic | B specificity: 72.2% [59.3, 83.3] |
| Tamil | under 0.2 s | B | 54 | tiny_int8 | B specificity: 64.8% [51.9, 77.8] |
| Tamil | under 0.2 s | C | 17 | smartturn_v3.2 | C interrupt rate: 94.1% [82.4, 100.0] |
| Tamil | under 0.2 s | C | 17 | base_fp32 | C interrupt rate: 76.5% [52.9, 94.1] |
| Tamil | under 0.2 s | C | 17 | base_int8_dynamic | C interrupt rate: 76.5% [52.9, 94.1] |
| Tamil | under 0.2 s | C | 17 | tiny_int8 | C interrupt rate: 88.2% [70.6, 100.0] |
| Tamil | 0.2–0.5 s | A | 7 | smartturn_v3.2 | A recall: 71.4% [28.6, 100.0] |
| Tamil | 0.2–0.5 s | A | 7 | base_fp32 | A recall: 85.7% [57.1, 100.0] |
| Tamil | 0.2–0.5 s | A | 7 | base_int8_dynamic | A recall: 85.7% [57.1, 100.0] |
| Tamil | 0.2–0.5 s | A | 7 | tiny_int8 | A recall: 85.7% [57.1, 100.0] |
| Tamil | 0.2–0.5 s | B | 313 | smartturn_v3.2 | B specificity: 40.3% [34.5, 45.0] |
| Tamil | 0.2–0.5 s | B | 313 | base_fp32 | B specificity: 73.2% [68.4, 78.3] |
| Tamil | 0.2–0.5 s | B | 313 | base_int8_dynamic | B specificity: 71.6% [66.8, 76.0] |
| Tamil | 0.2–0.5 s | B | 313 | tiny_int8 | B specificity: 62.6% [57.2, 68.1] |
| Tamil | 0.2–0.5 s | C | 149 | smartturn_v3.2 | C interrupt rate: 89.9% [85.2, 94.6] |
| Tamil | 0.2–0.5 s | C | 149 | base_fp32 | C interrupt rate: 91.9% [87.2, 96.0] |
| Tamil | 0.2–0.5 s | C | 149 | base_int8_dynamic | C interrupt rate: 90.6% [85.9, 94.6] |
| Tamil | 0.2–0.5 s | C | 149 | tiny_int8 | C interrupt rate: 87.2% [81.2, 92.0] |
| Tamil | 0.5–1.0 s | A | 11 | smartturn_v3.2 | A recall: 90.9% [72.7, 100.0] |
| Tamil | 0.5–1.0 s | A | 11 | base_fp32 | A recall: 90.9% [72.7, 100.0] |
| Tamil | 0.5–1.0 s | A | 11 | base_int8_dynamic | A recall: 90.9% [72.7, 100.0] |
| Tamil | 0.5–1.0 s | A | 11 | tiny_int8 | A recall: 81.8% [54.5, 100.0] |
| Tamil | 0.5–1.0 s | B | 104 | smartturn_v3.2 | B specificity: 44.2% [34.6, 52.9] |
| Tamil | 0.5–1.0 s | B | 104 | base_fp32 | B specificity: 68.3% [59.6, 76.9] |
| Tamil | 0.5–1.0 s | B | 104 | base_int8_dynamic | B specificity: 64.4% [55.8, 74.0] |
| Tamil | 0.5–1.0 s | B | 104 | tiny_int8 | B specificity: 54.8% [45.2, 64.4] |
| Tamil | 0.5–1.0 s | C | 77 | smartturn_v3.2 | C interrupt rate: 84.4% [76.6, 92.2] |
| Tamil | 0.5–1.0 s | C | 77 | base_fp32 | C interrupt rate: 94.8% [88.3, 98.7] |
| Tamil | 0.5–1.0 s | C | 77 | base_int8_dynamic | C interrupt rate: 94.8% [89.6, 98.7] |
| Tamil | 0.5–1.0 s | C | 77 | tiny_int8 | C interrupt rate: 81.8% [72.7, 90.9] |
| Tamil | 1.0 s and over | A | 144 | smartturn_v3.2 | A recall: 93.8% [89.6, 97.2] |
| Tamil | 1.0 s and over | A | 144 | base_fp32 | A recall: 95.8% [92.4, 98.6] |
| Tamil | 1.0 s and over | A | 144 | base_int8_dynamic | A recall: 95.8% [92.4, 98.6] |
| Tamil | 1.0 s and over | A | 144 | tiny_int8 | A recall: 90.3% [85.4, 95.1] |
| Tamil | 1.0 s and over | B | 29 | smartturn_v3.2 | B specificity: 55.2% [34.5, 72.4] |
| Tamil | 1.0 s and over | B | 29 | base_fp32 | B specificity: 79.3% [65.5, 93.1] |
| Tamil | 1.0 s and over | B | 29 | base_int8_dynamic | B specificity: 79.3% [62.1, 93.1] |
| Tamil | 1.0 s and over | B | 29 | tiny_int8 | B specificity: 55.2% [37.9, 72.4] |
| Tamil | 1.0 s and over | C | 19 | smartturn_v3.2 | C interrupt rate: 94.7% [84.2, 100.0] |
| Tamil | 1.0 s and over | C | 19 | base_fp32 | C interrupt rate: 89.5% [73.7, 100.0] |
| Tamil | 1.0 s and over | C | 19 | base_int8_dynamic | C interrupt rate: 84.2% [68.4, 100.0] |
| Tamil | 1.0 s and over | C | 19 | tiny_int8 | C interrupt rate: 73.7% [52.6, 94.7] |
| Telugu | under 0.2 s | A | 2 | smartturn_v3.2 | A recall: 100.0% [100.0, 100.0] |
| Telugu | under 0.2 s | A | 2 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Telugu | under 0.2 s | A | 2 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Telugu | under 0.2 s | A | 2 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Telugu | under 0.2 s | B | 58 | smartturn_v3.2 | B specificity: 51.7% [37.9, 63.8] |
| Telugu | under 0.2 s | B | 58 | base_fp32 | B specificity: 79.3% [69.0, 89.7] |
| Telugu | under 0.2 s | B | 58 | base_int8_dynamic | B specificity: 81.0% [70.7, 89.7] |
| Telugu | under 0.2 s | B | 58 | tiny_int8 | B specificity: 77.6% [67.2, 87.9] |
| Telugu | under 0.2 s | C | 21 | smartturn_v3.2 | C interrupt rate: 100.0% [100.0, 100.0] |
| Telugu | under 0.2 s | C | 21 | base_fp32 | C interrupt rate: 100.0% [100.0, 100.0] |
| Telugu | under 0.2 s | C | 21 | base_int8_dynamic | C interrupt rate: 100.0% [100.0, 100.0] |
| Telugu | under 0.2 s | C | 21 | tiny_int8 | C interrupt rate: 85.7% [71.4, 100.0] |
| Telugu | 0.2–0.5 s | A | 10 | smartturn_v3.2 | A recall: 80.0% [50.0, 100.0] |
| Telugu | 0.2–0.5 s | A | 10 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Telugu | 0.2–0.5 s | A | 10 | base_int8_dynamic | A recall: 90.0% [70.0, 100.0] |
| Telugu | 0.2–0.5 s | A | 10 | tiny_int8 | A recall: 90.0% [70.0, 100.0] |
| Telugu | 0.2–0.5 s | B | 343 | smartturn_v3.2 | B specificity: 53.1% [48.1, 58.0] |
| Telugu | 0.2–0.5 s | B | 343 | base_fp32 | B specificity: 65.9% [60.9, 71.4] |
| Telugu | 0.2–0.5 s | B | 343 | base_int8_dynamic | B specificity: 65.3% [60.1, 70.3] |
| Telugu | 0.2–0.5 s | B | 343 | tiny_int8 | B specificity: 59.8% [54.2, 65.0] |
| Telugu | 0.2–0.5 s | C | 166 | smartturn_v3.2 | C interrupt rate: 86.1% [80.7, 91.6] |
| Telugu | 0.2–0.5 s | C | 166 | base_fp32 | C interrupt rate: 88.0% [83.1, 92.8] |
| Telugu | 0.2–0.5 s | C | 166 | base_int8_dynamic | C interrupt rate: 89.2% [84.3, 93.4] |
| Telugu | 0.2–0.5 s | C | 166 | tiny_int8 | C interrupt rate: 85.5% [80.1, 91.0] |
| Telugu | 0.5–1.0 s | A | 6 | smartturn_v3.2 | A recall: 83.3% [50.0, 100.0] |
| Telugu | 0.5–1.0 s | A | 6 | base_fp32 | A recall: 100.0% [100.0, 100.0] |
| Telugu | 0.5–1.0 s | A | 6 | base_int8_dynamic | A recall: 100.0% [100.0, 100.0] |
| Telugu | 0.5–1.0 s | A | 6 | tiny_int8 | A recall: 100.0% [100.0, 100.0] |
| Telugu | 0.5–1.0 s | B | 135 | smartturn_v3.2 | B specificity: 48.9% [40.0, 57.0] |
| Telugu | 0.5–1.0 s | B | 135 | base_fp32 | B specificity: 68.9% [61.5, 76.3] |
| Telugu | 0.5–1.0 s | B | 135 | base_int8_dynamic | B specificity: 67.4% [60.0, 74.8] |
| Telugu | 0.5–1.0 s | B | 135 | tiny_int8 | B specificity: 63.7% [54.8, 71.9] |
| Telugu | 0.5–1.0 s | C | 83 | smartturn_v3.2 | C interrupt rate: 85.5% [77.1, 92.8] |
| Telugu | 0.5–1.0 s | C | 83 | base_fp32 | C interrupt rate: 94.0% [88.0, 98.8] |
| Telugu | 0.5–1.0 s | C | 83 | base_int8_dynamic | C interrupt rate: 95.2% [90.4, 98.8] |
| Telugu | 0.5–1.0 s | C | 83 | tiny_int8 | C interrupt rate: 80.7% [71.1, 89.2] |
| Telugu | 1.0 s and over | A | 118 | smartturn_v3.2 | A recall: 91.5% [86.4, 95.8] |
| Telugu | 1.0 s and over | A | 118 | base_fp32 | A recall: 94.1% [89.8, 98.3] |
| Telugu | 1.0 s and over | A | 118 | base_int8_dynamic | A recall: 94.1% [89.8, 97.5] |
| Telugu | 1.0 s and over | A | 118 | tiny_int8 | A recall: 92.4% [87.3, 96.6] |
| Telugu | 1.0 s and over | B | 59 | smartturn_v3.2 | B specificity: 49.2% [37.3, 61.1] |
| Telugu | 1.0 s and over | B | 59 | base_fp32 | B specificity: 66.1% [54.2, 78.0] |
| Telugu | 1.0 s and over | B | 59 | base_int8_dynamic | B specificity: 66.1% [54.2, 78.0] |
| Telugu | 1.0 s and over | B | 59 | tiny_int8 | B specificity: 64.4% [52.5, 76.3] |
| Telugu | 1.0 s and over | C | 42 | smartturn_v3.2 | C interrupt rate: 95.2% [88.1, 100.0] |
| Telugu | 1.0 s and over | C | 42 | base_fp32 | C interrupt rate: 88.1% [78.6, 97.6] |
| Telugu | 1.0 s and over | C | 42 | base_int8_dynamic | C interrupt rate: 90.5% [81.0, 97.6] |
| Telugu | 1.0 s and over | C | 42 | tiny_int8 | C interrupt rate: 88.1% [78.5, 97.6] |

## Deployment policy sweep

Each row applies both the minimum-pause gate and model threshold. It reports the desired A recall and the C interruption trade-off; category B is not part of this policy trade-off table.

| language | minimum pause | threshold | A n | C n | model | A recall | C interrupt rate |
|---|---:|---:|---:|---:|---|---:|---:|
| Overall | 0.2 s | 0.5 | 1921 | 3366 | smartturn_v3.2 | 87.8% | 82.4% |
| Overall | 0.2 s | 0.5 | 1921 | 3366 | base_fp32 | 91.3% | 82.7% |
| Overall | 0.2 s | 0.5 | 1921 | 3366 | base_int8_dynamic | 91.4% | 83.1% |
| Overall | 0.2 s | 0.5 | 1921 | 3366 | tiny_int8 | 89.3% | 82.1% |
| Overall | 0.2 s | 0.7 | 1921 | 3366 | smartturn_v3.2 | 82.4% | 76.1% |
| Overall | 0.2 s | 0.7 | 1921 | 3366 | base_fp32 | 90.3% | 81.4% |
| Overall | 0.2 s | 0.7 | 1921 | 3366 | base_int8_dynamic | 90.1% | 81.8% |
| Overall | 0.2 s | 0.7 | 1921 | 3366 | tiny_int8 | 87.2% | 79.5% |
| Overall | 0.2 s | 0.9 | 1921 | 3366 | smartturn_v3.2 | 68.5% | 60.0% |
| Overall | 0.2 s | 0.9 | 1921 | 3366 | base_fp32 | 88.3% | 78.6% |
| Overall | 0.2 s | 0.9 | 1921 | 3366 | base_int8_dynamic | 88.0% | 78.4% |
| Overall | 0.2 s | 0.9 | 1921 | 3366 | tiny_int8 | 82.7% | 73.3% |
| Overall | 0.5 s | 0.5 | 1764 | 1216 | smartturn_v3.2 | 88.2% | 82.6% |
| Overall | 0.5 s | 0.5 | 1764 | 1216 | base_fp32 | 92.1% | 86.1% |
| Overall | 0.5 s | 0.5 | 1764 | 1216 | base_int8_dynamic | 92.4% | 86.7% |
| Overall | 0.5 s | 0.5 | 1764 | 1216 | tiny_int8 | 89.9% | 82.1% |
| Overall | 0.5 s | 0.7 | 1764 | 1216 | smartturn_v3.2 | 82.8% | 76.2% |
| Overall | 0.5 s | 0.7 | 1764 | 1216 | base_fp32 | 91.2% | 84.7% |
| Overall | 0.5 s | 0.7 | 1764 | 1216 | base_int8_dynamic | 90.9% | 85.2% |
| Overall | 0.5 s | 0.7 | 1764 | 1216 | tiny_int8 | 87.7% | 79.9% |
| Overall | 0.5 s | 0.9 | 1764 | 1216 | smartturn_v3.2 | 69.3% | 61.4% |
| Overall | 0.5 s | 0.9 | 1764 | 1216 | base_fp32 | 89.1% | 82.0% |
| Overall | 0.5 s | 0.9 | 1764 | 1216 | base_int8_dynamic | 88.9% | 81.6% |
| Overall | 0.5 s | 0.9 | 1764 | 1216 | tiny_int8 | 83.2% | 74.8% |
| Overall | 1.0 s | 0.5 | 1639 | 326 | smartturn_v3.2 | 88.7% | 86.5% |
| Overall | 1.0 s | 0.5 | 1639 | 326 | base_fp32 | 92.1% | 87.1% |
| Overall | 1.0 s | 0.5 | 1639 | 326 | base_int8_dynamic | 92.4% | 87.4% |
| Overall | 1.0 s | 0.5 | 1639 | 326 | tiny_int8 | 90.1% | 85.9% |
| Overall | 1.0 s | 0.7 | 1639 | 326 | smartturn_v3.2 | 83.5% | 81.6% |
| Overall | 1.0 s | 0.7 | 1639 | 326 | base_fp32 | 91.2% | 85.0% |
| Overall | 1.0 s | 0.7 | 1639 | 326 | base_int8_dynamic | 91.0% | 85.3% |
| Overall | 1.0 s | 0.7 | 1639 | 326 | tiny_int8 | 87.9% | 83.7% |
| Overall | 1.0 s | 0.9 | 1639 | 326 | smartturn_v3.2 | 69.9% | 66.0% |
| Overall | 1.0 s | 0.9 | 1639 | 326 | base_fp32 | 89.2% | 82.8% |
| Overall | 1.0 s | 0.9 | 1639 | 326 | base_int8_dynamic | 89.0% | 81.9% |
| Overall | 1.0 s | 0.9 | 1639 | 326 | tiny_int8 | 83.3% | 78.5% |
| Bengali | 0.2 s | 0.5 | 267 | 605 | smartturn_v3.2 | 94.0% | 91.1% |
| Bengali | 0.2 s | 0.5 | 267 | 605 | base_fp32 | 93.3% | 87.1% |
| Bengali | 0.2 s | 0.5 | 267 | 605 | base_int8_dynamic | 93.3% | 87.4% |
| Bengali | 0.2 s | 0.5 | 267 | 605 | tiny_int8 | 90.3% | 85.5% |
| Bengali | 0.2 s | 0.7 | 267 | 605 | smartturn_v3.2 | 90.6% | 84.6% |
| Bengali | 0.2 s | 0.7 | 267 | 605 | base_fp32 | 92.9% | 85.8% |
| Bengali | 0.2 s | 0.7 | 267 | 605 | base_int8_dynamic | 91.8% | 86.3% |
| Bengali | 0.2 s | 0.7 | 267 | 605 | tiny_int8 | 88.4% | 83.5% |
| Bengali | 0.2 s | 0.9 | 267 | 605 | smartturn_v3.2 | 79.8% | 71.6% |
| Bengali | 0.2 s | 0.9 | 267 | 605 | base_fp32 | 89.1% | 83.8% |
| Bengali | 0.2 s | 0.9 | 267 | 605 | base_int8_dynamic | 88.4% | 83.6% |
| Bengali | 0.2 s | 0.9 | 267 | 605 | tiny_int8 | 82.0% | 77.0% |
| Bengali | 0.5 s | 0.5 | 241 | 200 | smartturn_v3.2 | 93.8% | 92.0% |
| Bengali | 0.5 s | 0.5 | 241 | 200 | base_fp32 | 94.2% | 90.5% |
| Bengali | 0.5 s | 0.5 | 241 | 200 | base_int8_dynamic | 94.6% | 92.0% |
| Bengali | 0.5 s | 0.5 | 241 | 200 | tiny_int8 | 90.9% | 85.0% |
| Bengali | 0.5 s | 0.7 | 241 | 200 | smartturn_v3.2 | 90.5% | 84.5% |
| Bengali | 0.5 s | 0.7 | 241 | 200 | base_fp32 | 94.2% | 88.5% |
| Bengali | 0.5 s | 0.7 | 241 | 200 | base_int8_dynamic | 92.9% | 90.0% |
| Bengali | 0.5 s | 0.7 | 241 | 200 | tiny_int8 | 88.8% | 84.0% |
| Bengali | 0.5 s | 0.9 | 241 | 200 | smartturn_v3.2 | 80.9% | 72.5% |
| Bengali | 0.5 s | 0.9 | 241 | 200 | base_fp32 | 90.9% | 85.5% |
| Bengali | 0.5 s | 0.9 | 241 | 200 | base_int8_dynamic | 90.5% | 86.0% |
| Bengali | 0.5 s | 0.9 | 241 | 200 | tiny_int8 | 82.6% | 80.0% |
| Bengali | 1.0 s | 0.5 | 224 | 60 | smartturn_v3.2 | 93.8% | 98.3% |
| Bengali | 1.0 s | 0.5 | 224 | 60 | base_fp32 | 94.2% | 95.0% |
| Bengali | 1.0 s | 0.5 | 224 | 60 | base_int8_dynamic | 94.6% | 95.0% |
| Bengali | 1.0 s | 0.5 | 224 | 60 | tiny_int8 | 92.4% | 88.3% |
| Bengali | 1.0 s | 0.7 | 224 | 60 | smartturn_v3.2 | 90.2% | 96.7% |
| Bengali | 1.0 s | 0.7 | 224 | 60 | base_fp32 | 94.2% | 91.7% |
| Bengali | 1.0 s | 0.7 | 224 | 60 | base_int8_dynamic | 92.9% | 91.7% |
| Bengali | 1.0 s | 0.7 | 224 | 60 | tiny_int8 | 90.6% | 88.3% |
| Bengali | 1.0 s | 0.9 | 224 | 60 | smartturn_v3.2 | 80.4% | 76.7% |
| Bengali | 1.0 s | 0.9 | 224 | 60 | base_fp32 | 91.1% | 88.3% |
| Bengali | 1.0 s | 0.9 | 224 | 60 | base_int8_dynamic | 90.6% | 86.7% |
| Bengali | 1.0 s | 0.9 | 224 | 60 | tiny_int8 | 84.8% | 83.3% |
| English | 0.2 s | 0.5 | 388 | 613 | smartturn_v3.2 | 76.3% | 68.4% |
| English | 0.2 s | 0.5 | 388 | 613 | base_fp32 | 84.8% | 71.0% |
| English | 0.2 s | 0.5 | 388 | 613 | base_int8_dynamic | 85.3% | 71.3% |
| English | 0.2 s | 0.5 | 388 | 613 | tiny_int8 | 85.1% | 73.1% |
| English | 0.2 s | 0.7 | 388 | 613 | smartturn_v3.2 | 68.8% | 61.8% |
| English | 0.2 s | 0.7 | 388 | 613 | base_fp32 | 82.5% | 68.2% |
| English | 0.2 s | 0.7 | 388 | 613 | base_int8_dynamic | 83.0% | 68.7% |
| English | 0.2 s | 0.7 | 388 | 613 | tiny_int8 | 82.0% | 69.3% |
| English | 0.2 s | 0.9 | 388 | 613 | smartturn_v3.2 | 50.3% | 44.0% |
| English | 0.2 s | 0.9 | 388 | 613 | base_fp32 | 79.1% | 63.5% |
| English | 0.2 s | 0.9 | 388 | 613 | base_int8_dynamic | 78.6% | 63.3% |
| English | 0.2 s | 0.9 | 388 | 613 | tiny_int8 | 77.3% | 63.5% |
| English | 0.5 s | 0.5 | 352 | 224 | smartturn_v3.2 | 76.4% | 68.3% |
| English | 0.5 s | 0.5 | 352 | 224 | base_fp32 | 86.6% | 74.1% |
| English | 0.5 s | 0.5 | 352 | 224 | base_int8_dynamic | 87.2% | 74.6% |
| English | 0.5 s | 0.5 | 352 | 224 | tiny_int8 | 85.8% | 74.1% |
| English | 0.5 s | 0.7 | 352 | 224 | smartturn_v3.2 | 69.3% | 62.5% |
| English | 0.5 s | 0.7 | 352 | 224 | base_fp32 | 84.1% | 71.4% |
| English | 0.5 s | 0.7 | 352 | 224 | base_int8_dynamic | 84.7% | 72.3% |
| English | 0.5 s | 0.7 | 352 | 224 | tiny_int8 | 82.4% | 70.5% |
| English | 0.5 s | 0.9 | 352 | 224 | smartturn_v3.2 | 50.9% | 45.1% |
| English | 0.5 s | 0.9 | 352 | 224 | base_fp32 | 80.4% | 69.6% |
| English | 0.5 s | 0.9 | 352 | 224 | base_int8_dynamic | 79.8% | 68.3% |
| English | 0.5 s | 0.9 | 352 | 224 | tiny_int8 | 77.3% | 65.2% |
| English | 1.0 s | 0.5 | 330 | 55 | smartturn_v3.2 | 77.3% | 74.5% |
| English | 1.0 s | 0.5 | 330 | 55 | base_fp32 | 87.0% | 78.2% |
| English | 1.0 s | 0.5 | 330 | 55 | base_int8_dynamic | 87.6% | 76.4% |
| English | 1.0 s | 0.5 | 330 | 55 | tiny_int8 | 85.8% | 83.6% |
| English | 1.0 s | 0.7 | 330 | 55 | smartturn_v3.2 | 70.6% | 67.3% |
| English | 1.0 s | 0.7 | 330 | 55 | base_fp32 | 84.5% | 72.7% |
| English | 1.0 s | 0.7 | 330 | 55 | base_int8_dynamic | 84.8% | 72.7% |
| English | 1.0 s | 0.7 | 330 | 55 | tiny_int8 | 82.1% | 81.8% |
| English | 1.0 s | 0.9 | 330 | 55 | smartturn_v3.2 | 51.5% | 45.5% |
| English | 1.0 s | 0.9 | 330 | 55 | base_fp32 | 80.9% | 72.7% |
| English | 1.0 s | 0.9 | 330 | 55 | base_int8_dynamic | 80.6% | 70.9% |
| English | 1.0 s | 0.9 | 330 | 55 | tiny_int8 | 77.3% | 76.4% |
| Gujarati | 0.2 s | 0.5 | 280 | 578 | smartturn_v3.2 | 87.9% | 78.5% |
| Gujarati | 0.2 s | 0.5 | 280 | 578 | base_fp32 | 90.0% | 77.3% |
| Gujarati | 0.2 s | 0.5 | 280 | 578 | base_int8_dynamic | 89.6% | 78.4% |
| Gujarati | 0.2 s | 0.5 | 280 | 578 | tiny_int8 | 91.4% | 81.1% |
| Gujarati | 0.2 s | 0.7 | 280 | 578 | smartturn_v3.2 | 82.9% | 70.6% |
| Gujarati | 0.2 s | 0.7 | 280 | 578 | base_fp32 | 89.3% | 76.6% |
| Gujarati | 0.2 s | 0.7 | 280 | 578 | base_int8_dynamic | 89.3% | 76.8% |
| Gujarati | 0.2 s | 0.7 | 280 | 578 | tiny_int8 | 89.3% | 78.7% |
| Gujarati | 0.2 s | 0.9 | 280 | 578 | smartturn_v3.2 | 70.4% | 49.1% |
| Gujarati | 0.2 s | 0.9 | 280 | 578 | base_fp32 | 88.6% | 73.5% |
| Gujarati | 0.2 s | 0.9 | 280 | 578 | base_int8_dynamic | 87.9% | 73.0% |
| Gujarati | 0.2 s | 0.9 | 280 | 578 | tiny_int8 | 82.5% | 70.1% |
| Gujarati | 0.5 s | 0.5 | 262 | 179 | smartturn_v3.2 | 88.5% | 77.7% |
| Gujarati | 0.5 s | 0.5 | 262 | 179 | base_fp32 | 91.2% | 78.2% |
| Gujarati | 0.5 s | 0.5 | 262 | 179 | base_int8_dynamic | 90.8% | 78.8% |
| Gujarati | 0.5 s | 0.5 | 262 | 179 | tiny_int8 | 92.0% | 82.1% |
| Gujarati | 0.5 s | 0.7 | 262 | 179 | smartturn_v3.2 | 83.6% | 70.9% |
| Gujarati | 0.5 s | 0.7 | 262 | 179 | base_fp32 | 90.5% | 77.1% |
| Gujarati | 0.5 s | 0.7 | 262 | 179 | base_int8_dynamic | 90.5% | 76.5% |
| Gujarati | 0.5 s | 0.7 | 262 | 179 | tiny_int8 | 89.7% | 79.9% |
| Gujarati | 0.5 s | 0.9 | 262 | 179 | smartturn_v3.2 | 71.0% | 47.5% |
| Gujarati | 0.5 s | 0.9 | 262 | 179 | base_fp32 | 89.7% | 73.2% |
| Gujarati | 0.5 s | 0.9 | 262 | 179 | base_int8_dynamic | 88.9% | 72.6% |
| Gujarati | 0.5 s | 0.9 | 262 | 179 | tiny_int8 | 83.6% | 73.7% |
| Gujarati | 1.0 s | 0.5 | 250 | 49 | smartturn_v3.2 | 88.0% | 77.6% |
| Gujarati | 1.0 s | 0.5 | 250 | 49 | base_fp32 | 90.8% | 69.4% |
| Gujarati | 1.0 s | 0.5 | 250 | 49 | base_int8_dynamic | 90.4% | 71.4% |
| Gujarati | 1.0 s | 0.5 | 250 | 49 | tiny_int8 | 92.0% | 81.6% |
| Gujarati | 1.0 s | 0.7 | 250 | 49 | smartturn_v3.2 | 82.8% | 69.4% |
| Gujarati | 1.0 s | 0.7 | 250 | 49 | base_fp32 | 90.0% | 65.3% |
| Gujarati | 1.0 s | 0.7 | 250 | 49 | base_int8_dynamic | 90.0% | 67.3% |
| Gujarati | 1.0 s | 0.7 | 250 | 49 | tiny_int8 | 89.6% | 79.6% |
| Gujarati | 1.0 s | 0.9 | 250 | 49 | smartturn_v3.2 | 70.4% | 46.9% |
| Gujarati | 1.0 s | 0.9 | 250 | 49 | base_fp32 | 89.2% | 61.2% |
| Gujarati | 1.0 s | 0.9 | 250 | 49 | base_int8_dynamic | 88.4% | 65.3% |
| Gujarati | 1.0 s | 0.9 | 250 | 49 | tiny_int8 | 83.2% | 71.4% |
| Hindi | 0.2 s | 0.5 | 386 | 531 | smartturn_v3.2 | 91.7% | 84.0% |
| Hindi | 0.2 s | 0.5 | 386 | 531 | base_fp32 | 92.5% | 87.4% |
| Hindi | 0.2 s | 0.5 | 386 | 531 | base_int8_dynamic | 92.2% | 87.4% |
| Hindi | 0.2 s | 0.5 | 386 | 531 | tiny_int8 | 89.4% | 86.1% |
| Hindi | 0.2 s | 0.7 | 386 | 531 | smartturn_v3.2 | 84.7% | 78.0% |
| Hindi | 0.2 s | 0.7 | 386 | 531 | base_fp32 | 92.5% | 86.6% |
| Hindi | 0.2 s | 0.7 | 386 | 531 | base_int8_dynamic | 91.5% | 86.6% |
| Hindi | 0.2 s | 0.7 | 386 | 531 | tiny_int8 | 87.8% | 83.4% |
| Hindi | 0.2 s | 0.9 | 386 | 531 | smartturn_v3.2 | 73.1% | 65.2% |
| Hindi | 0.2 s | 0.9 | 386 | 531 | base_fp32 | 91.2% | 84.4% |
| Hindi | 0.2 s | 0.9 | 386 | 531 | base_int8_dynamic | 91.2% | 84.6% |
| Hindi | 0.2 s | 0.9 | 386 | 531 | tiny_int8 | 83.4% | 78.2% |
| Hindi | 0.5 s | 0.5 | 349 | 232 | smartturn_v3.2 | 92.3% | 85.8% |
| Hindi | 0.5 s | 0.5 | 349 | 232 | base_fp32 | 92.8% | 91.4% |
| Hindi | 0.5 s | 0.5 | 349 | 232 | base_int8_dynamic | 92.8% | 91.4% |
| Hindi | 0.5 s | 0.5 | 349 | 232 | tiny_int8 | 90.3% | 86.2% |
| Hindi | 0.5 s | 0.7 | 349 | 232 | smartturn_v3.2 | 85.1% | 78.9% |
| Hindi | 0.5 s | 0.7 | 349 | 232 | base_fp32 | 92.8% | 90.1% |
| Hindi | 0.5 s | 0.7 | 349 | 232 | base_int8_dynamic | 92.0% | 90.5% |
| Hindi | 0.5 s | 0.7 | 349 | 232 | tiny_int8 | 88.5% | 82.8% |
| Hindi | 0.5 s | 0.9 | 349 | 232 | smartturn_v3.2 | 73.9% | 65.5% |
| Hindi | 0.5 s | 0.9 | 349 | 232 | base_fp32 | 91.4% | 88.4% |
| Hindi | 0.5 s | 0.9 | 349 | 232 | base_int8_dynamic | 91.7% | 87.5% |
| Hindi | 0.5 s | 0.9 | 349 | 232 | tiny_int8 | 84.2% | 77.6% |
| Hindi | 1.0 s | 0.5 | 318 | 51 | smartturn_v3.2 | 93.7% | 86.3% |
| Hindi | 1.0 s | 0.5 | 318 | 51 | base_fp32 | 93.4% | 92.2% |
| Hindi | 1.0 s | 0.5 | 318 | 51 | base_int8_dynamic | 93.4% | 94.1% |
| Hindi | 1.0 s | 0.5 | 318 | 51 | tiny_int8 | 90.9% | 86.3% |
| Hindi | 1.0 s | 0.7 | 318 | 51 | smartturn_v3.2 | 86.8% | 80.4% |
| Hindi | 1.0 s | 0.7 | 318 | 51 | base_fp32 | 93.4% | 92.2% |
| Hindi | 1.0 s | 0.7 | 318 | 51 | base_int8_dynamic | 92.8% | 94.1% |
| Hindi | 1.0 s | 0.7 | 318 | 51 | tiny_int8 | 89.0% | 80.4% |
| Hindi | 1.0 s | 0.9 | 318 | 51 | smartturn_v3.2 | 75.5% | 76.5% |
| Hindi | 1.0 s | 0.9 | 318 | 51 | base_fp32 | 92.1% | 92.2% |
| Hindi | 1.0 s | 0.9 | 318 | 51 | base_int8_dynamic | 92.5% | 88.2% |
| Hindi | 1.0 s | 0.9 | 318 | 51 | tiny_int8 | 84.6% | 80.4% |
| Kannada | 0.2 s | 0.5 | 47 | 90 | smartturn_v3.2 | 91.5% | 88.9% |
| Kannada | 0.2 s | 0.5 | 47 | 90 | base_fp32 | 100.0% | 83.3% |
| Kannada | 0.2 s | 0.5 | 47 | 90 | base_int8_dynamic | 100.0% | 83.3% |
| Kannada | 0.2 s | 0.5 | 47 | 90 | tiny_int8 | 91.5% | 87.8% |
| Kannada | 0.2 s | 0.7 | 47 | 90 | smartturn_v3.2 | 87.2% | 83.3% |
| Kannada | 0.2 s | 0.7 | 47 | 90 | base_fp32 | 100.0% | 82.2% |
| Kannada | 0.2 s | 0.7 | 47 | 90 | base_int8_dynamic | 100.0% | 83.3% |
| Kannada | 0.2 s | 0.7 | 47 | 90 | tiny_int8 | 91.5% | 86.7% |
| Kannada | 0.2 s | 0.9 | 47 | 90 | smartturn_v3.2 | 76.6% | 64.4% |
| Kannada | 0.2 s | 0.9 | 47 | 90 | base_fp32 | 97.9% | 81.1% |
| Kannada | 0.2 s | 0.9 | 47 | 90 | base_int8_dynamic | 100.0% | 80.0% |
| Kannada | 0.2 s | 0.9 | 47 | 90 | tiny_int8 | 91.5% | 80.0% |
| Kannada | 0.5 s | 0.5 | 43 | 15 | smartturn_v3.2 | 93.0% | 93.3% |
| Kannada | 0.5 s | 0.5 | 43 | 15 | base_fp32 | 100.0% | 93.3% |
| Kannada | 0.5 s | 0.5 | 43 | 15 | base_int8_dynamic | 100.0% | 93.3% |
| Kannada | 0.5 s | 0.5 | 43 | 15 | tiny_int8 | 90.7% | 93.3% |
| Kannada | 0.5 s | 0.7 | 43 | 15 | smartturn_v3.2 | 88.4% | 86.7% |
| Kannada | 0.5 s | 0.7 | 43 | 15 | base_fp32 | 100.0% | 93.3% |
| Kannada | 0.5 s | 0.7 | 43 | 15 | base_int8_dynamic | 100.0% | 93.3% |
| Kannada | 0.5 s | 0.7 | 43 | 15 | tiny_int8 | 90.7% | 93.3% |
| Kannada | 0.5 s | 0.9 | 43 | 15 | smartturn_v3.2 | 76.7% | 86.7% |
| Kannada | 0.5 s | 0.9 | 43 | 15 | base_fp32 | 97.7% | 93.3% |
| Kannada | 0.5 s | 0.9 | 43 | 15 | base_int8_dynamic | 100.0% | 93.3% |
| Kannada | 0.5 s | 0.9 | 43 | 15 | tiny_int8 | 90.7% | 93.3% |
| Kannada | 1.0 s | 0.5 | 39 | 4 | smartturn_v3.2 | 92.3% | 100.0% |
| Kannada | 1.0 s | 0.5 | 39 | 4 | base_fp32 | 100.0% | 100.0% |
| Kannada | 1.0 s | 0.5 | 39 | 4 | base_int8_dynamic | 100.0% | 100.0% |
| Kannada | 1.0 s | 0.5 | 39 | 4 | tiny_int8 | 89.7% | 100.0% |
| Kannada | 1.0 s | 0.7 | 39 | 4 | smartturn_v3.2 | 87.2% | 100.0% |
| Kannada | 1.0 s | 0.7 | 39 | 4 | base_fp32 | 100.0% | 100.0% |
| Kannada | 1.0 s | 0.7 | 39 | 4 | base_int8_dynamic | 100.0% | 100.0% |
| Kannada | 1.0 s | 0.7 | 39 | 4 | tiny_int8 | 89.7% | 100.0% |
| Kannada | 1.0 s | 0.9 | 39 | 4 | smartturn_v3.2 | 76.9% | 100.0% |
| Kannada | 1.0 s | 0.9 | 39 | 4 | base_fp32 | 97.4% | 100.0% |
| Kannada | 1.0 s | 0.9 | 39 | 4 | base_int8_dynamic | 100.0% | 100.0% |
| Kannada | 1.0 s | 0.9 | 39 | 4 | tiny_int8 | 89.7% | 100.0% |
| Malayalam | 0.2 s | 0.5 | 105 | 123 | smartturn_v3.2 | 83.8% | 85.4% |
| Malayalam | 0.2 s | 0.5 | 105 | 123 | base_fp32 | 95.2% | 91.1% |
| Malayalam | 0.2 s | 0.5 | 105 | 123 | base_int8_dynamic | 97.1% | 92.7% |
| Malayalam | 0.2 s | 0.5 | 105 | 123 | tiny_int8 | 91.4% | 89.4% |
| Malayalam | 0.2 s | 0.7 | 105 | 123 | smartturn_v3.2 | 80.0% | 77.2% |
| Malayalam | 0.2 s | 0.7 | 105 | 123 | base_fp32 | 94.3% | 91.1% |
| Malayalam | 0.2 s | 0.7 | 105 | 123 | base_int8_dynamic | 95.2% | 91.1% |
| Malayalam | 0.2 s | 0.7 | 105 | 123 | tiny_int8 | 87.6% | 89.4% |
| Malayalam | 0.2 s | 0.9 | 105 | 123 | smartturn_v3.2 | 61.0% | 65.0% |
| Malayalam | 0.2 s | 0.9 | 105 | 123 | base_fp32 | 92.4% | 90.2% |
| Malayalam | 0.2 s | 0.9 | 105 | 123 | base_int8_dynamic | 93.3% | 91.1% |
| Malayalam | 0.2 s | 0.9 | 105 | 123 | tiny_int8 | 86.7% | 78.9% |
| Malayalam | 0.5 s | 0.5 | 103 | 37 | smartturn_v3.2 | 83.5% | 78.4% |
| Malayalam | 0.5 s | 0.5 | 103 | 37 | base_fp32 | 95.1% | 94.6% |
| Malayalam | 0.5 s | 0.5 | 103 | 37 | base_int8_dynamic | 97.1% | 94.6% |
| Malayalam | 0.5 s | 0.5 | 103 | 37 | tiny_int8 | 91.3% | 86.5% |
| Malayalam | 0.5 s | 0.7 | 103 | 37 | smartturn_v3.2 | 79.6% | 67.6% |
| Malayalam | 0.5 s | 0.7 | 103 | 37 | base_fp32 | 94.2% | 94.6% |
| Malayalam | 0.5 s | 0.7 | 103 | 37 | base_int8_dynamic | 95.1% | 94.6% |
| Malayalam | 0.5 s | 0.7 | 103 | 37 | tiny_int8 | 88.3% | 86.5% |
| Malayalam | 0.5 s | 0.9 | 103 | 37 | smartturn_v3.2 | 60.2% | 56.8% |
| Malayalam | 0.5 s | 0.9 | 103 | 37 | base_fp32 | 92.2% | 94.6% |
| Malayalam | 0.5 s | 0.9 | 103 | 37 | base_int8_dynamic | 93.2% | 94.6% |
| Malayalam | 0.5 s | 0.9 | 103 | 37 | tiny_int8 | 87.4% | 73.0% |
| Malayalam | 1.0 s | 0.5 | 96 | 13 | smartturn_v3.2 | 84.4% | 69.2% |
| Malayalam | 1.0 s | 0.5 | 96 | 13 | base_fp32 | 95.8% | 100.0% |
| Malayalam | 1.0 s | 0.5 | 96 | 13 | base_int8_dynamic | 96.9% | 100.0% |
| Malayalam | 1.0 s | 0.5 | 96 | 13 | tiny_int8 | 90.6% | 84.6% |
| Malayalam | 1.0 s | 0.7 | 96 | 13 | smartturn_v3.2 | 81.2% | 61.5% |
| Malayalam | 1.0 s | 0.7 | 96 | 13 | base_fp32 | 94.8% | 100.0% |
| Malayalam | 1.0 s | 0.7 | 96 | 13 | base_int8_dynamic | 95.8% | 100.0% |
| Malayalam | 1.0 s | 0.7 | 96 | 13 | tiny_int8 | 87.5% | 84.6% |
| Malayalam | 1.0 s | 0.9 | 96 | 13 | smartturn_v3.2 | 61.5% | 46.2% |
| Malayalam | 1.0 s | 0.9 | 96 | 13 | base_fp32 | 92.7% | 100.0% |
| Malayalam | 1.0 s | 0.9 | 96 | 13 | base_int8_dynamic | 93.8% | 100.0% |
| Malayalam | 1.0 s | 0.9 | 96 | 13 | tiny_int8 | 86.5% | 76.9% |
| Marathi | 0.2 s | 0.5 | 142 | 271 | smartturn_v3.2 | 91.5% | 85.2% |
| Marathi | 0.2 s | 0.5 | 142 | 271 | base_fp32 | 90.8% | 79.7% |
| Marathi | 0.2 s | 0.5 | 142 | 271 | base_int8_dynamic | 92.3% | 80.1% |
| Marathi | 0.2 s | 0.5 | 142 | 271 | tiny_int8 | 89.4% | 78.2% |
| Marathi | 0.2 s | 0.7 | 142 | 271 | smartturn_v3.2 | 86.6% | 80.4% |
| Marathi | 0.2 s | 0.7 | 142 | 271 | base_fp32 | 90.8% | 77.9% |
| Marathi | 0.2 s | 0.7 | 142 | 271 | base_int8_dynamic | 90.1% | 78.6% |
| Marathi | 0.2 s | 0.7 | 142 | 271 | tiny_int8 | 88.0% | 75.3% |
| Marathi | 0.2 s | 0.9 | 142 | 271 | smartturn_v3.2 | 72.5% | 66.8% |
| Marathi | 0.2 s | 0.9 | 142 | 271 | base_fp32 | 90.1% | 74.2% |
| Marathi | 0.2 s | 0.9 | 142 | 271 | base_int8_dynamic | 90.1% | 74.9% |
| Marathi | 0.2 s | 0.9 | 142 | 271 | tiny_int8 | 84.5% | 71.6% |
| Marathi | 0.5 s | 0.5 | 129 | 103 | smartturn_v3.2 | 91.5% | 86.4% |
| Marathi | 0.5 s | 0.5 | 129 | 103 | base_fp32 | 90.7% | 86.4% |
| Marathi | 0.5 s | 0.5 | 129 | 103 | base_int8_dynamic | 92.2% | 87.4% |
| Marathi | 0.5 s | 0.5 | 129 | 103 | tiny_int8 | 89.1% | 81.6% |
| Marathi | 0.5 s | 0.7 | 129 | 103 | smartturn_v3.2 | 86.0% | 81.6% |
| Marathi | 0.5 s | 0.7 | 129 | 103 | base_fp32 | 90.7% | 84.5% |
| Marathi | 0.5 s | 0.7 | 129 | 103 | base_int8_dynamic | 89.9% | 85.4% |
| Marathi | 0.5 s | 0.7 | 129 | 103 | tiny_int8 | 87.6% | 80.6% |
| Marathi | 0.5 s | 0.9 | 129 | 103 | smartturn_v3.2 | 73.6% | 72.8% |
| Marathi | 0.5 s | 0.9 | 129 | 103 | base_fp32 | 89.9% | 78.6% |
| Marathi | 0.5 s | 0.9 | 129 | 103 | base_int8_dynamic | 89.9% | 79.6% |
| Marathi | 0.5 s | 0.9 | 129 | 103 | tiny_int8 | 84.5% | 77.7% |
| Marathi | 1.0 s | 0.5 | 116 | 33 | smartturn_v3.2 | 92.2% | 87.9% |
| Marathi | 1.0 s | 0.5 | 116 | 33 | base_fp32 | 89.7% | 97.0% |
| Marathi | 1.0 s | 0.5 | 116 | 33 | base_int8_dynamic | 91.4% | 97.0% |
| Marathi | 1.0 s | 0.5 | 116 | 33 | tiny_int8 | 88.8% | 93.9% |
| Marathi | 1.0 s | 0.7 | 116 | 33 | smartturn_v3.2 | 87.1% | 84.8% |
| Marathi | 1.0 s | 0.7 | 116 | 33 | base_fp32 | 89.7% | 97.0% |
| Marathi | 1.0 s | 0.7 | 116 | 33 | base_int8_dynamic | 88.8% | 93.9% |
| Marathi | 1.0 s | 0.7 | 116 | 33 | tiny_int8 | 87.1% | 93.9% |
| Marathi | 1.0 s | 0.9 | 116 | 33 | smartturn_v3.2 | 73.3% | 72.7% |
| Marathi | 1.0 s | 0.9 | 116 | 33 | base_fp32 | 88.8% | 90.9% |
| Marathi | 1.0 s | 0.9 | 116 | 33 | base_int8_dynamic | 88.8% | 90.9% |
| Marathi | 1.0 s | 0.9 | 116 | 33 | tiny_int8 | 83.6% | 87.9% |
| Odia | 0.2 s | 0.5 | 10 | 19 | smartturn_v3.2 | 80.0% | 89.5% |
| Odia | 0.2 s | 0.5 | 10 | 19 | base_fp32 | 90.0% | 94.7% |
| Odia | 0.2 s | 0.5 | 10 | 19 | base_int8_dynamic | 90.0% | 94.7% |
| Odia | 0.2 s | 0.5 | 10 | 19 | tiny_int8 | 90.0% | 89.5% |
| Odia | 0.2 s | 0.7 | 10 | 19 | smartturn_v3.2 | 70.0% | 73.7% |
| Odia | 0.2 s | 0.7 | 10 | 19 | base_fp32 | 90.0% | 89.5% |
| Odia | 0.2 s | 0.7 | 10 | 19 | base_int8_dynamic | 90.0% | 94.7% |
| Odia | 0.2 s | 0.7 | 10 | 19 | tiny_int8 | 90.0% | 89.5% |
| Odia | 0.2 s | 0.9 | 10 | 19 | smartturn_v3.2 | 50.0% | 52.6% |
| Odia | 0.2 s | 0.9 | 10 | 19 | base_fp32 | 90.0% | 84.2% |
| Odia | 0.2 s | 0.9 | 10 | 19 | base_int8_dynamic | 90.0% | 89.5% |
| Odia | 0.2 s | 0.9 | 10 | 19 | tiny_int8 | 90.0% | 89.5% |
| Odia | 0.5 s | 0.5 | 6 | 5 | smartturn_v3.2 | 66.7% | 80.0% |
| Odia | 0.5 s | 0.5 | 6 | 5 | base_fp32 | 100.0% | 100.0% |
| Odia | 0.5 s | 0.5 | 6 | 5 | base_int8_dynamic | 100.0% | 100.0% |
| Odia | 0.5 s | 0.5 | 6 | 5 | tiny_int8 | 100.0% | 80.0% |
| Odia | 0.5 s | 0.7 | 6 | 5 | smartturn_v3.2 | 66.7% | 60.0% |
| Odia | 0.5 s | 0.7 | 6 | 5 | base_fp32 | 100.0% | 100.0% |
| Odia | 0.5 s | 0.7 | 6 | 5 | base_int8_dynamic | 100.0% | 100.0% |
| Odia | 0.5 s | 0.7 | 6 | 5 | tiny_int8 | 100.0% | 80.0% |
| Odia | 0.5 s | 0.9 | 6 | 5 | smartturn_v3.2 | 66.7% | 40.0% |
| Odia | 0.5 s | 0.9 | 6 | 5 | base_fp32 | 100.0% | 80.0% |
| Odia | 0.5 s | 0.9 | 6 | 5 | base_int8_dynamic | 100.0% | 100.0% |
| Odia | 0.5 s | 0.9 | 6 | 5 | tiny_int8 | 100.0% | 80.0% |
| Odia | 1.0 s | 0.5 | 4 | 0 | smartturn_v3.2 | 100.0% | n/a |
| Odia | 1.0 s | 0.5 | 4 | 0 | base_fp32 | 100.0% | n/a |
| Odia | 1.0 s | 0.5 | 4 | 0 | base_int8_dynamic | 100.0% | n/a |
| Odia | 1.0 s | 0.5 | 4 | 0 | tiny_int8 | 100.0% | n/a |
| Odia | 1.0 s | 0.7 | 4 | 0 | smartturn_v3.2 | 100.0% | n/a |
| Odia | 1.0 s | 0.7 | 4 | 0 | base_fp32 | 100.0% | n/a |
| Odia | 1.0 s | 0.7 | 4 | 0 | base_int8_dynamic | 100.0% | n/a |
| Odia | 1.0 s | 0.7 | 4 | 0 | tiny_int8 | 100.0% | n/a |
| Odia | 1.0 s | 0.9 | 4 | 0 | smartturn_v3.2 | 100.0% | n/a |
| Odia | 1.0 s | 0.9 | 4 | 0 | base_fp32 | 100.0% | n/a |
| Odia | 1.0 s | 0.9 | 4 | 0 | base_int8_dynamic | 100.0% | n/a |
| Odia | 1.0 s | 0.9 | 4 | 0 | tiny_int8 | 100.0% | n/a |
| Tamil | 0.2 s | 0.5 | 162 | 245 | smartturn_v3.2 | 92.6% | 88.6% |
| Tamil | 0.2 s | 0.5 | 162 | 245 | base_fp32 | 95.1% | 92.7% |
| Tamil | 0.2 s | 0.5 | 162 | 245 | base_int8_dynamic | 95.1% | 91.4% |
| Tamil | 0.2 s | 0.5 | 162 | 245 | tiny_int8 | 89.5% | 84.5% |
| Tamil | 0.2 s | 0.7 | 162 | 245 | smartturn_v3.2 | 87.7% | 84.5% |
| Tamil | 0.2 s | 0.7 | 162 | 245 | base_fp32 | 95.1% | 91.4% |
| Tamil | 0.2 s | 0.7 | 162 | 245 | base_int8_dynamic | 93.8% | 91.0% |
| Tamil | 0.2 s | 0.7 | 162 | 245 | tiny_int8 | 87.7% | 82.0% |
| Tamil | 0.2 s | 0.9 | 162 | 245 | smartturn_v3.2 | 76.5% | 69.4% |
| Tamil | 0.2 s | 0.9 | 162 | 245 | base_fp32 | 93.2% | 89.0% |
| Tamil | 0.2 s | 0.9 | 162 | 245 | base_int8_dynamic | 92.6% | 86.9% |
| Tamil | 0.2 s | 0.9 | 162 | 245 | tiny_int8 | 84.6% | 78.0% |
| Tamil | 0.5 s | 0.5 | 155 | 96 | smartturn_v3.2 | 93.5% | 86.5% |
| Tamil | 0.5 s | 0.5 | 155 | 96 | base_fp32 | 95.5% | 93.8% |
| Tamil | 0.5 s | 0.5 | 155 | 96 | base_int8_dynamic | 95.5% | 92.7% |
| Tamil | 0.5 s | 0.5 | 155 | 96 | tiny_int8 | 89.7% | 80.2% |
| Tamil | 0.5 s | 0.7 | 155 | 96 | smartturn_v3.2 | 88.4% | 82.3% |
| Tamil | 0.5 s | 0.7 | 155 | 96 | base_fp32 | 95.5% | 93.8% |
| Tamil | 0.5 s | 0.7 | 155 | 96 | base_int8_dynamic | 94.2% | 92.7% |
| Tamil | 0.5 s | 0.7 | 155 | 96 | tiny_int8 | 87.7% | 77.1% |
| Tamil | 0.5 s | 0.9 | 155 | 96 | smartturn_v3.2 | 77.4% | 70.8% |
| Tamil | 0.5 s | 0.9 | 155 | 96 | base_fp32 | 93.5% | 89.6% |
| Tamil | 0.5 s | 0.9 | 155 | 96 | base_int8_dynamic | 92.9% | 87.5% |
| Tamil | 0.5 s | 0.9 | 155 | 96 | tiny_int8 | 84.5% | 71.9% |
| Tamil | 1.0 s | 0.5 | 144 | 19 | smartturn_v3.2 | 93.8% | 94.7% |
| Tamil | 1.0 s | 0.5 | 144 | 19 | base_fp32 | 95.8% | 89.5% |
| Tamil | 1.0 s | 0.5 | 144 | 19 | base_int8_dynamic | 95.8% | 84.2% |
| Tamil | 1.0 s | 0.5 | 144 | 19 | tiny_int8 | 90.3% | 73.7% |
| Tamil | 1.0 s | 0.7 | 144 | 19 | smartturn_v3.2 | 88.9% | 89.5% |
| Tamil | 1.0 s | 0.7 | 144 | 19 | base_fp32 | 95.8% | 89.5% |
| Tamil | 1.0 s | 0.7 | 144 | 19 | base_int8_dynamic | 94.4% | 84.2% |
| Tamil | 1.0 s | 0.7 | 144 | 19 | tiny_int8 | 88.2% | 68.4% |
| Tamil | 1.0 s | 0.9 | 144 | 19 | smartturn_v3.2 | 79.9% | 73.7% |
| Tamil | 1.0 s | 0.9 | 144 | 19 | base_fp32 | 93.8% | 84.2% |
| Tamil | 1.0 s | 0.9 | 144 | 19 | base_int8_dynamic | 93.1% | 78.9% |
| Tamil | 1.0 s | 0.9 | 144 | 19 | tiny_int8 | 84.7% | 63.2% |
| Telugu | 0.2 s | 0.5 | 134 | 291 | smartturn_v3.2 | 90.3% | 87.3% |
| Telugu | 0.2 s | 0.5 | 134 | 291 | base_fp32 | 94.8% | 89.7% |
| Telugu | 0.2 s | 0.5 | 134 | 291 | base_int8_dynamic | 94.0% | 91.1% |
| Telugu | 0.2 s | 0.5 | 134 | 291 | tiny_int8 | 92.5% | 84.5% |
| Telugu | 0.2 s | 0.7 | 134 | 291 | smartturn_v3.2 | 88.1% | 82.1% |
| Telugu | 0.2 s | 0.7 | 134 | 291 | base_fp32 | 91.0% | 89.7% |
| Telugu | 0.2 s | 0.7 | 134 | 291 | base_int8_dynamic | 92.5% | 90.7% |
| Telugu | 0.2 s | 0.7 | 134 | 291 | tiny_int8 | 91.0% | 82.1% |
| Telugu | 0.2 s | 0.9 | 134 | 291 | smartturn_v3.2 | 72.4% | 64.9% |
| Telugu | 0.2 s | 0.9 | 134 | 291 | base_fp32 | 90.3% | 88.0% |
| Telugu | 0.2 s | 0.9 | 134 | 291 | base_int8_dynamic | 89.6% | 88.3% |
| Telugu | 0.2 s | 0.9 | 134 | 291 | tiny_int8 | 86.6% | 76.3% |
| Telugu | 0.5 s | 0.5 | 124 | 125 | smartturn_v3.2 | 91.1% | 88.8% |
| Telugu | 0.5 s | 0.5 | 124 | 125 | base_fp32 | 94.4% | 92.0% |
| Telugu | 0.5 s | 0.5 | 124 | 125 | base_int8_dynamic | 94.4% | 93.6% |
| Telugu | 0.5 s | 0.5 | 124 | 125 | tiny_int8 | 92.7% | 83.2% |
| Telugu | 0.5 s | 0.7 | 124 | 125 | smartturn_v3.2 | 88.7% | 83.2% |
| Telugu | 0.5 s | 0.7 | 124 | 125 | base_fp32 | 91.1% | 92.0% |
| Telugu | 0.5 s | 0.7 | 124 | 125 | base_int8_dynamic | 92.7% | 92.8% |
| Telugu | 0.5 s | 0.7 | 124 | 125 | tiny_int8 | 91.9% | 82.4% |
| Telugu | 0.5 s | 0.9 | 124 | 125 | smartturn_v3.2 | 72.6% | 68.0% |
| Telugu | 0.5 s | 0.9 | 124 | 125 | base_fp32 | 90.3% | 91.2% |
| Telugu | 0.5 s | 0.9 | 124 | 125 | base_int8_dynamic | 89.5% | 91.2% |
| Telugu | 0.5 s | 0.9 | 124 | 125 | tiny_int8 | 87.1% | 78.4% |
| Telugu | 1.0 s | 0.5 | 118 | 42 | smartturn_v3.2 | 91.5% | 95.2% |
| Telugu | 1.0 s | 0.5 | 118 | 42 | base_fp32 | 94.1% | 88.1% |
| Telugu | 1.0 s | 0.5 | 118 | 42 | base_int8_dynamic | 94.1% | 90.5% |
| Telugu | 1.0 s | 0.5 | 118 | 42 | tiny_int8 | 92.4% | 88.1% |
| Telugu | 1.0 s | 0.7 | 118 | 42 | smartturn_v3.2 | 89.0% | 92.9% |
| Telugu | 1.0 s | 0.7 | 118 | 42 | base_fp32 | 90.7% | 88.1% |
| Telugu | 1.0 s | 0.7 | 118 | 42 | base_int8_dynamic | 92.4% | 90.5% |
| Telugu | 1.0 s | 0.7 | 118 | 42 | tiny_int8 | 91.5% | 85.7% |
| Telugu | 1.0 s | 0.9 | 118 | 42 | smartturn_v3.2 | 72.9% | 81.0% |
| Telugu | 1.0 s | 0.9 | 118 | 42 | base_fp32 | 89.8% | 88.1% |
| Telugu | 1.0 s | 0.9 | 118 | 42 | base_int8_dynamic | 89.0% | 88.1% |
| Telugu | 1.0 s | 0.9 | 118 | 42 | tiny_int8 | 87.3% | 78.6% |

## Agent-interruption finding by agent latency

The denominator is Gemini-labeled rule-complete test rows (A + D), so this is a finding about the fixed TTS agent rather than model performance. D is Gemini incomplete despite the recording rule marking a complete turn, and is excluded from model scoring.

| language | agent latency | A + D replies | D replies | D share (95% CI) |
|---|---|---:|---:|---|
| Overall | under 2.0 s | 933 | 470 | 50.4% [47.3, 53.5] |
| Overall | 2.0–3.5 s | 642 | 127 | 19.8% [16.5, 22.7] |
| Overall | 3.5–5.0 s | 1092 | 132 | 12.1% [10.2, 14.1] |
| Bengali | under 2.0 s | 132 | 69 | 52.3% [44.7, 61.4] |
| Bengali | 2.0–3.5 s | 54 | 16 | 29.6% [16.7, 42.6] |
| Bengali | 3.5–5.0 s | 196 | 29 | 14.8% [10.2, 20.4] |
| English | under 2.0 s | 166 | 86 | 51.8% [44.6, 59.6] |
| English | 2.0–3.5 s | 306 | 57 | 18.6% [14.4, 23.2] |
| English | 3.5–5.0 s | 76 | 13 | 17.1% [9.2, 25.0] |
| Gujarati | under 2.0 s | 103 | 48 | 46.6% [36.9, 56.3] |
| Gujarati | 2.0–3.5 s | 67 | 14 | 20.9% [11.9, 31.3] |
| Gujarati | 3.5–5.0 s | 199 | 24 | 12.1% [8.0, 16.6] |
| Hindi | under 2.0 s | 233 | 121 | 51.9% [45.5, 58.4] |
| Hindi | 2.0–3.5 s | 87 | 18 | 20.7% [12.6, 29.9] |
| Hindi | 3.5–5.0 s | 222 | 13 | 5.9% [2.7, 9.0] |
| Kannada | under 2.0 s | 20 | 10 | 50.0% [30.0, 70.0] |
| Kannada | 2.0–3.5 s | 6 | 0 | 0.0% [0.0, 0.0] |
| Kannada | 3.5–5.0 s | 34 | 2 | 5.9% [0.0, 14.7] |
| Malayalam | under 2.0 s | 25 | 9 | 36.0% [16.0, 56.0] |
| Malayalam | 2.0–3.5 s | 27 | 9 | 33.3% [18.5, 51.9] |
| Malayalam | 3.5–5.0 s | 82 | 11 | 13.4% [7.3, 20.7] |
| Marathi | under 2.0 s | 82 | 30 | 36.6% [26.8, 47.6] |
| Marathi | 2.0–3.5 s | 30 | 4 | 13.3% [3.3, 26.7] |
| Marathi | 3.5–5.0 s | 74 | 10 | 13.5% [6.8, 21.6] |
| Odia | under 2.0 s | 23 | 15 | 65.2% [47.8, 82.6] |
| Odia | 2.0–3.5 s | 0 | 0 | n/a |
| Odia | 3.5–5.0 s | 4 | 1 | 25.0% [0.0, 75.0] |
| Tamil | under 2.0 s | 83 | 43 | 51.8% [41.0, 63.9] |
| Tamil | 2.0–3.5 s | 45 | 7 | 15.6% [6.7, 26.7] |
| Tamil | 3.5–5.0 s | 101 | 16 | 15.8% [8.9, 22.8] |
| Telugu | under 2.0 s | 66 | 39 | 59.1% [47.0, 71.2] |
| Telugu | 2.0–3.5 s | 20 | 2 | 10.0% [0.0, 25.0] |
| Telugu | 3.5–5.0 s | 104 | 13 | 12.5% [6.7, 19.2] |

## Public-test reference

These are a fresh local scoring pass over `data/built/*.parquet`, split `test`, using the same model files and fixed 0.5 threshold. They are included only as a public-domain reference and were not used to choose a private-data policy.

| public language | n | model | accuracy | AUC | recall incomplete | recall complete |
|---|---:|---|---:|---:|---:|---:|
| Assamese | 639 | smartturn_v3.2 | 64.9% | 0.691 | 59.6% | 67.5% |
| Assamese | 639 | base_fp32 | 83.6% | 0.892 | 75.0% | 87.7% |
| Assamese | 639 | base_int8_dynamic | 82.9% | 0.893 | 75.0% | 86.8% |
| Assamese | 639 | tiny_int8 | 81.5% | 0.850 | 72.6% | 85.8% |
| Bengali | 482 | smartturn_v3.2 | 75.3% | 0.784 | 65.9% | 78.9% |
| Bengali | 482 | base_fp32 | 87.8% | 0.913 | 78.8% | 91.1% |
| Bengali | 482 | base_int8_dynamic | 87.6% | 0.909 | 79.5% | 90.6% |
| Bengali | 482 | tiny_int8 | 88.0% | 0.916 | 76.5% | 92.3% |
| Gujarati | 498 | smartturn_v3.2 | 72.5% | 0.765 | 66.4% | 74.5% |
| Gujarati | 498 | base_fp32 | 84.7% | 0.895 | 73.6% | 88.5% |
| Gujarati | 498 | base_int8_dynamic | 84.1% | 0.891 | 74.4% | 87.4% |
| Gujarati | 498 | tiny_int8 | 79.9% | 0.849 | 70.4% | 83.1% |
| Hindi | 460 | smartturn_v3.2 | 72.6% | 0.774 | 67.9% | 74.1% |
| Hindi | 460 | base_fp32 | 82.6% | 0.852 | 67.0% | 87.5% |
| Hindi | 460 | base_int8_dynamic | 83.5% | 0.855 | 69.7% | 87.7% |
| Hindi | 460 | tiny_int8 | 83.3% | 0.849 | 67.9% | 88.0% |
| Kannada | 385 | smartturn_v3.2 | 74.0% | 0.783 | 64.0% | 76.5% |
| Kannada | 385 | base_fp32 | 88.6% | 0.921 | 81.3% | 90.3% |
| Kannada | 385 | base_int8_dynamic | 88.3% | 0.921 | 81.3% | 90.0% |
| Kannada | 385 | tiny_int8 | 84.2% | 0.895 | 73.3% | 86.8% |
| Malayalam | 472 | smartturn_v3.2 | 63.8% | 0.664 | 57.3% | 66.1% |
| Malayalam | 472 | base_fp32 | 84.5% | 0.859 | 71.8% | 89.1% |
| Malayalam | 472 | base_int8_dynamic | 83.9% | 0.855 | 71.8% | 88.2% |
| Malayalam | 472 | tiny_int8 | 79.4% | 0.830 | 67.7% | 83.6% |
| Marathi | 537 | smartturn_v3.2 | 70.8% | 0.788 | 73.2% | 69.9% |
| Marathi | 537 | base_fp32 | 88.8% | 0.925 | 82.4% | 91.1% |
| Marathi | 537 | base_int8_dynamic | 88.5% | 0.925 | 81.0% | 91.1% |
| Marathi | 537 | tiny_int8 | 87.9% | 0.925 | 83.1% | 89.6% |
| Odia | 331 | smartturn_v3.2 | 75.2% | 0.778 | 62.4% | 80.3% |
| Odia | 331 | base_fp32 | 88.5% | 0.938 | 75.3% | 93.7% |
| Odia | 331 | base_int8_dynamic | 87.6% | 0.938 | 73.1% | 93.3% |
| Odia | 331 | tiny_int8 | 87.6% | 0.920 | 72.0% | 93.7% |
| Punjabi | 556 | smartturn_v3.2 | 69.4% | 0.749 | 64.6% | 71.4% |
| Punjabi | 556 | base_fp32 | 85.3% | 0.903 | 75.2% | 89.4% |
| Punjabi | 556 | base_int8_dynamic | 85.3% | 0.901 | 74.5% | 89.6% |
| Punjabi | 556 | tiny_int8 | 83.6% | 0.860 | 77.0% | 86.3% |
| Tamil | 300 | smartturn_v3.2 | 66.7% | 0.781 | 73.9% | 65.4% |
| Tamil | 300 | base_fp32 | 90.3% | 0.926 | 80.4% | 92.1% |
| Tamil | 300 | base_int8_dynamic | 91.0% | 0.936 | 80.4% | 92.9% |
| Tamil | 300 | tiny_int8 | 85.7% | 0.909 | 73.9% | 87.8% |
| Telugu | 725 | smartturn_v3.2 | 70.9% | 0.766 | 63.8% | 74.1% |
| Telugu | 725 | base_fp32 | 85.7% | 0.908 | 77.2% | 89.4% |
| Telugu | 725 | base_int8_dynamic | 85.4% | 0.907 | 75.0% | 90.0% |
| Telugu | 725 | tiny_int8 | 87.9% | 0.900 | 82.1% | 90.4% |
