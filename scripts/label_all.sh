#!/usr/bin/env bash
# Labels primary text labels. Run with `nohup bash scripts/label_all.sh > data/label.log 2>&1 &`.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
set -a
. "$root/.env"
set +a
cd "$root"

# Stage 1 needs metadata for the three languages not previously scanned to the 10k-row target.
uv run python -m indic_turn.scan --langs malayalam gujarati punjabi --target-rows 10000 --max-shards 12

declare -A limit=( [mar]=5000 [kan]=5000 [mal]=5000 [guj]=5000 [pan]=5000 [tam]=3000 )
for lang in mar kan mal guj pan tam; do
  if [[ ! -f "data/index/$lang.parquet" ]]; then
    echo "[$lang] missing metadata index; scan did not produce data/index/$lang.parquet" >&2
    exit 1
  fi
  uv run python -m indic_turn.label --langs "$lang" --limit-rows "${limit[$lang]}" --concurrency 6
done

uv run python -m indic_turn.label_report --strict
echo "ALL PRIMARY LABELLING DONE"
