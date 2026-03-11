#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <site-name> <company-name> [company-abbr] [country] [currency]"
  echo "Example: $0 biomeds ""Global Business Concern"" GBC Pakistan PKR"
  exit 1
fi

SITE_NAME="$1"
COMPANY_NAME="$2"
COMPANY_ABBR="${3:-GBC}"
COUNTRY="${4:-Pakistan}"
CURRENCY="${5:-PKR}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "ERROR: .env not found in project root. Run ./scripts/deploy.sh first."
  exit 1
fi

# shellcheck disable=SC1091
source .env

if ! docker compose ps backend >/dev/null 2>&1; then
  echo "ERROR: backend service not available. Start stack with docker compose up -d"
  exit 1
fi

site_exists() {
  docker compose exec -T backend bash -lc "test -f /home/frappe/frappe-bench/sites/$1/site_config.json"
}

app_installed() {
  docker compose exec -T backend bash -lc "bench --site '$1' list-apps | grep -qx 'erpnext'"
}

echo "Ensuring site: $SITE_NAME"
if site_exists "$SITE_NAME"; then
  echo "Site already exists: $SITE_NAME"
else
  docker compose exec -T backend \
    bench new-site "$SITE_NAME" \
      --db-root-password "${DB_ROOT_PASSWORD}" \
      --admin-password "${ADMIN_PASSWORD:-admin}" \
      --no-mariadb-socket
fi

echo "Ensuring ERPNext app is installed on site: $SITE_NAME"
if app_installed "$SITE_NAME"; then
  echo "ERPNext already installed on $SITE_NAME"
else
  docker compose exec -T backend bench --site "$SITE_NAME" install-app erpnext
fi

echo "Setting default site"
docker compose exec -T backend bench use "$SITE_NAME"

echo "Ensuring company: $COMPANY_NAME"
KWARGS="{'company_name':'$COMPANY_NAME','abbr':'$COMPANY_ABBR','country':'$COUNTRY','currency':'$CURRENCY','set_global_defaults':1}"
docker compose exec -T backend \
  bench --site "$SITE_NAME" execute erpnext.seed.demo_setup.ensure_company --kwargs "$KWARGS"

echo "Done. Site '$SITE_NAME' and company '$COMPANY_NAME' are ready for demo seed import."
