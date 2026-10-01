#!/usr/bin/env bash
#
# preview.sh — eyeball the assets in a real browser.
#
# Animated SVG only animates when a browser renders it, so checking these in
# a text editor (or a GitHub diff) tells you nothing about whether they move.
#
# Usage:
#   bash scripts/preview.sh              # list assets, print the command
#   bash scripts/preview.sh --serve      # start a local server and open it
#   bash scripts/preview.sh --port 9000
#
# With no flags this never blocks and never starts a server.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SERVE=0
PORT=8080
while (( $# )); do
  case "$1" in
    --serve) SERVE=1 ;;
    --port)  PORT="${2:-8080}"; shift ;;
    -h|--help)
      sed -n '3,14p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

echo
echo "  ASSET LIBRARY"
echo "  ────────────────────────────────────────────────────────────"
find assets -name '*.svg' -not -path '*/live/*' | sort | while IFS= read -r f; do
  kb=$(( $(wc -c < "$f" | tr -d ' ') / 1024 ))
  printf '  %-44s %4sKB   http://localhost:%s/%s\n' "$f" "$kb" "$PORT" "$f"
done
echo
echo "  Total: $(find assets -name '*.svg' -not -path '*/live/*' | wc -l | tr -d ' ') assets, \
$(( $(find assets -name '*.svg' -not -path '*/live/*' -exec cat {} + | wc -c | tr -d ' ') / 1024 ))KB total"
echo
echo "  Start the server with:  bash scripts/preview.sh --serve"
echo

if (( SERVE == 0 )); then
  exit 0
fi

echo "  Serving $ROOT on http://localhost:$PORT  (ctrl-c to stop)"
echo
exec python3 -m http.server "$PORT" --bind 127.0.0.1
