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

detect_default_site() {
  docker compose exec -T backend bash -lc 'cat /home/frappe/frappe-bench/sites/currentsite.txt 2>/dev/null || true' | tr -d '\r' | xargs
}

site_exists_in_container() {
  local site="$1"
  docker compose exec -T backend bash -lc "test -f /home/frappe/frappe-bench/sites/${site}/site_config.json"
}

# In Docker deployment, seed files are committed under apps/erpnext/seed_output.
if [[ "$SEED_DIR" = /* ]]; then
  CONTAINER_SEED_DIR="$SEED_DIR"
else
  CONTAINER_SEED_DIR="/home/frappe/frappe-bench/apps/erpnext/${SEED_DIR}"
fi

BENCH_ARGS="import-demo-seed --seed-dir $CONTAINER_SEED_DIR"
if [ -n "$COMPANY_OVERRIDE" ]; then
  BENCH_ARGS="$BENCH_ARGS --company \"$COMPANY_OVERRIDE\""
fi

# If provided site name is not a real Frappe site directory, auto-resolve to
# current default site and treat original input as company override.
if docker compose ps backend >/dev/null 2>&1; then
  if ! site_exists_in_container "$SITE_NAME"; then
    DETECTED_SITE="$(detect_default_site)"
    if [ -n "$DETECTED_SITE" ] && site_exists_in_container "$DETECTED_SITE"; then
      if [ -z "$COMPANY_OVERRIDE" ]; then
        COMPANY_OVERRIDE="$SITE_NAME"
      fi
      SITE_NAME="$DETECTED_SITE"

      BENCH_ARGS="import-demo-seed --seed-dir $CONTAINER_SEED_DIR"
      if [ -n "$COMPANY_OVERRIDE" ]; then
        BENCH_ARGS="$BENCH_ARGS --company \"$COMPANY_OVERRIDE\""
      fi
    fi
  fi
fi

if docker compose ps backend >/dev/null 2>&1; then
  # Sync latest seed module code and data into running container so that
  # a git pull on the host is enough — no full image rebuild needed.
  echo "Syncing seed code and data into container …"
  docker compose cp erpnext/seed/. backend:/home/frappe/frappe-bench/apps/erpnext/erpnext/seed/
  docker compose cp erpnext/commands/. backend:/home/frappe/frappe-bench/apps/erpnext/erpnext/commands/
  if [ -d "$SEED_DIR" ]; then
    docker compose cp "${SEED_DIR}/." backend:/home/frappe/frappe-bench/apps/erpnext/${SEED_DIR}/
  fi

  # Purge Python bytecache so the container uses the freshly-copied .py files
  # instead of stale .pyc compiled from the original Docker image build.
  docker compose exec -T backend bash -c \
    "find /home/frappe/frappe-bench/apps/erpnext/erpnext/seed /home/frappe/frappe-bench/apps/erpnext/erpnext/commands -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true"

  docker compose exec -T backend bash -c \
    "cd /home/frappe/frappe-bench && bench --site $SITE_NAME $BENCH_ARGS"
else
  bench --site "$SITE_NAME" $BENCH_ARGS
fi

echo "Import execution finished. Report path inside container: ${CONTAINER_SEED_DIR}/frappe_import_report.json"
