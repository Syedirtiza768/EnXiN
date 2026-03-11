#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 scripts/seed/generate_demo_seed.py "$@"
python3 scripts/seed/validate_demo_seed.py --input seed_output

echo "Seed pipeline completed successfully."
