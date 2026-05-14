#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="genshin_tracker_macos"
BUILD_SCRIPT="$ROOT_DIR/build-macos.sh"
APP_BINARY="$ROOT_DIR/external/cvAutoTrack/build-macos/bin/$APP_NAME"

MODE="${1:-run}"
if [[ $# -gt 0 ]]; then
    shift
fi

pkill -x "$APP_NAME" >/dev/null 2>&1 || true

"$BUILD_SCRIPT" --configuration "${CONFIGURATION:-Release}"

case "$MODE" in
    run)
        if [[ $# -eq 0 ]]; then
            exec "$APP_BINARY" --status
        fi
        exec "$APP_BINARY" "$@"
        ;;
    --debug|debug)
        exec lldb -- "$APP_BINARY" "$@"
        ;;
    --logs|logs)
        "$APP_BINARY" "$@" &
        exec /usr/bin/log stream --info --style compact --predicate "process == \"$APP_NAME\""
        ;;
    --telemetry|telemetry)
        "$APP_BINARY" "$@" &
        exec /usr/bin/log stream --info --style compact --predicate "process == \"$APP_NAME\""
        ;;
    --verify|verify)
        "$APP_BINARY" --status >/tmp/genshin_tracker_macos.verify.log 2>&1
        test -x "$APP_BINARY"
        ;;
    *)
        exec "$APP_BINARY" "$MODE" "$@"
        ;;
esac
