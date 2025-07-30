#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  parallels_setup.sh
#
#  One-shot installer + manager for:
#    • Clipboard-Watcher + Window-Info GUI
#    • Services Manager GUI
#    • API GUI
#    • Parallels Dashboard (interactive)
#
#  Usage:
#      ./parallels_setup.sh            # install + start all
#      ./parallels_setup.sh start      # start   all user units
#      ./parallels_setup.sh stop       # stop    all user units
#      ./parallels_setup.sh restart    # restart all user units
#      ./parallels_setup.sh status     # show    status
#      ./parallels_setup.sh logs       # journalctl -fu <each>
# ──────────────────────────────────────────────────────────────

set -euo pipefail

# ─── Variables ────────────────────────────────────────────────
SUFFIX="abstract"
UNITS=(
  "clip_win"       # Clipboard+Window GUI
  "services_mgr"   # Services Manager GUI
  "api_gui"        # API GUI
  "dashboard"      # Dashboard picker
)
SRC_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &>/dev/null && pwd )"
SYSTEMD_DIR="${HOME}/.config/systemd/user"
LOG_DIR="${HOME}/parallels_logs"
mkdir -p "$SYSTEMD_DIR" "$LOG_DIR"

# ─── Helper: write a unit if missing ──────────────────────────
write_unit () {
  local name=$1; local exec=$2; local restart=${3:-on-failure}
  local unit="${SYSTEMD_DIR}/${SUFFIX}_${name}.service"
  [[ -f $unit ]] && return
  cat > "$unit" <<EOF
[Unit]
Description=Abstract Parallels - ${name}

[Service]
Type=simple
ExecStart=${exec}
Restart=${restart}
EOF
  echo "• installed $unit"
}

# ─── Step 1: create units (idempotent) ────────────────────────
write_unit "clip_win"     "${SRC_DIR}/clipit/run_clipit_gui.sh both --detach"
write_unit "services_mgr" "${SRC_DIR}/services_mgr/run_services_manager.sh"
write_unit "api_gui"      "${SRC_DIR}/apis/run_api_gui.sh"
write_unit "dashboard"    "${SRC_DIR}/parallels_dashboard.sh"       no

systemctl --user daemon-reload

# ─── Step 2: dispatcher ───────────────────────────────────────
cmd="${1:-install}"

case $cmd in
  install)
    for n in "${UNITS[@]}"; do
      systemctl --user enable --now "${SUFFIX}_${n}.service"
    done
    echo -e "\n✅  All services enabled & started."
    echo   "   View logs with: $0 logs"
    ;;
  start|stop|restart)
    for n in "${UNITS[@]}"; do
      systemctl --user "$cmd" "${SUFFIX}_${n}.service"
    done
    ;;
  status)
    systemctl --user status "${SUFFIX}_"{clip_win,services_mgr,api_gui,dashboard}.service
    ;;
  logs)
    echo "⌨  Ctrl-C to exit."
    journalctl --user -fu "${SUFFIX}_"{clip_win,services_mgr,api_gui}.service
    ;;
  *)
    echo "Usage: $0 [install|start|stop|restart|status|logs]" >&2
    exit 1
    ;;
esac
