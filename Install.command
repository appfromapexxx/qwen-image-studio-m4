#!/bin/bash
# Finder entry point; invoke Bash explicitly even if archive extraction lost script permissions.
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd) || exit 1
echo "M4 Image Studio — Install"
bash "$SCRIPT_DIR/install.sh" "$@"
status=$?
if [ -t 0 ]; then read -r -p "Press Return to close this window."; fi
exit "$status"
