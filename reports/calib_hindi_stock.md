# Evaluation report

rows: 6375; models: v32cpu, v32gpu

| model | CPU latency (ms, 1 thread, batch 1) |
|---|---|
| v32cpu | 40.1 |
| v32gpu | 25.9 |

## By language

| language | n | pos% | model | acc | AUC | prec(inc) | rec(inc) | rec(comp) |
|---|---|---|---|---|---|---|---|---|
| Hindi | 6375 | 67 | v32cpu | 60.5 | 0.610 | 41.9 | 52.2 | 64.5 |
| Hindi | 6375 | 67 | v32gpu | 50.9 | 0.616 | 37.5 | 74.1 | 39.6 |

## By dataset

| dataset | n | pos% | model | acc | AUC | prec(inc) | rec(inc) | rec(comp) |
|---|---|---|---|---|---|---|---|---|
| indicvoices_hin | 5009 | 85 | v32cpu | 63.1 | 0.630 | 20.9 | 55.0 | 64.5 |
| indicvoices_hin | 5009 | 85 | v32gpu | 45.3 | 0.638 | 18.1 | 78.5 | 39.6 |
| indicvoices_hin_pausecut | 1366 | 0 | v32cpu | 50.7 | nan | 100.0 | 50.7 | 0.0 |
| indicvoices_hin_pausecut | 1366 | 0 | v32gpu | 71.7 | nan | 100.0 | 71.7 | 0.0 |

## Overall

| model | acc | AUC |
|---|---|---|
| v32cpu | 60.5 | 0.610 |
| v32gpu | 50.9 | 0.616 |