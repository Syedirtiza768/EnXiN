#!/usr/bin/env bash
# ==================================================================
# EnXi ERP — Pull Updates & Redeploy
# ==================================================================
# Usage:  ./scripts/update.sh [branch]
#         Default branch: main
# ==================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_DIR}"

BRANCH="${1:-main}"
TAG_BEFORE=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo "============================================"
echo "  EnXi ERP — Update  (${BRANCH})"
echo "  Current commit: ${TAG_BEFORE}"
echo "============================================"

# ---- 1. Backup ---------------------------------------------------
echo ""
echo "[1/5] Creating pre-update backup..."
bash scripts/backup.sh 2>/dev/null || echo "  (skipped — site may not be running yet)"

# ---- 2. Pull code ------------------------------------------------
echo ""
echo "[2/5] Pulling latest code from origin/${BRANCH}..."
git pull origin "${BRANCH}"

TAG_AFTER=$(git rev-parse --short HEAD)
echo "  Updated: ${TAG_BEFORE} → ${TAG_AFTER}"

# ---- 3. Rebuild --------------------------------------------------
echo ""
echo "[3/5] Rebuilding Docker image..."
docker compose build

# ---- 4. Restart --------------------------------------------------
echo ""
echo "[4/5] Restarting services (configurator will run migrations)..."
docker compose down --timeout 30
docker compose up -d

# ---- 5. Verify ---------------------------------------------------
echo ""
echo "[5/5] Waiting for services..."
sleep 10

if docker compose ps --format "table {{.Service}}\t{{.State}}" 2>/dev/null; then
    echo ""
else
    docker compose ps
fi

echo "============================================"
echo "  Update complete."
echo "  Logs : docker compose logs -f"
echo "============================================"
echo ""
echo "ROLLBACK (if needed):"
echo "  git checkout ${TAG_BEFORE}"
echo "  docker compose down && docker compose up -d --build"
