#!/usr/bin/env bash
# Build + Gemini-label one language. usage: audio_label_one.sh <lang>
set -uo pipefail; cd "$(dirname "$0")/.."; set -a; . ./.env; set +a
lang=$1
echo "=== $(date '+%T') build $lang ==="
uv run python -m indic_turn.build --langs $lang --pausecut-frac 1.0 --short-cap 0.2 2>&1 | grep -v Warning
echo "=== $(date '+%T') gemini $lang ==="
uv run python -m indic_turn.label_audio --lang $lang --split "" --limit 0 --pausecut -1 --workers 12 2>&1 | grep -v Warning
echo "=== $(date '+%T') $lang DONE ==="
