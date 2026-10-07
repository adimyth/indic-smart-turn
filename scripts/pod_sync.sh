#!/usr/bin/env bash
# rsync code + labels to the pod (reads .pod_ssh written by pod_create.py). usage: pod_sync.sh [extra rsync paths]
set -euo pipefail; cd "$(dirname "$0")/.."
read HOST PORT < .pod_ssh
rsync -rlptz -e "ssh -o StrictHostKeyChecking=no -p $PORT" --exclude '.venv' --exclude 'references' --exclude 'data/hf_cache' \
  --exclude 'data/built' --exclude 'data/private' --exclude 'data/preview' --exclude '__pycache__' --exclude 'models' \
  ./ root@$HOST:/workspace/indic-turn/
echo synced
