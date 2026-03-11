#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <site-name> <company-name> [company-abbr] [country] [currency]"
  echo "Example: $0 biomeds ""Global Business Concern"" GBC Pakistan PKR"
  exit 1
fi

SITE_NAME_INPUT="$1"
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

# Preserve CLI-provided site name; .env may also define SITE_NAME.
SITE_NAME="$SITE_NAME_INPUT"

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
docker compose exec -T \
  -e DEMO_SITE_NAME="$SITE_NAME" \
  -e DEMO_COMPANY_NAME="$COMPANY_NAME" \
  -e DEMO_COMPANY_ABBR="$COMPANY_ABBR" \
  -e DEMO_COUNTRY="$COUNTRY" \
  -e DEMO_CURRENCY="$CURRENCY" \
  backend \
  python - <<'PY'
import os
import frappe

site = os.environ["DEMO_SITE_NAME"]
company_name = os.environ["DEMO_COMPANY_NAME"]
abbr = os.environ["DEMO_COMPANY_ABBR"]
country = os.environ["DEMO_COUNTRY"]
currency = os.environ["DEMO_CURRENCY"]

# Ensure frappe resolves site from bench runtime paths inside container.
bench_dir = "/home/frappe/frappe-bench"
sites_dir = f"{bench_dir}/sites"
os.chdir(bench_dir)

# Ensure expected log paths exist for frappe logger initialization.
os.makedirs("/home/frappe/logs", exist_ok=True)
os.makedirs(f"{sites_dir}/{site}/logs", exist_ok=True)

frappe.init(site=site, sites_path=sites_dir)
frappe.connect()

from erpnext.seed.demo_setup import ensure_company

result = ensure_company(
    company_name=company_name,
    abbr=abbr,
    country=country,
    currency=currency,
    set_global_defaults=True,
)
print(result)

frappe.destroy()
PY

echo "Done. Site '$SITE_NAME' and company '$COMPANY_NAME' are ready for demo seed import."
