#!/usr/bin/env bash
# Runs ON the pod after pod_setup.sh: build samples -> train -> quantize -> evaluate.
# usage: pod_pipeline.sh [run_name]   (env: BASE_MODEL, EPOCHS, BATCH, LR, INDIC_REPEAT, V32_ENG_CAP)
set -euo pipefail
RUN=${1:-indic-base}
cd /workspace/indic-turn
set -a; . /workspace/indic-turn/.env; set +a
export HF_HOME=/workspace/hf INDIC_TURN_DATA=/workspace/indic-turn/data PYTHONPATH=/workspace/indic-turn
export TOKENIZERS_PARALLELISM=false
mkdir -p logs reports output
step() { echo "=== $(date '+%F %T') $* ==="; }

step build
for l in hin mar tam kan mal guj pan tel; do
  if [ -f data/labels/$l.jsonl ] && [ ! -f data/built/$l.parquet ]; then
    python -m indic_turn.build --langs $l --pausecut-frac 0.8 2>&1 | grep -v Warning
  fi
done
ls -la data/built

step train $RUN
(cd train && python train_local.py --training-run-name "$RUN" --output-dir /workspace/indic-turn/output 2>&1 | tee ../logs/train_$RUN.log | grep -vE "it/s|s/it" || true)
FP32=/workspace/indic-turn/output/$RUN/final_model/exports/model_fp32.onnx
test -f "$FP32"

step quantize
(cd train && python train_local.py --quantize "$FP32" 2>&1 | tee ../logs/quant_$RUN.log | tail -3)
INT8=$(ls /workspace/indic-turn/output/$RUN/final_model/exports/model_int8_static_calib*.onnx | head -1)
mkdir -p models/$RUN && cp "$FP32" models/$RUN/indic-smart-turn-fp32.onnx && cp "$INT8" models/$RUN/indic-smart-turn-int8.onnx

step evaluate
python -m indic_turn.eval \
  --models smartturn_v3.2_cpu=models/smart-turn-v3.2-cpu.onnx smartturn_v3.2_gpu=models/smart-turn-v3.2-gpu.onnx \
           tamil_base_int8=models/smart-turn-tamil-base-int8.onnx \
           ours_fp32=models/$RUN/indic-smart-turn-fp32.onnx ours_int8=models/$RUN/indic-smart-turn-int8.onnx \
  --data 'data/built/*.parquet' --split test \
  --hf santhosh-005/tamil-eot:test pipecat-ai/smart-turn-data-v3.2-test:train:eng,hin,mar,ben \
  --out reports/eval_$RUN.md 2>&1 | tee logs/eval_$RUN.log | tail -80
step done
