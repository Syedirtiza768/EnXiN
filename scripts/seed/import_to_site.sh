#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <site-name> [seed-dir] [company-override]"
  echo "Example: $0 enxi.localhost seed_output 'EnXi Biomedical & Waste Management (Pvt) Ltd'"
  echo "Also supports unquoted names with spaces if seed-dir token is present:"
  echo "  $0 Global Business Concern seed_output Global Business Concern"
  exit 1
fi

# Parse arguments robustly:
# 1) If an explicit seed dir token (existing path or 'seed_output') is present,
#    tokens before it are site name and tokens after it are company override.
# 2) Otherwise fallback to classic positional parsing.
ARGS=("$@")
SEED_DIR_INDEX=-1
for i in "${!ARGS[@]}"; do
  token="${ARGS[$i]}"
  if [ "$token" = "seed_output" ] || [ -d "$token" ] || [ -f "$token" ]; then
    SEED_DIR_INDEX=$i
    break
  fi
done

if [ "$SEED_DIR_INDEX" -ge 0 ]; then
  SITE_NAME="${ARGS[0]}"
  if [ "$SEED_DIR_INDEX" -gt 1 ]; then
    for ((j=1; j<SEED_DIR_INDEX; j++)); do
      SITE_NAME+=" ${ARGS[$j]}"
    done
  fi

  SEED_DIR="${ARGS[$SEED_DIR_INDEX]}"

  COMPANY_OVERRIDE=""
  if [ "$SEED_DIR_INDEX" -lt $((${#ARGS[@]} - 1)) ]; then
    COMPANY_OVERRIDE="${ARGS[$((SEED_DIR_INDEX + 1))]}"
    if [ "$((SEED_DIR_INDEX + 2))" -le $((${#ARGS[@]} - 1)) ]; then
      for ((j=SEED_DIR_INDEX+2; j<${#ARGS[@]}; j++)); do
        COMPANY_OVERRIDE+=" ${ARGS[$j]}"
      done
    fi
  fi
else
  SITE_NAME="$1"
  SEED_DIR="${2:-seed_output}"
  COMPANY_OVERRIDE="${3:-}"
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# In Docker deployment, seed files are committed under apps/erpnext/seed_output.
if [[ "$SEED_DIR" = /* ]]; then
  CONTAINER_SEED_DIR="$SEED_DIR"
else
  CONTAINER_SEED_DIR="/home/frappe/frappe-bench/apps/erpnext/${SEED_DIR}"
fi

if [ -n "$COMPANY_OVERRIDE" ]; then
  KWARGS="{'seed_dir':'$CONTAINER_SEED_DIR','company_override':'$COMPANY_OVERRIDE'}"
else
  KWARGS="{'seed_dir':'$CONTAINER_SEED_DIR'}"
fi

if docker compose ps backend >/dev/null 2>&1; then
  docker compose exec -T backend \
    bench --site "$SITE_NAME" execute erpnext.seed.import_executor.import_seed --kwargs "$KWARGS"
else
  bench --site "$SITE_NAME" execute erpnext.seed.import_executor.import_seed --kwargs "$KWARGS"
fi

echo "Import execution finished. Report path inside container: ${CONTAINER_SEED_DIR}/frappe_import_report.json"
