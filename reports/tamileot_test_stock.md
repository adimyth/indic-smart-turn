# Evaluation report

rows: 4168; models: v32cpu, v32gpu, tamil_base_int8

| model | CPU latency (ms, 1 thread, batch 1) |
|---|---|
| v32cpu | 40.4 |
| v32gpu | 26.2 |
| tamil_base_int8 | 48.4 |

## By language

| language | n | pos% | model | acc | AUC | prec(inc) | rec(inc) | rec(comp) |
|---|---|---|---|---|---|---|---|---|
| Tamil | 4168 | 63 | v32cpu | 70.2 | 0.749 | 59.0 | 63.5 | 74.1 |
| Tamil | 4168 | 63 | v32gpu | 59.4 | 0.743 | 47.1 | 81.1 | 46.7 |
| Tamil | 4168 | 63 | tamil_base_int8 | 86.1 | 0.922 | 85.9 | 74.7 | 92.8 |

## By dataset

| dataset | n | pos% | model | acc | AUC | prec(inc) | rec(inc) | rec(comp) |
|---|---|---|---|---|---|---|---|---|
| tamil_eot_spring_inx_r1 | 4168 | 63 | v32cpu | 70.2 | 0.749 | 59.0 | 63.5 | 74.1 |
| tamil_eot_spring_inx_r1 | 4168 | 63 | v32gpu | 59.4 | 0.743 | 47.1 | 81.1 | 46.7 |
| tamil_eot_spring_inx_r1 | 4168 | 63 | tamil_base_int8 | 86.1 | 0.922 | 85.9 | 74.7 | 92.8 |

## Overall

| model | acc | AUC |
|---|---|---|
| v32cpu | 70.2 | 0.749 |
| v32gpu | 59.4 | 0.743 |
| tamil_base_int8 | 86.1 | 0.922 |