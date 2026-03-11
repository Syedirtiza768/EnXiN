#!/usr/bin/env bash
# ==================================================================
# EnXi ERP — First-time Deployment
# ==================================================================
# Usage:  ./scripts/deploy.sh
# ==================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_DIR}"

echo "============================================"
echo "  EnXi ERP — Deployment"
echo "============================================"

# ---- Generate .env on first run ----------------------------------
if [ ! -f .env ]; then
    echo "No .env found. Generating from template with secure passwords..."
    cp env/.env.example .env

    python3 << 'PYEOF'
import secrets, pathlib
env = pathlib.Path(".env").read_text()
db_pw   = secrets.token_urlsafe(20)
admin_pw = secrets.token_urlsafe(20)
env = env.replace("changeme_db_root", db_pw)
env = env.replace("changeme_admin",   admin_pw)
pathlib.Path(".env").write_text(env)
print(f"\n  DB Root Password : {db_pw}")
print(f"  Admin Password   : {admin_pw}\n")
PYEOF

    echo "Passwords saved to .env — store them securely."
    echo "Review .env, then re-run:  ./scripts/deploy.sh"
    exit 0
fi

# ---- Build -------------------------------------------------------
echo ""
echo "[1/2] Building containers (this takes several minutes on first run)..."
docker compose build

# ---- Start -------------------------------------------------------
echo "[2/2] Starting services..."
docker compose up -d

HTTP_PORT=$(grep -E '^HTTP_PORT=' .env | cut -d= -f2 | tr -d ' ' || echo 8090)

echo ""
echo "============================================"
echo "  EnXi is starting up."
echo "  First-time initialisation takes 2-5 min."
echo ""
echo "  Monitor : docker compose logs -f"
echo "  Access  : http://localhost:${HTTP_PORT}"
echo "============================================"
