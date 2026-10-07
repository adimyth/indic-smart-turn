#!/usr/bin/env bash
# Build every language (short cap 20%, pause-cut candidates for all eligible segments), then
# label every built clip with Gemini audio. Resumable. Run: nohup bash scripts/audio_label_all.sh > data/audio_all.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."; set -a; . ./.env; set +a
for lang in hin tel kan mar tam mal guj pan; do
  echo "=== $(date '+%T') build $lang ==="
  uv run python -m indic_turn.build --langs $lang --pausecut-frac 1.0 --short-cap 0.2 2>&1 | grep -v Warning
  echo "=== $(date '+%T') gemini $lang ==="
  uv run python -m indic_turn.label_audio --lang $lang --split "" --limit 0 --pausecut -1 --workers 16 2>&1 | grep -v Warning
done
uv run python scripts/audio_agreement.py hin tel kan mar tam mal guj pan > reports/label_agreement_audio.txt 2>&1
echo "ALL AUDIO LABELLING DONE"
