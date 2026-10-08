#!/usr/bin/env bash
# On the pod: build alternative int8 variants of the base model (dynamic, and static percentile with 256 samples) and score them.
set -euo pipefail; cd /workspace/indic-turn; set -a; . .env; set +a
export HF_HOME=/workspace/hf INDIC_TURN_DATA=/workspace/indic-turn/data PYTHONPATH=/workspace/indic-turn EVAL_THREADS=12
FP32=models/indic-base/indic-smart-turn-fp32.onnx
python - <<'PY'
import os, sys
sys.path.insert(0, "train")
from onnxruntime.quantization import quantize_dynamic, quantize_static, QuantType, QuantFormat, CalibrationMethod, quant_pre_process
import train
fp32 = "models/indic-base/indic-smart-turn-fp32.onnx"
quantize_dynamic(fp32, "models/indic-base/indic-smart-turn-int8-dynamic.onnx", weight_type=QuantType.QInt8, op_types_to_quantize=["MatMul", "Gemm"])
print("dynamic done", os.path.getsize("models/indic-base/indic-smart-turn-int8-dynamic.onnx") / 1e6, "MB")
from transformers import WhisperFeatureExtractor
fe = WhisperFeatureExtractor(chunk_length=8)
ds = train.prepare_datasets_ondemand(fe, train.CONFIG)["training"]
quant_pre_process(fp32, "models/indic-base/_pre.onnx", skip_optimization=False, skip_symbolic_shape=True)
calib = train.CalibrationDataset(ds, fe, max_samples=256)
quantize_static(model_input="models/indic-base/_pre.onnx", model_output="models/indic-base/indic-smart-turn-int8-percentile.onnx",
                calibration_data_reader=train.ONNXCalibrationDataReader(calib), quant_format=QuantFormat.QDQ,
                activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8, per_channel=True,
                calibrate_method=CalibrationMethod.Percentile, op_types_to_quantize=["Conv", "MatMul", "Gemm"],
                extra_options={"CalibPercentile": 99.99})
print("percentile done", os.path.getsize("models/indic-base/indic-smart-turn-int8-percentile.onnx") / 1e6, "MB")
PY
echo "=== $(date '+%T') evaluate int8 variants ==="
python -m indic_turn.eval --models base_fp32=$FP32 base_int8_minmax=models/indic-base/indic-smart-turn-int8.onnx \
  base_int8_dynamic=models/indic-base/indic-smart-turn-int8-dynamic.onnx base_int8_percentile=models/indic-base/indic-smart-turn-int8-percentile.onnx \
  --data 'data/built/*.parquet' --split test --hf santhosh-005/tamil-eot:test --out reports/eval_base_int8_variants.md
echo "=== $(date '+%T') QUANT ALT DONE ==="
