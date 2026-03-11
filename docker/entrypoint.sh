#!/bin/bash
# ==================================================================
# EnXi ERP — Container Entrypoint
# ==================================================================
set -e

BENCH_DIR="/home/frappe/frappe-bench"
cd "${BENCH_DIR}"

# ============================  Helpers  ===========================

wait_for_tcp () {
    local host="$1" port="$2" timeout="${3:-60}"
    python3 -c "
import socket, sys, time
host, port, timeout = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
deadline = time.time() + timeout
while time.time() < deadline:
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        sys.exit(0)
    except (ConnectionRefusedError, OSError):
        time.sleep(1)
print(f'Timeout waiting for {host}:{port}', file=sys.stderr)
sys.exit(1)
" "$host" "$port" "$timeout"
}

log () { echo ">>> [entrypoint] $*"; }

# ============================  Commands  ==========================

do_configure () {
    log "Waiting for database and Redis..."
    wait_for_tcp "${DB_HOST:-db}" "${DB_PORT:-3306}" 120
    wait_for_tcp redis-cache 6379 30
    wait_for_tcp redis-queue 6379 30
    wait_for_tcp redis-socketio 6379 30

    # -- Restore build artefacts into the mounted volume ----------
    log "Restoring apps.txt and built assets into volume..."
    cp -f /home/frappe/apps.txt sites/apps.txt
    mkdir -p sites/assets
    cp -af /home/frappe/assets/. sites/assets/

    # -- Generate common_site_config.json -------------------------
    log "Writing common_site_config.json..."
    cat > sites/common_site_config.json <<CFG
{
  "db_host": "${DB_HOST:-db}",
  "db_port": ${DB_PORT:-3306},
  "redis_cache": "${REDIS_CACHE:-redis://redis-cache:6379/0}",
  "redis_queue": "${REDIS_QUEUE:-redis://redis-queue:6379/0}",
  "redis_socketio": "${REDIS_SOCKETIO:-redis://redis-socketio:6379/0}",
  "socketio_port": 9000,
  "webserver_port": 8000,
  "serve_default_site": true
}
CFG

    # -- Create or migrate site -----------------------------------
    local site="${SITE_NAME:-enxi.localhost}"

    if [ ! -f "sites/${site}/site_config.json" ]; then
        log "Creating new site: ${site}"
        bench new-site "${site}" \
            --db-root-password "${DB_ROOT_PASSWORD}" \
            --admin-password "${ADMIN_PASSWORD:-admin}" \
            --install-app erpnext \
            --set-default \
            --no-mariadb-socket
    else
        log "Site ${site} exists — running migrations..."
        bench --site "${site}" migrate --skip-failing
    fi

    echo "${site}" > sites/currentsite.txt
    log "Configuration complete."
}

do_backend () {
    log "Starting Gunicorn (workers=${GUNICORN_WORKERS:-4})..."
    exec /home/frappe/frappe-bench/env/bin/gunicorn \
        --chdir "${BENCH_DIR}/sites" \
        --bind 0.0.0.0:8000 \
        --threads 4 \
        --workers "${GUNICORN_WORKERS:-4}" \
        --worker-class gthread \
        --worker-tmp-dir /dev/shm \
        --timeout 120 \
        --graceful-timeout 30 \
        --preload \
        frappe.app:application
}

do_worker () {
    local queue="$1"
    log "Starting worker (queue=${queue})..."
    exec bench worker --queue "${queue}"
}

do_scheduler () {
    log "Starting scheduler..."
    exec bench schedule
}

do_websocket () {
    log "Starting WebSocket server..."
    exec node apps/frappe/socketio.js
}

# ============================  Dispatch  ==========================

case "${1}" in
    configure)      do_configure ;;
    backend)        do_backend ;;
    worker-default) do_worker default ;;
    worker-short)   do_worker short ;;
    worker-long)    do_worker long ;;
    scheduler)      do_scheduler ;;
    websocket)      do_websocket ;;
    *)              exec "$@" ;;
esac
