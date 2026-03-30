#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_SRC="$SCRIPT_DIR/com.user.mihomo.root.plist"
PLIST_DST="/Library/LaunchDaemons/com.user.mihomo.root.plist"

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)."
    exit 1
fi

if [[ ! -f "$PLIST_SRC" ]]; then
    echo "Root plist not found at $PLIST_SRC"
    exit 1
fi

echo "Installing root LaunchDaemon..."
cp "$PLIST_SRC" "$PLIST_DST"
launchctl load -w "$PLIST_DST"
echo "Root daemon installed and started."