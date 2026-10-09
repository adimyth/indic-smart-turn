#!/usr/bin/env bash
# On the pod: fine-tune from the Stage 5 base checkpoint on private + capped public data, export, quantise (dynamic int8),
# then evaluate current vs adapted on the public Indic test, TamilEOT, v3.2 test, and the private test.
set -euo pipefail
RUN=${1:-indic-base-ft}
cd /workspace/indic-turn; set -a; . .env; set +a
export HF_HOME=/workspace/hf INDIC_TURN_DATA=/workspace/indic-turn/data PYTHONPATH=/workspace/indic-turn TOKENIZERS_PARALLELISM=false EVAL_THREADS=12
mkdir -p logs reports models/$RUN
step() { echo "=== $(date '+%F %T') $* ==="; }
step train $RUN
(cd train && FINETUNE=1 BASE_MODEL=/workspace/indic-turn/output/indic-base/final_model EPOCHS=${EPOCHS:-1} LR=${LR:-1e-5} BATCH=128 EVAL_STEPS=${EVAL_STEPS:-100} \
  python train_local.py --training-run-name "$RUN" --output-dir /workspace/indic-turn/output 2>&1 | tee ../logs/train_$RUN.log | grep -vE "it/s|s/it" || true)
FP32=/workspace/indic-turn/output/$RUN/final_model/exports/model_fp32.onnx; test -f "$FP32"
step quantise dynamic
python - <<PY
from onnxruntime.quantization import quantize_dynamic, QuantType
quantize_dynamic("$FP32", "models/$RUN/indic-smart-turn-int8.onnx", weight_type=QuantType.QInt8, op_types_to_quantize=["MatMul", "Gemm"])
PY
cp "$FP32" models/$RUN/indic-smart-turn-fp32.onnx
step evaluate public
python -m indic_turn.eval --models base_int8_current=models/indic-base/indic-smart-turn-int8-dynamic.onnx base_fp32_current=models/indic-base/indic-smart-turn-fp32.onnx \
  ft_int8=models/$RUN/indic-smart-turn-int8.onnx ft_fp32=models/$RUN/indic-smart-turn-fp32.onnx \
  --data 'data/built/*.parquet' --split test --hf santhosh-005/tamil-eot:test pipecat-ai/smart-turn-data-v3.2-test:train:eng,hin,mar,ben \
  --out reports/eval_${RUN}_public.md
step evaluate private
python -m indic_turn.eval --models smartturn_v3.2=models/smart-turn-v3.2-cpu.onnx base_int8_current=models/indic-base/indic-smart-turn-int8-dynamic.onnx \
  ft_int8=models/$RUN/indic-smart-turn-int8.onnx ft_fp32=models/$RUN/indic-smart-turn-fp32.onnx \
  --data 'data/private/pod/*.parquet' --split test --out reports/eval_${RUN}_private.md --dump-probs reports/${RUN}_private_probs.csv
step FINETUNE DONE
