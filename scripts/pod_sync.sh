#!/usr/bin/env bash
# rsync code + labels to the pod (reads .pod_ssh written by pod_create.py). usage: pod_sync.sh [extra rsync paths]
set -euo pipefail; cd "$(dirname "$0")/.."
read HOST PORT < .pod_ssh
SSH="ssh -o StrictHostKeyChecking=no -p $PORT"
rsync -rlptz -e "$SSH" --exclude '.venv' --exclude 'references' --exclude '/data' --exclude '__pycache__' --exclude 'models' \
  ./ root@$HOST:/workspace/indic-turn/
# only the index and labels go up; the pod builds its own clips into data/built
rsync -rlptz -e "$SSH" data/index data/labels root@$HOST:/workspace/indic-turn/data/
echo synced
