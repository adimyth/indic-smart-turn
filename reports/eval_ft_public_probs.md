# Evaluation report

Models: base_int8_current, ft_int8

## CPU latency

| model | latency (ms, 1 thread, batch 1) |
|---|---:|
| base_int8_current | 138.9 |
| ft_int8 | 139.5 |

## Clean test split

rows: 20431

### By language

| language | n | pos% | model | acc 95% CI | AUC 95% CI | prec(inc) | rec(inc) | rec(comp) |
|---|---:|---:|---|---|---|---:|---:|---:|
| Assamese | 639 | 67 | base_int8_current | 81.8 [78.9, 85.0] | 0.888 [0.857, 0.916] | 69.5 | 78.8 | 83.3 |
| Assamese | 639 | 67 | ft_int8 | 82.8 [79.8, 85.4] | 0.889 [0.860, 0.913] | 72.9 | 75.0 | 86.5 |
| Bengali | 1482 | 57 | base_int8_current | 85.0 [83.1, 86.8] | 0.932 [0.919, 0.944] | 80.3 | 86.6 | 83.8 |
| Bengali | 1482 | 57 | ft_int8 | 81.3 [79.4, 83.3] | 0.935 [0.922, 0.946] | 72.8 | 90.8 | 74.0 |
| English | 7820 | 49 | base_int8_current | 93.2 [92.7, 93.8] | 0.987 [0.984, 0.989] | 91.0 | 96.2 | 90.1 |
| English | 7820 | 49 | ft_int8 | 94.0 [93.5, 94.5] | 0.988 [0.986, 0.990] | 92.6 | 95.9 | 92.0 |
| Gujarati | 498 | 75 | base_int8_current | 82.5 [79.3, 85.7] | 0.891 [0.856, 0.923] | 62.2 | 77.6 | 84.2 |
| Gujarati | 498 | 75 | ft_int8 | 81.9 [78.5, 85.1] | 0.893 [0.854, 0.929] | 60.9 | 78.4 | 83.1 |
| Hindi | 1744 | 58 | base_int8_current | 90.7 [89.2, 91.9] | 0.968 [0.960, 0.975] | 86.6 | 91.7 | 89.9 |
| Hindi | 1744 | 58 | ft_int8 | 88.5 [86.9, 90.0] | 0.970 [0.962, 0.977] | 81.2 | 94.1 | 84.5 |
| Kannada | 385 | 81 | base_int8_current | 87.0 [83.6, 90.1] | 0.923 [0.879, 0.957] | 61.5 | 89.3 | 86.5 |
| Kannada | 385 | 81 | ft_int8 | 86.5 [82.9, 89.9] | 0.923 [0.888, 0.956] | 62.4 | 77.3 | 88.7 |
| Malayalam | 472 | 74 | base_int8_current | 82.6 [78.8, 86.0] | 0.858 [0.810, 0.902] | 64.6 | 75.0 | 85.3 |
| Malayalam | 472 | 74 | ft_int8 | 82.4 [78.8, 85.8] | 0.871 [0.829, 0.909] | 65.0 | 71.8 | 86.2 |
| Marathi | 1311 | 60 | base_int8_current | 88.1 [86.4, 89.8] | 0.951 [0.938, 0.961] | 81.9 | 90.1 | 86.8 |
| Marathi | 1311 | 60 | ft_int8 | 86.9 [85.0, 88.8] | 0.954 [0.943, 0.965] | 78.4 | 92.7 | 83.0 |
| Odia | 331 | 72 | base_int8_current | 89.1 [85.8, 92.4] | 0.937 [0.905, 0.966] | 81.3 | 79.6 | 92.9 |
| Odia | 331 | 72 | ft_int8 | 86.4 [82.8, 90.3] | 0.932 [0.902, 0.961] | 80.0 | 68.8 | 93.3 |
| Punjabi | 556 | 71 | base_int8_current | 82.7 [79.3, 85.4] | 0.894 [0.860, 0.924] | 67.4 | 78.3 | 84.6 |
| Punjabi | 556 | 71 | ft_int8 | 82.2 [79.0, 85.3] | 0.888 [0.855, 0.920] | 65.5 | 81.4 | 82.5 |
| Tamil | 4468 | 65 | base_int8_current | 84.8 [83.8, 85.8] | 0.917 [0.908, 0.926] | 76.6 | 82.1 | 86.2 |
| Tamil | 4468 | 65 | ft_int8 | 82.7 [81.6, 83.8] | 0.922 [0.914, 0.930] | 70.8 | 87.2 | 80.2 |
| Telugu | 725 | 69 | base_int8_current | 85.0 [82.5, 87.4] | 0.910 [0.885, 0.933] | 73.9 | 79.5 | 87.4 |
| Telugu | 725 | 69 | ft_int8 | 85.7 [83.0, 88.1] | 0.923 [0.901, 0.943] | 76.1 | 78.1 | 89.0 |

### By dataset

| dataset | n | pos% | model | acc 95% CI | AUC 95% CI | prec(inc) | rec(inc) | rec(comp) |
|---|---:|---:|---|---|---|---:|---:|---:|
| indicvoices_asm | 503 | 86 | base_int8_current | 82.1 [78.5, 85.5] | 0.865 [0.810, 0.911] | 42.9 | 75.0 | 83.3 |
| indicvoices_asm | 503 | 86 | ft_int8 | 84.3 [81.1, 87.3] | 0.872 [0.822, 0.914] | 46.8 | 70.8 | 86.5 |
| indicvoices_asm_pausecut | 136 | 0 | base_int8_current | 80.9 [75.0, 86.8] | n/a | 100.0 | 80.9 | 0.0 |
| indicvoices_asm_pausecut | 136 | 0 | ft_int8 | 77.2 [69.9, 84.6] | n/a | 100.0 | 77.2 | 0.0 |
| indicvoices_ben | 383 | 91 | base_int8_current | 85.1 [81.5, 88.8] | 0.852 [0.768, 0.923] | 31.8 | 63.6 | 87.1 |
| indicvoices_ben | 383 | 91 | ft_int8 | 87.7 [84.6, 90.6] | 0.872 [0.803, 0.932] | 38.3 | 69.7 | 89.4 |
| indicvoices_ben_pausecut | 99 | 0 | base_int8_current | 87.9 [81.8, 93.9] | n/a | 100.0 | 87.9 | 0.0 |
| indicvoices_ben_pausecut | 99 | 0 | ft_int8 | 84.8 [77.8, 91.9] | n/a | 100.0 | 84.8 | 0.0 |
| indicvoices_guj | 409 | 91 | base_int8_current | 82.4 [78.7, 86.1] | 0.798 [0.713, 0.882] | 28.0 | 63.9 | 84.2 |
| indicvoices_guj | 409 | 91 | ft_int8 | 81.9 [78.2, 85.3] | 0.802 [0.715, 0.885] | 28.4 | 69.4 | 83.1 |
| indicvoices_guj_pausecut | 89 | 0 | base_int8_current | 83.1 [75.3, 91.0] | n/a | 100.0 | 83.1 | 0.0 |
| indicvoices_guj_pausecut | 89 | 0 | ft_int8 | 82.0 [74.2, 89.9] | n/a | 100.0 | 82.0 | 0.0 |
| indicvoices_hin | 384 | 91 | base_int8_current | 85.2 [81.8, 88.5] | 0.773 [0.669, 0.869] | 31.2 | 60.6 | 87.5 |
| indicvoices_hin | 384 | 91 | ft_int8 | 84.4 [80.7, 88.3] | 0.824 [0.729, 0.898] | 29.2 | 57.6 | 86.9 |
| indicvoices_hin_pausecut | 76 | 0 | base_int8_current | 73.7 [64.4, 82.9] | n/a | 100.0 | 73.7 | 0.0 |
| indicvoices_hin_pausecut | 76 | 0 | ft_int8 | 76.3 [67.1, 85.5] | n/a | 100.0 | 76.3 | 0.0 |
| indicvoices_kan | 323 | 96 | base_int8_current | 86.1 [82.7, 89.8] | 0.859 [0.709, 0.969] | 19.2 | 76.9 | 86.5 |
| indicvoices_kan | 323 | 96 | ft_int8 | 87.9 [84.5, 91.0] | 0.873 [0.759, 0.965] | 20.5 | 69.2 | 88.7 |
| indicvoices_kan_pausecut | 62 | 0 | base_int8_current | 91.9 [85.5, 98.4] | n/a | 100.0 | 91.9 | 0.0 |
| indicvoices_kan_pausecut | 62 | 0 | ft_int8 | 79.0 [69.4, 88.7] | n/a | 100.0 | 79.0 | 0.0 |
| indicvoices_mal | 396 | 88 | base_int8_current | 82.8 [78.8, 86.6] | 0.825 [0.747, 0.893] | 37.8 | 64.6 | 85.3 |
| indicvoices_mal | 396 | 88 | ft_int8 | 82.8 [79.0, 86.4] | 0.824 [0.752, 0.889] | 36.8 | 58.3 | 86.2 |
| indicvoices_mal_pausecut | 76 | 0 | base_int8_current | 81.6 [72.4, 89.5] | n/a | 100.0 | 81.6 | 0.0 |
| indicvoices_mal_pausecut | 76 | 0 | ft_int8 | 80.3 [71.1, 88.2] | n/a | 100.0 | 80.3 | 0.0 |
| indicvoices_mar | 444 | 89 | base_int8_current | 86.3 [83.1, 89.4] | 0.912 [0.868, 0.951] | 43.5 | 81.6 | 86.8 |
| indicvoices_mar | 444 | 89 | ft_int8 | 85.4 [82.2, 88.7] | 0.905 [0.856, 0.947] | 41.3 | 77.6 | 86.3 |
| indicvoices_mar_pausecut | 93 | 0 | base_int8_current | 89.2 [82.8, 95.7] | n/a | 100.0 | 89.2 | 0.0 |
| indicvoices_mar_pausecut | 93 | 0 | ft_int8 | 88.2 [80.6, 93.6] | n/a | 100.0 | 88.2 | 0.0 |
| indicvoices_ori | 265 | 90 | base_int8_current | 90.2 [86.4, 93.6] | 0.918 [0.861, 0.960] | 51.4 | 66.7 | 92.9 |
| indicvoices_ori | 265 | 90 | ft_int8 | 89.8 [86.0, 93.2] | 0.918 [0.872, 0.958] | 50.0 | 59.3 | 93.3 |
| indicvoices_ori_pausecut | 66 | 0 | base_int8_current | 84.8 [75.8, 92.4] | n/a | 100.0 | 84.8 | 0.0 |
| indicvoices_ori_pausecut | 66 | 0 | ft_int8 | 72.7 [62.1, 83.3] | n/a | 100.0 | 72.7 | 0.0 |
| indicvoices_pan | 444 | 89 | base_int8_current | 82.9 [79.3, 86.5] | 0.833 [0.758, 0.902] | 35.8 | 69.4 | 84.6 |
| indicvoices_pan | 444 | 89 | ft_int8 | 81.1 [77.7, 84.7] | 0.821 [0.744, 0.888] | 33.0 | 69.4 | 82.5 |
| indicvoices_pan_pausecut | 112 | 0 | base_int8_current | 82.1 [75.0, 89.3] | n/a | 100.0 | 82.1 | 0.0 |
| indicvoices_pan_pausecut | 112 | 0 | ft_int8 | 86.6 [80.4, 92.0] | n/a | 100.0 | 86.6 | 0.0 |
| indicvoices_tam | 269 | 94 | base_int8_current | 90.3 [86.6, 93.3] | 0.909 [0.828, 0.968] | 33.3 | 73.3 | 91.3 |
| indicvoices_tam | 269 | 94 | ft_int8 | 90.0 [86.6, 93.3] | 0.893 [0.767, 0.970] | 33.3 | 80.0 | 90.6 |
| indicvoices_tam_pausecut | 31 | 0 | base_int8_current | 80.6 [67.7, 93.5] | n/a | 100.0 | 80.6 | 0.0 |
| indicvoices_tam_pausecut | 31 | 0 | ft_int8 | 80.6 [67.7, 93.5] | n/a | 100.0 | 80.6 | 0.0 |
| indicvoices_tel | 567 | 88 | base_int8_current | 85.0 [82.0, 87.8] | 0.857 [0.799, 0.910] | 41.1 | 66.7 | 87.4 |
| indicvoices_tel | 567 | 88 | ft_int8 | 86.6 [83.8, 89.2] | 0.883 [0.832, 0.929] | 45.0 | 68.2 | 89.0 |
| indicvoices_tel_pausecut | 158 | 0 | base_int8_current | 84.8 [79.1, 90.5] | n/a | 100.0 | 84.8 | 0.0 |
| indicvoices_tel_pausecut | 158 | 0 | ft_int8 | 82.3 [75.9, 88.0] | n/a | 100.0 | 82.3 | 0.0 |
| smart-turn-data-v3.2-test:train | 10878 | 50 | base_int8_current | 92.1 [91.6, 92.6] | 0.981 [0.979, 0.983] | 90.0 | 95.0 | 89.2 |
| smart-turn-data-v3.2-test:train | 10878 | 50 | ft_int8 | 91.7 [91.1, 92.2] | 0.984 [0.982, 0.985] | 88.6 | 95.9 | 87.4 |
| tamil-eot:test | 4168 | 63 | base_int8_current | 84.5 [83.3, 85.6] | 0.916 [0.906, 0.925] | 77.1 | 82.3 | 85.7 |
| tamil-eot:test | 4168 | 63 | ft_int8 | 82.2 [81.1, 83.4] | 0.920 [0.912, 0.929] | 71.1 | 87.4 | 79.2 |

### Overall

| model | acc | AUC |
|---|---:|---:|
| base_int8_current | 88.6 | 0.953 |
| ft_int8 | 87.9 | 0.957 |
