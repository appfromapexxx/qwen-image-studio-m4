#!/bin/bash
# Shared environment checks are also used by download.sh and studio.sh.

select_python() {
  local candidate resolved
  PYTHON_BIN=""
  if [ -n "${PYTHON:-}" ]; then
    resolved=$(command -v "$PYTHON" 2>/dev/null) || resolved=""
    if [ -n "$resolved" ] && "$resolved" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      PYTHON_BIN="$resolved"
      return 0
    fi
    echo "PYTHON must name an available Python 3.9+ executable: $PYTHON" >&2
    return 1
  fi
  for candidate in python3 python3.13 python3.12 python3.11 python3.10 python3.9 /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
    resolved=$(command -v "$candidate" 2>/dev/null) || continue
    if "$resolved" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      PYTHON_BIN="$resolved"
      return 0
    fi
  done
  echo "Python 3.9+ is required. Install Python, or set PYTHON to its executable path." >&2
  return 1
}

check_environment() {
  local version major tool
  if [ "$(uname -s)" != "Darwin" ]; then
    echo "M4 Image Studio requires macOS 26 or newer." >&2
    return 1
  fi
  if [ "$(uname -m)" != "arm64" ]; then
    echo "M4 Image Studio requires Apple Silicon. Run Terminal natively, without Rosetta." >&2
    return 1
  fi
  version=$(sw_vers -productVersion) || return 1
  major=${version%%.*}
  if ! [[ "$major" =~ ^[0-9]+$ ]] || [ "$major" -lt 26 ]; then
    echo "macOS 26 or newer is required by the bundled engines; detected $version." >&2
    return 1
  fi
  for tool in curl unzip tar shasum sips open; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      echo "Required macOS tool is missing: $tool" >&2
      return 1
    fi
  done
  select_python || return 1
  echo "Environment OK: Apple Silicon, macOS $version, Python: $PYTHON_BIN"
}

install_main() {
  local script_dir
  case "${1:-}" in
    --help|-h)
      cat <<'HELP'
M4 Image Studio installer
Usage: bash install.sh [--check | --help]
  No option: install the original 4-step setup, then add Turbo 8-step.
  --check:   check Apple Silicon, macOS 26+, tools and Python 3.9+; no downloads.
  --help:    show this help.
PYTHON may name one Python executable, including a full path with spaces.
This installer does not install Python, Homebrew or pip packages.
Downloads can be resumed by running this installer again.
HELP
      return 0 ;;
    ""|--check) ;;
    *) echo "Unknown option: $1. Use bash install.sh --help." >&2; return 2 ;;
  esac
  [ "$#" -le 1 ] || { echo "Use bash install.sh --help for supported options." >&2; return 2; }
  check_environment || return 1
  [ "${1:-}" != "--check" ] || return 0
  script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || return 1
  cd "$script_dir" || return 1
  echo "Installing M4 Image Studio: original setup, then Turbo 8-step."
  bash "$script_dir/download.sh" || return $?
  bash "$script_dir/download.sh" --turbo8 || return $?
  echo "Installation complete. Double-click Start.command to open M4 Image Studio."
}

# Sourcing this file only defines helpers; it never installs or downloads anything.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  set -euo pipefail
  install_main "$@"
fi
