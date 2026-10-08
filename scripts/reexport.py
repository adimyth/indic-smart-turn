#!/usr/bin/env python3
"""Re-export fp32 ONNX from a saved checkpoint (with constant folding) and re-quantize it.
usage (on the pod, from train/): python ../scripts/reexport.py <run_name>"""
import os, sys, glob, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../train")
import train
run = sys.argv[1]
final = f"/workspace/indic-turn/output/{run}/final_model"
model = train.SmartTurnV3Model.from_pretrained(final).eval().cpu()
exports = os.path.join(final, "exports"); os.makedirs(exports, exist_ok=True)
for f in glob.glob(os.path.join(exports, "*.onnx")): os.rename(f, f + ".bak")
fp32 = train.export_to_onnx_fp32(model, os.path.join(exports, "model_fp32.onnx"), train.CONFIG)
assert fp32, "export failed"
import onnx, collections
m = onnx.load(fp32); print("fp32 nodes", len(m.graph.node), "initializers", len(m.graph.initializer), dict(collections.Counter(n.op_type for n in m.graph.node).most_common(5)))
int8 = train.do_quantization_run(fp32)
m = onnx.load(int8); dt = collections.Counter(t.data_type for t in m.graph.initializer)
print("int8 initializer dtypes", dict(dt), "size MB", round(os.path.getsize(int8) / 1e6, 1))
dst = f"/workspace/indic-turn/models/{run}"; os.makedirs(dst, exist_ok=True)
shutil.copy(fp32, f"{dst}/indic-smart-turn-fp32.onnx"); shutil.copy(int8, f"{dst}/indic-smart-turn-int8.onnx")
print("copied to", dst)
