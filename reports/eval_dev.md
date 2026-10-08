# Evaluation report

Models: base_fp32, base_int8_dynamic, tiny_int8

## CPU latency

| model | latency (ms, 1 thread, batch 1) |
|---|---:|
| base_fp32 | 257.9 |
| base_int8_dynamic | 195.2 |
| tiny_int8 | 145.4 |

## Clean test split

rows: 4706

### By language

| language | n | pos% | model | acc 95% CI | AUC 95% CI | prec(inc) | rec(inc) | rec(comp) |
|---|---:|---:|---|---|---|---:|---:|---:|
| Assamese | 388 | 69 | base_fp32 | 81.7 [77.8, 85.6] | 0.839 [0.788, 0.886] | 73.4 | 65.6 | 89.1 |
| Assamese | 388 | 69 | base_int8_dynamic | 80.9 [76.5, 84.5] | 0.844 [0.793, 0.891] | 68.5 | 73.0 | 84.6 |
| Assamese | 388 | 69 | tiny_int8 | 78.1 [74.0, 82.2] | 0.800 [0.745, 0.852] | 66.4 | 61.5 | 85.7 |
| Bengali | 717 | 69 | base_fp32 | 84.5 [81.7, 87.0] | 0.897 [0.868, 0.922] | 78.2 | 69.4 | 91.3 |
| Bengali | 717 | 69 | base_int8_dynamic | 84.5 [81.6, 87.2] | 0.895 [0.867, 0.921] | 74.4 | 76.1 | 88.3 |
| Bengali | 717 | 69 | tiny_int8 | 83.3 [80.3, 85.9] | 0.873 [0.844, 0.900] | 76.0 | 67.1 | 90.5 |
| Gujarati | 368 | 59 | base_fp32 | 81.5 [77.4, 85.3] | 0.876 [0.837, 0.911] | 81.1 | 71.3 | 88.5 |
| Gujarati | 368 | 59 | base_int8_dynamic | 79.6 [75.3, 83.7] | 0.879 [0.844, 0.916] | 73.9 | 77.3 | 81.2 |
| Gujarati | 368 | 59 | tiny_int8 | 81.5 [77.7, 85.6] | 0.865 [0.824, 0.906] | 78.9 | 74.7 | 86.2 |
| Hindi | 527 | 68 | base_fp32 | 83.9 [81.0, 87.1] | 0.899 [0.870, 0.929] | 77.1 | 71.2 | 89.9 |
| Hindi | 527 | 68 | base_int8_dynamic | 83.7 [80.5, 86.5] | 0.882 [0.847, 0.912] | 72.8 | 78.8 | 86.0 |
| Hindi | 527 | 68 | tiny_int8 | 78.7 [75.3, 82.2] | 0.834 [0.796, 0.869] | 67.7 | 65.3 | 85.2 |
| Kannada | 371 | 75 | base_fp32 | 85.7 [82.2, 89.2] | 0.865 [0.812, 0.910] | 75.7 | 61.5 | 93.6 |
| Kannada | 371 | 75 | base_int8_dynamic | 83.0 [79.5, 86.5] | 0.871 [0.823, 0.913] | 65.6 | 64.8 | 88.9 |
| Kannada | 371 | 75 | tiny_int8 | 84.6 [80.9, 88.1] | 0.836 [0.778, 0.885] | 69.8 | 65.9 | 90.7 |
| Malayalam | 376 | 74 | base_fp32 | 82.4 [78.5, 86.4] | 0.858 [0.812, 0.901] | 66.7 | 66.7 | 88.1 |
| Malayalam | 376 | 74 | base_int8_dynamic | 78.5 [73.9, 82.4] | 0.850 [0.799, 0.893] | 57.5 | 69.7 | 81.6 |
| Malayalam | 376 | 74 | tiny_int8 | 80.9 [76.6, 84.8] | 0.833 [0.786, 0.876] | 64.2 | 61.6 | 87.7 |
| Marathi | 521 | 66 | base_fp32 | 80.2 [76.4, 83.7] | 0.853 [0.815, 0.889] | 73.2 | 67.0 | 87.1 |
| Marathi | 521 | 66 | base_int8_dynamic | 80.2 [76.6, 83.7] | 0.844 [0.804, 0.879] | 70.4 | 73.2 | 83.9 |
| Marathi | 521 | 66 | tiny_int8 | 75.6 [72.0, 79.3] | 0.802 [0.760, 0.843] | 65.7 | 60.9 | 83.3 |
| Odia | 248 | 73 | base_fp32 | 80.6 [76.2, 85.5] | 0.818 [0.756, 0.877] | 66.7 | 56.7 | 89.5 |
| Odia | 248 | 73 | base_int8_dynamic | 80.2 [75.0, 84.7] | 0.815 [0.747, 0.874] | 64.1 | 61.2 | 87.3 |
| Odia | 248 | 73 | tiny_int8 | 76.6 [71.4, 81.5] | 0.751 [0.672, 0.828] | 58.2 | 47.8 | 87.3 |
| Punjabi | 366 | 69 | base_fp32 | 83.3 [79.5, 87.2] | 0.882 [0.842, 0.918] | 73.6 | 71.7 | 88.5 |
| Punjabi | 366 | 69 | base_int8_dynamic | 82.0 [78.1, 85.5] | 0.883 [0.842, 0.919] | 68.8 | 76.1 | 84.6 |
| Punjabi | 366 | 69 | tiny_int8 | 80.6 [76.5, 84.4] | 0.834 [0.783, 0.879] | 67.8 | 70.8 | 85.0 |
| Tamil | 226 | 73 | base_fp32 | 90.3 [86.3, 93.8] | 0.920 [0.869, 0.963] | 86.5 | 75.0 | 95.8 |
| Tamil | 226 | 73 | base_int8_dynamic | 88.9 [84.5, 92.9] | 0.928 [0.880, 0.967] | 77.8 | 81.7 | 91.6 |
| Tamil | 226 | 73 | tiny_int8 | 82.3 [77.0, 87.6] | 0.847 [0.784, 0.905] | 67.2 | 65.0 | 88.6 |
| Telugu | 598 | 72 | base_fp32 | 84.9 [82.1, 87.8] | 0.866 [0.827, 0.900] | 77.3 | 65.3 | 92.6 |
| Telugu | 598 | 72 | base_int8_dynamic | 82.8 [79.8, 85.6] | 0.863 [0.825, 0.897] | 69.8 | 67.7 | 88.6 |
| Telugu | 598 | 72 | tiny_int8 | 81.1 [77.9, 83.9] | 0.860 [0.827, 0.891] | 67.8 | 61.7 | 88.6 |

### By dataset

| dataset | n | pos% | model | acc 95% CI | AUC 95% CI | prec(inc) | rec(inc) | rec(comp) |
|---|---:|---:|---|---|---|---:|---:|---:|
| indicvoices_asm | 314 | 85 | base_fp32 | 83.4 [79.3, 87.6] | 0.774 [0.693, 0.848] | 46.3 | 52.1 | 89.1 |
| indicvoices_asm | 314 | 85 | base_int8_dynamic | 80.6 [76.1, 84.7] | 0.787 [0.707, 0.860] | 40.6 | 58.3 | 84.6 |
| indicvoices_asm | 314 | 85 | tiny_int8 | 80.3 [75.8, 84.7] | 0.730 [0.642, 0.818] | 38.7 | 50.0 | 85.7 |
| indicvoices_asm_pausecut | 74 | 0 | base_fp32 | 74.3 [63.5, 83.8] | n/a | 100.0 | 74.3 | 0.0 |
| indicvoices_asm_pausecut | 74 | 0 | base_int8_dynamic | 82.4 [73.0, 90.5] | n/a | 100.0 | 82.4 | 0.0 |
| indicvoices_asm_pausecut | 74 | 0 | tiny_int8 | 68.9 [59.5, 79.7] | n/a | 100.0 | 68.9 | 0.0 |
| indicvoices_ben | 581 | 85 | base_fp32 | 86.1 [83.1, 88.8] | 0.841 [0.784, 0.889] | 52.7 | 55.8 | 91.3 |
| indicvoices_ben | 581 | 85 | base_int8_dynamic | 85.2 [82.4, 88.1] | 0.843 [0.791, 0.887] | 50.0 | 67.4 | 88.3 |
| indicvoices_ben | 581 | 85 | tiny_int8 | 85.4 [82.3, 88.1] | 0.835 [0.784, 0.881] | 50.5 | 55.8 | 90.5 |
| indicvoices_ben_pausecut | 136 | 0 | base_fp32 | 77.9 [70.6, 84.6] | n/a | 100.0 | 77.9 | 0.0 |
| indicvoices_ben_pausecut | 136 | 0 | base_int8_dynamic | 81.6 [74.3, 88.2] | n/a | 100.0 | 81.6 | 0.0 |
| indicvoices_ben_pausecut | 136 | 0 | tiny_int8 | 74.3 [66.9, 80.9] | n/a | 100.0 | 74.3 | 0.0 |
| indicvoices_guj | 282 | 77 | base_fp32 | 84.0 [79.8, 88.3] | 0.868 [0.812, 0.918] | 63.8 | 68.8 | 88.5 |
| indicvoices_guj | 282 | 77 | base_int8_dynamic | 80.5 [75.9, 84.8] | 0.879 [0.825, 0.925] | 54.9 | 78.1 | 81.2 |
| indicvoices_guj | 282 | 77 | tiny_int8 | 83.3 [78.7, 87.6] | 0.858 [0.794, 0.910] | 61.0 | 73.4 | 86.2 |
| indicvoices_guj_pausecut | 86 | 0 | base_fp32 | 73.3 [62.8, 82.6] | n/a | 100.0 | 73.3 | 0.0 |
| indicvoices_guj_pausecut | 86 | 0 | base_int8_dynamic | 76.7 [68.6, 84.9] | n/a | 100.0 | 76.7 | 0.0 |
| indicvoices_guj_pausecut | 86 | 0 | tiny_int8 | 75.6 [66.3, 84.9] | n/a | 100.0 | 75.6 | 0.0 |
| indicvoices_hin | 430 | 83 | base_fp32 | 84.4 [80.9, 87.4] | 0.841 [0.784, 0.891] | 53.8 | 57.5 | 89.9 |
| indicvoices_hin | 430 | 83 | base_int8_dynamic | 83.3 [79.8, 86.7] | 0.821 [0.754, 0.878] | 50.5 | 69.9 | 86.0 |
| indicvoices_hin | 430 | 83 | tiny_int8 | 79.5 [75.8, 83.5] | 0.755 [0.684, 0.817] | 41.8 | 52.1 | 85.2 |
| indicvoices_hin_pausecut | 97 | 0 | base_fp32 | 81.4 [73.2, 88.7] | n/a | 100.0 | 81.4 | 0.0 |
| indicvoices_hin_pausecut | 97 | 0 | base_int8_dynamic | 85.6 [78.3, 92.8] | n/a | 100.0 | 85.6 | 0.0 |
| indicvoices_hin_pausecut | 97 | 0 | tiny_int8 | 75.3 [67.0, 83.5] | n/a | 100.0 | 75.3 | 0.0 |
| indicvoices_kan | 318 | 88 | base_fp32 | 87.1 [83.6, 90.6] | 0.770 [0.674, 0.858] | 45.5 | 39.5 | 93.6 |
| indicvoices_kan | 318 | 88 | base_int8_dynamic | 83.0 [78.6, 87.1] | 0.772 [0.683, 0.851] | 32.6 | 39.5 | 88.9 |
| indicvoices_kan | 318 | 88 | tiny_int8 | 84.6 [80.5, 88.1] | 0.718 [0.616, 0.812] | 36.6 | 39.5 | 90.7 |
| indicvoices_kan_pausecut | 53 | 0 | base_fp32 | 77.4 [66.0, 88.7] | n/a | 100.0 | 77.4 | 0.0 |
| indicvoices_kan_pausecut | 53 | 0 | base_int8_dynamic | 83.0 [73.6, 92.5] | n/a | 100.0 | 83.0 | 0.0 |
| indicvoices_kan_pausecut | 53 | 0 | tiny_int8 | 84.9 [73.6, 94.3] | n/a | 100.0 | 84.9 | 0.0 |
| indicvoices_mal | 319 | 87 | base_fp32 | 83.4 [79.3, 87.1] | 0.805 [0.735, 0.874] | 40.0 | 52.4 | 88.1 |
| indicvoices_mal | 319 | 87 | base_int8_dynamic | 77.7 [73.0, 82.4] | 0.795 [0.721, 0.868] | 30.1 | 52.4 | 81.6 |
| indicvoices_mal | 319 | 87 | tiny_int8 | 82.4 [78.1, 86.2] | 0.772 [0.682, 0.845] | 37.0 | 47.6 | 87.7 |
| indicvoices_mal_pausecut | 57 | 0 | base_fp32 | 77.2 [64.9, 87.7] | n/a | 100.0 | 77.2 | 0.0 |
| indicvoices_mal_pausecut | 57 | 0 | base_int8_dynamic | 82.5 [71.9, 91.2] | n/a | 100.0 | 82.5 | 0.0 |
| indicvoices_mal_pausecut | 57 | 0 | tiny_int8 | 71.9 [59.6, 82.5] | n/a | 100.0 | 71.9 | 0.0 |
| indicvoices_mar | 413 | 83 | base_fp32 | 82.3 [78.7, 86.0] | 0.803 [0.737, 0.865] | 48.8 | 59.2 | 87.1 |
| indicvoices_mar | 413 | 83 | base_int8_dynamic | 81.4 [77.5, 85.0] | 0.798 [0.733, 0.859] | 47.1 | 69.0 | 83.9 |
| indicvoices_mar | 413 | 83 | tiny_int8 | 78.0 [73.8, 82.1] | 0.745 [0.676, 0.809] | 39.4 | 52.1 | 83.3 |
| indicvoices_mar_pausecut | 108 | 0 | base_fp32 | 72.2 [63.9, 80.6] | n/a | 100.0 | 72.2 | 0.0 |
| indicvoices_mar_pausecut | 108 | 0 | base_int8_dynamic | 75.9 [68.5, 84.3] | n/a | 100.0 | 75.9 | 0.0 |
| indicvoices_mar_pausecut | 108 | 0 | tiny_int8 | 66.7 [57.4, 75.0] | n/a | 100.0 | 66.7 | 0.0 |
| indicvoices_ori | 219 | 83 | base_fp32 | 81.7 [76.7, 86.8] | 0.772 [0.676, 0.849] | 47.2 | 44.7 | 89.5 |
| indicvoices_ori | 219 | 83 | base_int8_dynamic | 80.8 [75.3, 85.8] | 0.781 [0.699, 0.858] | 45.2 | 50.0 | 87.3 |
| indicvoices_ori | 219 | 83 | tiny_int8 | 79.5 [73.1, 84.9] | 0.695 [0.577, 0.796] | 41.0 | 42.1 | 87.3 |
| indicvoices_ori_pausecut | 29 | 0 | base_fp32 | 72.4 [55.2, 89.7] | n/a | 100.0 | 72.4 | 0.0 |
| indicvoices_ori_pausecut | 29 | 0 | base_int8_dynamic | 75.9 [62.1, 89.7] | n/a | 100.0 | 75.9 | 0.0 |
| indicvoices_ori_pausecut | 29 | 0 | tiny_int8 | 55.2 [37.9, 72.4] | n/a | 100.0 | 55.2 | 0.0 |
| indicvoices_pan | 293 | 86 | base_fp32 | 83.6 [79.2, 87.7] | 0.821 [0.748, 0.885] | 42.0 | 52.5 | 88.5 |
| indicvoices_pan | 293 | 86 | base_int8_dynamic | 80.9 [76.4, 85.3] | 0.809 [0.729, 0.883] | 37.1 | 57.5 | 84.6 |
| indicvoices_pan | 293 | 86 | tiny_int8 | 79.9 [75.1, 84.0] | 0.736 [0.655, 0.802] | 33.3 | 47.5 | 85.0 |
| indicvoices_pan_pausecut | 73 | 0 | base_fp32 | 82.2 [72.6, 90.4] | n/a | 100.0 | 82.2 | 0.0 |
| indicvoices_pan_pausecut | 73 | 0 | base_int8_dynamic | 86.3 [78.1, 93.2] | n/a | 100.0 | 86.3 | 0.0 |
| indicvoices_pan_pausecut | 73 | 0 | tiny_int8 | 83.6 [75.3, 91.8] | n/a | 100.0 | 83.6 | 0.0 |
| indicvoices_tam | 195 | 85 | base_fp32 | 91.8 [87.7, 95.4] | 0.884 [0.779, 0.959] | 74.1 | 69.0 | 95.8 |
| indicvoices_tam | 195 | 85 | base_int8_dynamic | 89.7 [85.6, 93.8] | 0.889 [0.803, 0.965] | 62.2 | 79.3 | 91.6 |
| indicvoices_tam | 195 | 85 | tiny_int8 | 83.6 [78.4, 88.7] | 0.786 [0.672, 0.883] | 45.7 | 55.2 | 88.6 |
| indicvoices_tam_pausecut | 31 | 0 | base_fp32 | 80.6 [64.5, 93.5] | n/a | 100.0 | 80.6 | 0.0 |
| indicvoices_tam_pausecut | 31 | 0 | base_int8_dynamic | 83.9 [71.0, 96.8] | n/a | 100.0 | 83.9 | 0.0 |
| indicvoices_tam_pausecut | 31 | 0 | tiny_int8 | 74.2 [58.1, 90.3] | n/a | 100.0 | 74.2 | 0.0 |
| indicvoices_tel | 502 | 86 | base_fp32 | 87.5 [84.5, 90.2] | 0.818 [0.754, 0.876] | 55.6 | 56.3 | 92.6 |
| indicvoices_tel | 502 | 86 | base_int8_dynamic | 84.5 [81.1, 87.5] | 0.811 [0.739, 0.873] | 46.2 | 59.2 | 88.6 |
| indicvoices_tel | 502 | 86 | tiny_int8 | 82.9 [79.7, 86.1] | 0.809 [0.757, 0.861] | 41.0 | 47.9 | 88.6 |
| indicvoices_tel_pausecut | 96 | 0 | base_fp32 | 71.9 [62.5, 80.2] | n/a | 100.0 | 71.9 | 0.0 |
| indicvoices_tel_pausecut | 96 | 0 | base_int8_dynamic | 74.0 [64.6, 82.3] | n/a | 100.0 | 74.0 | 0.0 |
| indicvoices_tel_pausecut | 96 | 0 | tiny_int8 | 71.9 [62.5, 80.2] | n/a | 100.0 | 71.9 | 0.0 |

### Overall

| model | acc | AUC |
|---|---:|---:|
| base_fp32 | 83.5 | 0.873 |
| base_int8_dynamic | 82.2 | 0.871 |
| tiny_int8 | 80.4 | 0.838 |
