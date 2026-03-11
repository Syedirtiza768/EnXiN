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

if [ -n "$COMPANY_OVERRIDE" ]; then
  KWARGS="{'seed_dir':'$SEED_DIR','company_override':'$COMPANY_OVERRIDE'}"
else
  KWARGS="{'seed_dir':'$SEED_DIR'}"
fi

bench --site "$SITE_NAME" execute erpnext.seed.import_executor.import_seed --kwargs "$KWARGS"

echo "Import execution finished. See ${SEED_DIR}/frappe_import_report.json"
