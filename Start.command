#!/bin/bash
# Finder entry point; Ctrl+C stops the local studio.
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd) || exit 1
echo "M4 Image Studio — Start"
bash "$SCRIPT_DIR/studio.sh" "$@"
status=$?
if [ -t 0 ]; then read -r -p "Press Return to close this window."; fi
exit "$status"
