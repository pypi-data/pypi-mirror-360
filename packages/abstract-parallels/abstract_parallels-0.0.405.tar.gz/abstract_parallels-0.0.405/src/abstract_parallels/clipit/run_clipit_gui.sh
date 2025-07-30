#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  run_clipit_gui.sh
#
#  Launch the PyQt5 “Remote Systemd Service Viewer”.
#
#  Examples
#  ─────────────────────────────────────────────────────────────
#  ./run_clipit_gui.sh           # normal foreground launch
#  ./run_clipit_gui.sh -d        # launch detached (background)
#  ./run_clipit_gui.sh --debug   # pass extra args to Python
#  ./run_clipit_gui.sh --detach --debug
#
#  Flags
#  ─────────────────────────────────────────────────────────────
#  -d | --detach     Detach from this terminal, keep running
#  -h | --help       Show this help
#
#  All **other** options are forwarded unchanged to get_clipit.py
# ──────────────────────────────────────────────────────────────

# 1) Fail safely but *stay alive* if a sub-shell dies
set -Eeuo pipefail
trap 'echo "💥  Unhandled error – exit code $?"' ERR

# 2) Ignore SIGHUP so losing the parent TTY doesn’t kill the GUI
trap "" HUP

# 3) Ensure job control even when launched via cron/systemd
set -m

##########  LOCATE PYTHON ENTRYPOINT  ##########
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PY_SCRIPT="${SCRIPT_DIR}/get_clipit.py"

##########  HELP  ##########
usage() {
  sed -n '2,32p' "$0"    # print header block above
  exit "${1:-0}"
}

##########  ARG PARSING  ##########
detach=false
py_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--detach) detach=true ;;
    -h|--help)   usage 0 ;;
    --*)         py_args+=("$1") ;;   # forward long opts to Python
    *)           py_args+=("$1") ;;   # forward positional args
  esac
  shift
done

##########  SELF-DETACH  ##########
if $detach; then
  log="${HOME}/services_manager.log"
  setsid "$0" "${py_args[@]}" >"$log" 2>&1 < /dev/null &
  echo "Services Manager launched in background → $log"
  exit 0
fi

##########  MAIN LAUNCH  ##########
exec python3 "$PY_SCRIPT" "${py_args[@]}"
