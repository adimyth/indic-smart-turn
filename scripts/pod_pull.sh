#!/usr/bin/env bash
# Copy a completed pod run home, including the PyTorch checkpoint required for optional local adaptation.
set -euo pipefail

run=${1:?usage: scripts/pod_pull.sh <run_name>}
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
read host port < .pod_ssh
remote="root@$host:/workspace/indic-turn"
transport="ssh -o StrictHostKeyChecking=no -p $port"

mkdir -p "models/$run" "output/$run" reports logs
rsync -rlptz -e "$transport" "$remote/models/$run/" "models/$run/"
rsync -rlptz -e "$transport" "$remote/output/$run/final_model/" "output/$run/final_model/"
rsync -rlptz -e "$transport" "$remote/reports/" reports/
rsync -rlptz -e "$transport" "$remote/logs/" logs/
echo "pulled $run, including output/$run/final_model"
