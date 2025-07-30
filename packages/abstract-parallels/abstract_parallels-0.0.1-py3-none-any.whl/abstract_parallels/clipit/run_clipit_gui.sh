#!/usr/bin/env bash
# ----------------------------------------------------------
# run_clipit_gui.sh   (hardened)
#
#   Usage examples
#   --------------
#   ./run_clipit_gui.sh                 # same as “both”
#   ./run_clipit_gui.sh gui             # GUI only
#   ./run_clipit_gui.sh clipit          # clipboard watcher only
#   ./run_clipit_gui.sh both            # run both
#   ./run_clipit_gui.sh --detach gui    # run GUI, detached from terminal
#   ./run_clipit_gui.sh -d              # run both, detached
#
#   Flags
#   -----
#   -d | --detach   Launch in the background (no terminal attachment)
#   -h | --help     Show this help
# ----------------------------------------------------------

# 1) Fail safely but *stay alive* if a sub-shell dies
set -Eeuo pipefail
trap 'echo "💥  Unhandled error – exit code $?"' ERR

# 2) Ignore SIGHUP so losing the parent TTY doesn’t kill us
trap "" HUP

# 3) Ensure job control even when launched via cron/systemd
set -m

##########  FUNCTIONS  ##########
usage() {
  cat <<EOF
Usage: $0 [clipit|gui|both] [-d|--detach]

  clipit   Run abstract_clipit.run_clipit() only
  gui      Run abstract_gui.start_window_info_gui() only
  both     Run both (default) – clipit in background, GUI in foreground
  -d, --detach
           Detach from the current terminal and keep running
EOF
  exit 1
}

run_clipit() {
  python - <<'PY'
from abstract_clipit import run_clipit
run_clipit()
PY
}

run_gui() {
  python - <<'PY'
from abstract_gui import start_window_info_gui
start_window_info_gui()
PY
}

##########  ARG PARSING  ##########
mode="both"
detach=false

for arg in "$@"; do
  case "$arg" in
    clipit|gui|both) mode="$arg" ;;
    -d|--detach)     detach=true ;;
    -h|--help)       usage ;;
    *) echo "Unknown option: $arg"; usage ;;
  esac
done

##########  SELF-DETACH  ##########
if $detach; then
  log="${HOME}/run_clipit_gui.log"
  # Re-exec in a brand-new session, silence stdin, capture stdout/stderr
  setsid "$0" "$mode" >"$log" 2>&1 < /dev/null &
  echo "Launched '$mode' in background. Logging to $log"
  exit 0
fi

##########  MAIN LAUNCHER  ##########
case "$mode" in
  clipit)
    run_clipit
    ;;

  gui)
    run_gui
    ;;

  both)
    # --- Start clipboard watcher in background ---
    # --- Start clipboard watcher in its own session & disown ---
    setsid bash -c 'run_clipit' >/dev/null 2>&1 &
    CLIP_PID=$!
    disown "$CLIP_PID"

    # --- Ensure it stops when GUI ends or on Ctrl-C ---
    cleanup() {
      if kill -0 "$CLIP_PID" 2>/dev/null; then
        kill "$CLIP_PID"
        wait "$CLIP_PID" 2>/dev/null || true
      fi
    }
    trap cleanup EXIT INT TERM

    # --- Launch GUI (blocks) ---
    run_gui
    ;;
esac
