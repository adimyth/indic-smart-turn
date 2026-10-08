#!/usr/bin/env bash
# On the pod: re-export tiny (if needed), then evaluate all 7 models once with the shared-feature evaluator.
set -euo pipefail
cd /workspace/indic-turn; set -a; . .env; set +a
export HF_HOME=/workspace/hf INDIC_TURN_DATA=/workspace/indic-turn/data PYTHONPATH=/workspace/indic-turn EVAL_THREADS=12
if [ "$(stat -c %s models/indic-tiny/indic-smart-turn-int8.onnx)" -gt 20000000 ]; then
  echo "=== $(date '+%T') re-export tiny ==="; (cd train && python ../scripts/reexport.py indic-tiny)
fi
echo "=== $(date '+%T') evaluate all ==="
python -m indic_turn.eval \
  --models smartturn_v3.2_cpu=models/smart-turn-v3.2-cpu.onnx smartturn_v3.2_gpu=models/smart-turn-v3.2-gpu.onnx \
           tamil_base_int8=models/smart-turn-tamil-base-int8.onnx \
           base_fp32=models/indic-base/indic-smart-turn-fp32.onnx base_int8=models/indic-base/indic-smart-turn-int8.onnx \
           tiny_fp32=models/indic-tiny/indic-smart-turn-fp32.onnx tiny_int8=models/indic-tiny/indic-smart-turn-int8.onnx \
  --data 'data/built/*.parquet' --split test \
  --hf santhosh-005/tamil-eot:test pipecat-ai/smart-turn-data-v3.2-test:train:eng,hin,mar,ben \
  --out reports/eval_all_test.md
echo "=== $(date '+%T') evaluate ambiguous ==="
python -m indic_turn.eval --models base_fp32=models/indic-base/indic-smart-turn-fp32.onnx tiny_fp32=models/indic-tiny/indic-smart-turn-fp32.onnx smartturn_v3.2_cpu=models/smart-turn-v3.2-cpu.onnx \
  --data 'data/built/*.parquet' --split test_ambiguous --out reports/eval_all_test_ambiguous.md
echo "=== $(date '+%T') EVAL ALL DONE ==="
