#!/usr/bin/env bash
# Scan + text-label one IndicVoices config, then (optionally) build + Gemini audio label.
# usage: add_language.sh <config e.g. assamese> <iso e.g. asm> [--audio]
set -uo pipefail; cd "$(dirname "$0")/.."; set -a; . ./.env; set +a
cfg=$1; iso=$2; audio=${3:-}
echo "=== $(date '+%T') scan $cfg ==="
uv run python -m indic_turn.scan --langs $cfg --target-rows 10000 --max-shards 12 2>&1 | grep -v Warning | tail -2
echo "=== $(date '+%T') text labels $iso ==="
uv run python -m indic_turn.label --langs $iso --limit-rows 5000 --concurrency 6 2>&1 | grep -v Warning | tail -2
if [ "$audio" = "--audio" ]; then bash scripts/audio_label_one.sh $iso; fi
echo "=== $(date '+%T') $iso TEXT DONE ==="
