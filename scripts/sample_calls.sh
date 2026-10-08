#!/usr/bin/env bash
# Download + analyze the first N sessions of a language from the private CSV. usage: sample_calls.sh <Language> <N>
set -uo pipefail; cd "$(dirname "$0")/.."
lang=$1; n=$2; csv=data/private/additional-data.csv; tag=$(echo "$lang" | tr 'A-Z' 'a-z')
mkdir -p data/private/raw data/private/preview
uv run python -c "
import csv,sys
rows=[r['audio_file'] for r in csv.DictReader(open('$csv')) if r['language']=='$lang'][:$n]
print('\n'.join(rows))" | nl -w1 | while read k url; do
  base="data/private/raw/${tag}_$k"; t0=$(date +%s)
  curl -sL -o "$base.mp4" "$url"; t1=$(date +%s)
  ffmpeg -v error -y -i "$base.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$base.wav"; t2=$(date +%s)
  echo "===== $lang #$k  (download $((t1-t0))s, decode $((t2-t1))s, $(du -h "$base.mp4" | cut -f1)) ====="
  uv run python scripts/analyze_call.py "$base.wav" --preview-dir "data/private/preview/${tag}_$k" --n-preview 8 2>&1 | grep -vE "Warning|warn|pkg_resources|timeline|^  +[0-9.]+- +[0-9.]+ +[0-9.]+s (agent|user)$"
  echo "analysis $(( $(date +%s) - t2 ))s"
done
