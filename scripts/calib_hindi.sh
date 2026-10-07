#!/usr/bin/env bash
# Label-quality calibration: build Hindi locally, score with stock v3.2 (which already knows Hindi).
set -euo pipefail; cd "$(dirname "$0")/.."; set -a; . ./.env; set +a
mkdir -p models reports
uv run python -c "
from huggingface_hub import hf_hub_download; import os
for f in ['smart-turn-v3.2-cpu.onnx','smart-turn-v3.2-gpu.onnx']:
    p=hf_hub_download('pipecat-ai/smart-turn-v3',f,token=os.environ['HF_TOKEN']); os.system(f'cp {p} models/{f}')
p=hf_hub_download('santhosh-005/smart-turn-tamil','smart-turn-tamil-base/smart-turn-tamil-int8-dynamic.onnx',token=os.environ['HF_TOKEN']); os.system(f'cp {p} models/smart-turn-tamil-base-int8.onnx')
"
uv run python -m indic_turn.build --langs hin --pausecut-frac 0.8
uv run python -m indic_turn.eval --models v32cpu=models/smart-turn-v3.2-cpu.onnx v32gpu=models/smart-turn-v3.2-gpu.onnx --data data/built/hin.parquet --split "" --out reports/calib_hindi_stock.md
