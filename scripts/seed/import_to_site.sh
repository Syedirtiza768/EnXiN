#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <site-name> [seed-dir] [company-override]"
  echo "Example: $0 enxi.localhost seed_output 'EnXi Biomedical & Waste Management (Pvt) Ltd'"
  exit 1
fi

SITE_NAME="$1"
SEED_DIR="${2:-seed_output}"
COMPANY_OVERRIDE="${3:-}"

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
