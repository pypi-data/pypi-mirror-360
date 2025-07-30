#!/usr/bin/env bash
# --------------------------------------------
# parallels_dashboard.sh
#   Zero-arg interactive wrapper for
#   run_clipit_window_mgr.sh
# --------------------------------------------
set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LAUNCHER="${SCRIPT_DIR}/clipit/run_clipit_window_mgr.sh"

show_menu() {
  clear
  echo "╔══════════════════════════════════════╗"
  echo "║  Abstract Parallels  ▸  Main Menu    ║"
  echo "╚══════════════════════════════════════╝"
  PS3=$'\nChoose an option › '
  options=(
    "🗒  Clipboard watcher only"
    "🖥  Window-info GUI only"
    "🔗  Both (foreground)"
    "🏃  Both, detached (no terminal)"
    "❌  Quit"
  )
  select opt in "${options[@]}"; do
    case $REPLY in
      1) set -- clipit ;;
      2) set -- gui ;;
      3) set -- both ;;
      4) set -- both --detach ;;
      5) exit 0 ;;
      *) echo "Invalid choice—try again."; continue ;;
    esac
    break
  done
}

# ── If no arguments, drop into menu ────────────────────────────
[[ $# -eq 0 ]] && show_menu

# Everything else is just delegated ↓
exec "$LAUNCHER" "$@"
