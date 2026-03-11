#!/usr/bin/env bash
# ==================================================================
# EnXi ERP — Backup Database & Files
# ==================================================================
# Usage:  ./scripts/backup.sh
#
# Backups are saved to ./backups/<timestamp>/
# The 10 most recent backups are kept; older ones are pruned.
# ==================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_DIR}"

# Read site name from .env or default
SITE_NAME="${SITE_NAME:-$(grep -E '^SITE_NAME=' .env 2>/dev/null | cut -d= -f2 | tr -d ' ' || true)}"
SITE_NAME="${SITE_NAME:-enxi.localhost}"

BACKUP_DIR="${PROJECT_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEST="${BACKUP_DIR}/${TIMESTAMP}"

mkdir -p "${DEST}"

echo "Backing up site: ${SITE_NAME}..."

# Run bench backup inside the backend container
docker compose exec -T backend \
    bench --site "${SITE_NAME}" backup --with-files

# Copy backup files from the container volume to the host
docker compose cp \
    "backend:/home/frappe/frappe-bench/sites/${SITE_NAME}/private/backups/." \
    "${DEST}/"

# Prune old backups — keep the 10 most recent
cd "${BACKUP_DIR}"
# shellcheck disable=SC2012
ls -dt */ 2>/dev/null | tail -n +11 | xargs -r rm -rf

echo ""
echo "Backup saved to: ${DEST}"
ls -lh "${DEST}/" 2>/dev/null || true
