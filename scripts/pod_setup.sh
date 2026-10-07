#!/usr/bin/env bash
# Runs ON the pod. Installs deps and pre-downloads the upstream datasets. Idempotent.
set -euo pipefail
cd /workspace/indic-turn
set -a; . /workspace/indic-turn/.env; set +a
export HF_HOME=/workspace/hf INDIC_TURN_DATA=/workspace/indic-turn/data
mkdir -p logs data/built
if [ ! -f .deps_done ]; then
  apt-get update -qq && apt-get install -y -qq ffmpeg rsync > /dev/null
  pip install -q --break-system-packages "torchcodec==0.7.0" "transformers[torch]==4.48.2" "datasets==4.4.1" scikit-learn librosa soundfile \
      onnx onnxruntime-gpu onnxscript wandb huggingface_hub pyarrow python-dotenv openai tqdm
  python -c "import torch, torchcodec, datasets, transformers; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())"
  touch .deps_done
fi
# upstream data: v3.2 (filtered to eng/hin/mar at train time) + TamilEOT clips
python - <<'PY'
import os
from huggingface_hub import snapshot_download
for r in ["pipecat-ai/smart-turn-data-v3.2-train", "pipecat-ai/smart-turn-data-v3.2-test", "santhosh-005/tamil-eot"]:
    snapshot_download(r, repo_type="dataset", token=os.environ["HF_TOKEN"]); print("ok", r)
from huggingface_hub import hf_hub_download
os.makedirs("models", exist_ok=True)
for repo, f, out in [("pipecat-ai/smart-turn-v3","smart-turn-v3.2-cpu.onnx","models/smart-turn-v3.2-cpu.onnx"),
                     ("pipecat-ai/smart-turn-v3","smart-turn-v3.2-gpu.onnx","models/smart-turn-v3.2-gpu.onnx"),
                     ("santhosh-005/smart-turn-tamil","smart-turn-tamil-base/smart-turn-tamil-int8-dynamic.onnx","models/smart-turn-tamil-base-int8.onnx")]:
    p = hf_hub_download(repo, f, token=os.environ["HF_TOKEN"]); os.system(f"cp {p} {out}")
PY
echo "SETUP DONE"
