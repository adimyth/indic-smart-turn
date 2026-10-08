# Evaluation report

Models: base_fp32, base_int8_minmax, base_int8_dynamic, base_int8_percentile

## CPU latency

| model | latency (ms, 1 thread, batch 1) |
|---|---:|
| base_fp32 | 189.9 |
| base_int8_minmax | 137.4 |
| base_int8_dynamic | 122.4 |
| base_int8_percentile | 135.9 |

## Clean test split

rows: 9553

### By language

| language | n | pos% | model | acc 95% CI | AUC 95% CI | prec(inc) | rec(inc) | rec(comp) |
|---|---:|---:|---|---|---|---:|---:|---:|
| Assamese | 639 | 67 | base_fp32 | 83.6 [80.6, 86.5] | 0.892 [0.862, 0.921] | 74.6 | 75.0 | 87.7 |
| Assamese | 639 | 67 | base_int8_minmax | 76.8 [73.6, 80.0] | 0.849 [0.817, 0.879] | 62.0 | 74.5 | 78.0 |
| Assamese | 639 | 67 | base_int8_dynamic | 81.8 [79.0, 84.7] | 0.888 [0.859, 0.914] | 69.5 | 78.8 | 83.3 |
| Assamese | 639 | 67 | base_int8_percentile | 83.7 [80.8, 86.5] | 0.889 [0.861, 0.915] | 75.2 | 74.5 | 88.2 |
| Bengali | 482 | 73 | base_fp32 | 87.8 [84.6, 90.7] | 0.913 [0.879, 0.943] | 77.0 | 78.8 | 91.1 |
| Bengali | 482 | 73 | base_int8_minmax | 84.6 [81.3, 87.8] | 0.903 [0.870, 0.934] | 68.4 | 81.8 | 85.7 |
| Bengali | 482 | 73 | base_int8_dynamic | 85.7 [82.4, 88.8] | 0.914 [0.883, 0.942] | 70.6 | 81.8 | 87.1 |
| Bengali | 482 | 73 | base_int8_percentile | 87.3 [84.2, 90.2] | 0.899 [0.864, 0.934] | 77.1 | 76.5 | 91.4 |
| Gujarati | 498 | 75 | base_fp32 | 84.7 [81.5, 88.0] | 0.895 [0.861, 0.926] | 68.1 | 73.6 | 88.5 |
| Gujarati | 498 | 75 | base_int8_minmax | 81.1 [77.3, 84.5] | 0.861 [0.815, 0.900] | 60.8 | 69.6 | 85.0 |
| Gujarati | 498 | 75 | base_int8_dynamic | 82.5 [78.9, 85.7] | 0.891 [0.853, 0.924] | 62.2 | 77.6 | 84.2 |
| Gujarati | 498 | 75 | base_int8_percentile | 84.9 [81.7, 88.2] | 0.889 [0.851, 0.921] | 68.1 | 75.2 | 88.2 |
| Hindi | 460 | 76 | base_fp32 | 82.6 [78.9, 85.9] | 0.852 [0.802, 0.897] | 62.4 | 67.0 | 87.5 |
| Hindi | 460 | 76 | base_int8_minmax | 80.4 [77.0, 84.1] | 0.851 [0.807, 0.894] | 56.6 | 74.3 | 82.3 |
| Hindi | 460 | 76 | base_int8_dynamic | 83.3 [79.8, 86.5] | 0.863 [0.816, 0.903] | 63.3 | 69.7 | 87.5 |
| Hindi | 460 | 76 | base_int8_percentile | 82.4 [78.7, 85.9] | 0.845 [0.796, 0.888] | 61.5 | 68.8 | 86.6 |
| Kannada | 385 | 81 | base_fp32 | 88.6 [85.2, 91.7] | 0.921 [0.878, 0.955] | 67.0 | 81.3 | 90.3 |
| Kannada | 385 | 81 | base_int8_minmax | 83.9 [80.0, 87.5] | 0.900 [0.852, 0.940] | 56.0 | 81.3 | 84.5 |
| Kannada | 385 | 81 | base_int8_dynamic | 87.0 [83.6, 90.4] | 0.923 [0.881, 0.957] | 61.5 | 89.3 | 86.5 |
| Kannada | 385 | 81 | base_int8_percentile | 87.3 [83.9, 90.6] | 0.912 [0.871, 0.950] | 63.3 | 82.7 | 88.4 |
| Malayalam | 472 | 74 | base_fp32 | 84.5 [80.9, 87.7] | 0.859 [0.811, 0.906] | 70.1 | 71.8 | 89.1 |
| Malayalam | 472 | 74 | base_int8_minmax | 76.1 [72.5, 79.9] | 0.801 [0.754, 0.848] | 53.4 | 70.2 | 78.2 |
| Malayalam | 472 | 74 | base_int8_dynamic | 82.6 [78.8, 85.8] | 0.858 [0.813, 0.901] | 64.6 | 75.0 | 85.3 |
| Malayalam | 472 | 74 | base_int8_percentile | 82.4 [79.0, 86.0] | 0.853 [0.809, 0.893] | 65.2 | 71.0 | 86.5 |
| Marathi | 537 | 74 | base_fp32 | 88.8 [86.0, 91.2] | 0.925 [0.895, 0.947] | 77.0 | 82.4 | 91.1 |
| Marathi | 537 | 74 | base_int8_minmax | 85.3 [82.3, 88.3] | 0.902 [0.872, 0.933] | 70.1 | 77.5 | 88.1 |
| Marathi | 537 | 74 | base_int8_dynamic | 86.8 [83.8, 89.6] | 0.921 [0.891, 0.948] | 70.3 | 86.6 | 86.8 |
| Marathi | 537 | 74 | base_int8_percentile | 89.4 [86.8, 92.0] | 0.925 [0.896, 0.951] | 79.7 | 80.3 | 92.7 |
| Odia | 331 | 72 | base_fp32 | 88.5 [85.2, 91.8] | 0.938 [0.907, 0.966] | 82.4 | 75.3 | 93.7 |
| Odia | 331 | 72 | base_int8_minmax | 86.4 [82.8, 90.0] | 0.896 [0.849, 0.936] | 73.5 | 80.6 | 88.7 |
| Odia | 331 | 72 | base_int8_dynamic | 89.1 [85.5, 92.4] | 0.937 [0.903, 0.966] | 81.3 | 79.6 | 92.9 |
| Odia | 331 | 72 | base_int8_percentile | 87.0 [83.4, 90.6] | 0.928 [0.896, 0.956] | 80.5 | 71.0 | 93.3 |
| Punjabi | 556 | 71 | base_fp32 | 85.3 [82.2, 87.9] | 0.903 [0.872, 0.930] | 74.2 | 75.2 | 89.4 |
| Punjabi | 556 | 71 | base_int8_minmax | 76.6 [73.2, 80.0] | 0.829 [0.788, 0.868] | 57.6 | 72.7 | 78.2 |
| Punjabi | 556 | 71 | base_int8_dynamic | 82.7 [79.5, 85.6] | 0.894 [0.861, 0.924] | 67.4 | 78.3 | 84.6 |
| Punjabi | 556 | 71 | base_int8_percentile | 81.8 [78.6, 84.9] | 0.861 [0.824, 0.895] | 67.4 | 72.0 | 85.8 |
| Tamil | 4468 | 65 | base_fp32 | 86.2 [85.2, 87.2] | 0.918 [0.909, 0.927] | 83.1 | 76.7 | 91.4 |
| Tamil | 4468 | 65 | base_int8_minmax | 81.3 [80.1, 82.4] | 0.877 [0.866, 0.887] | 73.5 | 73.9 | 85.3 |
| Tamil | 4468 | 65 | base_int8_dynamic | 84.8 [83.8, 85.9] | 0.917 [0.908, 0.927] | 76.7 | 82.1 | 86.3 |
| Tamil | 4468 | 65 | base_int8_percentile | 85.3 [84.2, 86.3] | 0.907 [0.897, 0.916] | 80.4 | 77.4 | 89.7 |
| Telugu | 725 | 69 | base_fp32 | 85.7 [83.3, 88.0] | 0.908 [0.884, 0.932] | 76.5 | 77.2 | 89.4 |
| Telugu | 725 | 69 | base_int8_minmax | 81.4 [78.5, 84.1] | 0.871 [0.840, 0.900] | 71.5 | 66.1 | 88.2 |
| Telugu | 725 | 69 | base_int8_dynamic | 85.0 [82.3, 87.3] | 0.910 [0.884, 0.933] | 73.9 | 79.5 | 87.4 |
| Telugu | 725 | 69 | base_int8_percentile | 85.7 [83.0, 88.1] | 0.908 [0.883, 0.931] | 77.5 | 75.4 | 90.2 |

### By dataset

| dataset | n | pos% | model | acc 95% CI | AUC 95% CI | prec(inc) | rec(inc) | rec(comp) |
|---|---:|---:|---|---|---|---:|---:|---:|
| indicvoices_asm | 503 | 86 | base_fp32 | 85.5 [82.3, 88.7] | 0.870 [0.814, 0.916] | 49.5 | 72.2 | 87.7 |
| indicvoices_asm | 503 | 86 | base_int8_minmax | 76.7 [73.0, 80.3] | 0.819 [0.764, 0.868] | 34.5 | 69.4 | 78.0 |
| indicvoices_asm | 503 | 86 | base_int8_dynamic | 82.1 [78.7, 85.5] | 0.865 [0.808, 0.909] | 42.9 | 75.0 | 83.3 |
| indicvoices_asm | 503 | 86 | base_int8_percentile | 85.5 [82.5, 88.5] | 0.860 [0.807, 0.907] | 49.5 | 69.4 | 88.2 |
| indicvoices_asm_pausecut | 136 | 0 | base_fp32 | 76.5 [69.9, 83.1] | n/a | 100.0 | 76.5 | 0.0 |
| indicvoices_asm_pausecut | 136 | 0 | base_int8_minmax | 77.2 [69.9, 83.8] | n/a | 100.0 | 77.2 | 0.0 |
| indicvoices_asm_pausecut | 136 | 0 | base_int8_dynamic | 80.9 [73.5, 87.5] | n/a | 100.0 | 80.9 | 0.0 |
| indicvoices_asm_pausecut | 136 | 0 | base_int8_percentile | 77.2 [70.6, 83.8] | n/a | 100.0 | 77.2 | 0.0 |
| indicvoices_ben | 383 | 91 | base_fp32 | 88.8 [85.4, 91.9] | 0.850 [0.767, 0.921] | 40.4 | 63.6 | 91.1 |
| indicvoices_ben | 383 | 91 | base_int8_minmax | 84.3 [80.7, 87.7] | 0.829 [0.743, 0.907] | 31.5 | 69.7 | 85.7 |
| indicvoices_ben | 383 | 91 | base_int8_dynamic | 85.1 [81.5, 88.5] | 0.852 [0.769, 0.926] | 31.8 | 63.6 | 87.1 |
| indicvoices_ben | 383 | 91 | base_int8_percentile | 88.8 [85.4, 91.9] | 0.834 [0.747, 0.912] | 40.0 | 60.6 | 91.4 |
| indicvoices_ben_pausecut | 99 | 0 | base_fp32 | 83.8 [76.8, 89.9] | n/a | 100.0 | 83.8 | 0.0 |
| indicvoices_ben_pausecut | 99 | 0 | base_int8_minmax | 85.9 [78.8, 92.9] | n/a | 100.0 | 85.9 | 0.0 |
| indicvoices_ben_pausecut | 99 | 0 | base_int8_dynamic | 87.9 [80.8, 93.9] | n/a | 100.0 | 87.9 | 0.0 |
| indicvoices_ben_pausecut | 99 | 0 | base_int8_percentile | 81.8 [73.7, 88.9] | n/a | 100.0 | 81.8 | 0.0 |
| indicvoices_guj | 409 | 91 | base_fp32 | 85.6 [82.2, 88.8] | 0.818 [0.744, 0.892] | 31.7 | 55.6 | 88.5 |
| indicvoices_guj | 409 | 91 | base_int8_minmax | 82.4 [79.0, 85.8] | 0.766 [0.685, 0.846] | 26.3 | 55.6 | 85.0 |
| indicvoices_guj | 409 | 91 | base_int8_dynamic | 82.4 [78.5, 85.8] | 0.798 [0.699, 0.882] | 28.0 | 63.9 | 84.2 |
| indicvoices_guj | 409 | 91 | base_int8_percentile | 86.3 [82.9, 89.7] | 0.811 [0.723, 0.893] | 35.3 | 66.7 | 88.2 |
| indicvoices_guj_pausecut | 89 | 0 | base_fp32 | 80.9 [73.0, 88.8] | n/a | 100.0 | 80.9 | 0.0 |
| indicvoices_guj_pausecut | 89 | 0 | base_int8_minmax | 75.3 [66.3, 83.1] | n/a | 100.0 | 75.3 | 0.0 |
| indicvoices_guj_pausecut | 89 | 0 | base_int8_dynamic | 83.1 [75.3, 91.0] | n/a | 100.0 | 83.1 | 0.0 |
| indicvoices_guj_pausecut | 89 | 0 | base_int8_percentile | 78.7 [69.7, 86.5] | n/a | 100.0 | 78.7 | 0.0 |
| indicvoices_hin | 384 | 91 | base_fp32 | 84.9 [81.2, 88.3] | 0.748 [0.632, 0.854] | 30.2 | 57.6 | 87.5 |
| indicvoices_hin | 384 | 91 | base_int8_minmax | 80.2 [76.3, 84.1] | 0.797 [0.713, 0.872] | 23.5 | 57.6 | 82.3 |
| indicvoices_hin | 384 | 91 | base_int8_dynamic | 85.2 [81.5, 88.3] | 0.773 [0.667, 0.869] | 31.2 | 60.6 | 87.5 |
| indicvoices_hin | 384 | 91 | base_int8_percentile | 83.9 [80.2, 87.2] | 0.762 [0.662, 0.860] | 27.7 | 54.5 | 86.6 |
| indicvoices_hin_pausecut | 76 | 0 | base_fp32 | 71.1 [60.5, 80.3] | n/a | 100.0 | 71.1 | 0.0 |
| indicvoices_hin_pausecut | 76 | 0 | base_int8_minmax | 81.6 [72.4, 89.5] | n/a | 100.0 | 81.6 | 0.0 |
| indicvoices_hin_pausecut | 76 | 0 | base_int8_dynamic | 73.7 [63.2, 82.9] | n/a | 100.0 | 73.7 | 0.0 |
| indicvoices_hin_pausecut | 76 | 0 | base_int8_percentile | 75.0 [64.5, 84.2] | n/a | 100.0 | 75.0 | 0.0 |
| indicvoices_kan | 323 | 96 | base_fp32 | 89.5 [86.4, 92.9] | 0.845 [0.671, 0.968] | 23.1 | 69.2 | 90.3 |
| indicvoices_kan | 323 | 96 | base_int8_minmax | 84.2 [80.5, 87.9] | 0.858 [0.708, 0.971] | 17.2 | 76.9 | 84.5 |
| indicvoices_kan | 323 | 96 | base_int8_dynamic | 86.1 [82.3, 89.5] | 0.859 [0.720, 0.972] | 19.2 | 76.9 | 86.5 |
| indicvoices_kan | 323 | 96 | base_int8_percentile | 87.9 [84.2, 91.3] | 0.845 [0.679, 0.963] | 21.7 | 76.9 | 88.4 |
| indicvoices_kan_pausecut | 62 | 0 | base_fp32 | 83.9 [74.2, 91.9] | n/a | 100.0 | 83.9 | 0.0 |
| indicvoices_kan_pausecut | 62 | 0 | base_int8_minmax | 82.3 [71.0, 91.9] | n/a | 100.0 | 82.3 | 0.0 |
| indicvoices_kan_pausecut | 62 | 0 | base_int8_dynamic | 91.9 [85.5, 98.4] | n/a | 100.0 | 91.9 | 0.0 |
| indicvoices_kan_pausecut | 62 | 0 | base_int8_percentile | 83.9 [74.2, 91.9] | n/a | 100.0 | 83.9 | 0.0 |
| indicvoices_mal | 396 | 88 | base_fp32 | 85.6 [81.8, 89.1] | 0.821 [0.740, 0.891] | 43.3 | 60.4 | 89.1 |
| indicvoices_mal | 396 | 88 | base_int8_minmax | 76.8 [72.5, 80.8] | 0.771 [0.700, 0.838] | 29.6 | 66.7 | 78.2 |
| indicvoices_mal | 396 | 88 | base_int8_dynamic | 82.8 [78.8, 86.6] | 0.825 [0.752, 0.891] | 37.8 | 64.6 | 85.3 |
| indicvoices_mal | 396 | 88 | base_int8_percentile | 83.1 [79.5, 86.6] | 0.813 [0.742, 0.884] | 37.3 | 58.3 | 86.5 |
| indicvoices_mal_pausecut | 76 | 0 | base_fp32 | 78.9 [68.4, 88.2] | n/a | 100.0 | 78.9 | 0.0 |
| indicvoices_mal_pausecut | 76 | 0 | base_int8_minmax | 72.4 [61.8, 82.9] | n/a | 100.0 | 72.4 | 0.0 |
| indicvoices_mal_pausecut | 76 | 0 | base_int8_dynamic | 81.6 [72.4, 89.5] | n/a | 100.0 | 81.6 | 0.0 |
| indicvoices_mal_pausecut | 76 | 0 | base_int8_percentile | 78.9 [69.7, 86.8] | n/a | 100.0 | 78.9 | 0.0 |
| indicvoices_mar | 444 | 89 | base_fp32 | 89.6 [86.7, 92.3] | 0.919 [0.879, 0.954] | 52.1 | 77.6 | 91.1 |
| indicvoices_mar | 444 | 89 | base_int8_minmax | 86.5 [83.3, 89.6] | 0.881 [0.825, 0.936] | 43.4 | 73.5 | 88.1 |
| indicvoices_mar | 444 | 89 | base_int8_dynamic | 86.3 [82.9, 89.4] | 0.912 [0.867, 0.950] | 43.5 | 81.6 | 86.8 |
| indicvoices_mar | 444 | 89 | base_int8_percentile | 90.5 [87.6, 93.0] | 0.912 [0.857, 0.957] | 55.4 | 73.5 | 92.7 |
| indicvoices_mar_pausecut | 93 | 0 | base_fp32 | 84.9 [77.4, 91.4] | n/a | 100.0 | 84.9 | 0.0 |
| indicvoices_mar_pausecut | 93 | 0 | base_int8_minmax | 79.6 [71.0, 88.2] | n/a | 100.0 | 79.6 | 0.0 |
| indicvoices_mar_pausecut | 93 | 0 | base_int8_dynamic | 89.2 [82.8, 94.6] | n/a | 100.0 | 89.2 | 0.0 |
| indicvoices_mar_pausecut | 93 | 0 | base_int8_percentile | 83.9 [76.3, 90.3] | n/a | 100.0 | 83.9 | 0.0 |
| indicvoices_ori | 265 | 90 | base_fp32 | 89.8 [86.0, 93.6] | 0.907 [0.845, 0.957] | 50.0 | 55.6 | 93.7 |
| indicvoices_ori | 265 | 90 | base_int8_minmax | 87.2 [83.0, 90.9] | 0.868 [0.778, 0.945] | 42.6 | 74.1 | 88.7 |
| indicvoices_ori | 265 | 90 | base_int8_dynamic | 90.2 [86.8, 93.6] | 0.918 [0.871, 0.961] | 51.4 | 66.7 | 92.9 |
| indicvoices_ori | 265 | 90 | base_int8_percentile | 89.1 [84.9, 92.8] | 0.896 [0.838, 0.944] | 46.7 | 51.9 | 93.3 |
| indicvoices_ori_pausecut | 66 | 0 | base_fp32 | 83.3 [75.8, 90.9] | n/a | 100.0 | 83.3 | 0.0 |
| indicvoices_ori_pausecut | 66 | 0 | base_int8_minmax | 83.3 [74.2, 90.9] | n/a | 100.0 | 83.3 | 0.0 |
| indicvoices_ori_pausecut | 66 | 0 | base_int8_dynamic | 84.8 [75.8, 92.4] | n/a | 100.0 | 84.8 | 0.0 |
| indicvoices_ori_pausecut | 66 | 0 | base_int8_percentile | 78.8 [68.2, 87.9] | n/a | 100.0 | 78.8 | 0.0 |
| indicvoices_pan | 444 | 89 | base_fp32 | 86.7 [83.6, 89.9] | 0.855 [0.793, 0.912] | 43.2 | 65.3 | 89.4 |
| indicvoices_pan | 444 | 89 | base_int8_minmax | 76.1 [72.1, 80.0] | 0.764 [0.679, 0.845] | 25.2 | 59.2 | 78.2 |
| indicvoices_pan | 444 | 89 | base_int8_dynamic | 82.9 [79.5, 86.5] | 0.833 [0.758, 0.899] | 35.8 | 69.4 | 84.6 |
| indicvoices_pan | 444 | 89 | base_int8_percentile | 83.6 [80.2, 87.2] | 0.791 [0.709, 0.875] | 36.4 | 65.3 | 85.8 |
| indicvoices_pan_pausecut | 112 | 0 | base_fp32 | 79.5 [72.3, 86.6] | n/a | 100.0 | 79.5 | 0.0 |
| indicvoices_pan_pausecut | 112 | 0 | base_int8_minmax | 78.6 [70.5, 85.7] | n/a | 100.0 | 78.6 | 0.0 |
| indicvoices_pan_pausecut | 112 | 0 | base_int8_dynamic | 82.1 [75.0, 89.3] | n/a | 100.0 | 82.1 | 0.0 |
| indicvoices_pan_pausecut | 112 | 0 | base_int8_percentile | 75.0 [66.1, 82.1] | n/a | 100.0 | 75.0 | 0.0 |
| indicvoices_tam | 269 | 94 | base_fp32 | 91.1 [87.7, 94.1] | 0.901 [0.802, 0.974] | 35.5 | 73.3 | 92.1 |
| indicvoices_tam | 269 | 94 | base_int8_minmax | 89.2 [85.9, 92.9] | 0.886 [0.757, 0.970] | 31.6 | 80.0 | 89.8 |
| indicvoices_tam | 269 | 94 | base_int8_dynamic | 90.3 [86.6, 93.7] | 0.909 [0.832, 0.976] | 33.3 | 73.3 | 91.3 |
| indicvoices_tam | 269 | 94 | base_int8_percentile | 90.7 [87.0, 94.1] | 0.884 [0.730, 0.989] | 35.3 | 80.0 | 91.3 |
| indicvoices_tam_pausecut | 31 | 0 | base_fp32 | 83.9 [71.0, 93.5] | n/a | 100.0 | 83.9 | 0.0 |
| indicvoices_tam_pausecut | 31 | 0 | base_int8_minmax | 80.6 [67.7, 93.5] | n/a | 100.0 | 80.6 | 0.0 |
| indicvoices_tam_pausecut | 31 | 0 | base_int8_dynamic | 80.6 [64.5, 93.5] | n/a | 100.0 | 80.6 | 0.0 |
| indicvoices_tam_pausecut | 31 | 0 | base_int8_percentile | 80.6 [64.5, 93.5] | n/a | 100.0 | 80.6 | 0.0 |
| indicvoices_tel | 567 | 88 | base_fp32 | 86.6 [83.8, 89.4] | 0.859 [0.800, 0.911] | 44.8 | 65.2 | 89.4 |
| indicvoices_tel | 567 | 88 | base_int8_minmax | 84.1 [81.0, 86.9] | 0.794 [0.721, 0.854] | 37.2 | 53.0 | 88.2 |
| indicvoices_tel | 567 | 88 | base_int8_dynamic | 85.0 [82.0, 87.8] | 0.857 [0.795, 0.908] | 41.1 | 66.7 | 87.4 |
| indicvoices_tel | 567 | 88 | base_int8_percentile | 87.3 [84.7, 90.1] | 0.846 [0.782, 0.904] | 46.7 | 65.2 | 90.2 |
| indicvoices_tel_pausecut | 158 | 0 | base_fp32 | 82.3 [76.6, 88.0] | n/a | 100.0 | 82.3 | 0.0 |
| indicvoices_tel_pausecut | 158 | 0 | base_int8_minmax | 71.5 [64.6, 78.5] | n/a | 100.0 | 71.5 | 0.0 |
| indicvoices_tel_pausecut | 158 | 0 | base_int8_dynamic | 84.8 [79.1, 89.9] | n/a | 100.0 | 84.8 | 0.0 |
| indicvoices_tel_pausecut | 158 | 0 | base_int8_percentile | 79.7 [72.8, 86.1] | n/a | 100.0 | 79.7 | 0.0 |
| tamil-eot:test | 4168 | 63 | base_fp32 | 85.9 [84.9, 86.9] | 0.917 [0.908, 0.926] | 83.8 | 76.5 | 91.4 |
| tamil-eot:test | 4168 | 63 | base_int8_minmax | 80.8 [79.7, 81.9] | 0.876 [0.865, 0.887] | 74.1 | 73.7 | 84.9 |
| tamil-eot:test | 4168 | 63 | base_int8_dynamic | 84.5 [83.4, 85.6] | 0.916 [0.907, 0.925] | 77.2 | 82.2 | 85.8 |
| tamil-eot:test | 4168 | 63 | base_int8_percentile | 85.0 [84.0, 86.1] | 0.906 [0.896, 0.916] | 81.2 | 77.3 | 89.5 |

### Overall

| model | acc | AUC |
|---|---:|---:|
| base_fp32 | 86.0 | 0.909 |
| base_int8_minmax | 81.1 | 0.869 |
| base_int8_dynamic | 84.6 | 0.909 |
| base_int8_percentile | 85.2 | 0.898 |
