#!/bin/bash
# Start M4 Image Studio: bash studio.sh [port]   (Ctrl+C to stop)
set -euo pipefail
cd "$(dirname "$0")"
source ./install.sh
check_environment
PORT="${1:-7860}"
export PYTHONDONTWRITEBYTECODE=1
echo "Opening M4 Image Studio at http://127.0.0.1:$PORT (Ctrl+C to stop)."
(sleep 1.5 && open "http://127.0.0.1:$PORT") &
exec "$PYTHON_BIN" studio/server.py "$PORT"
