#!/bin/bash
# Restart Clash Verge (GUI + core) on macOS
# Usage: ./restart_clash_verge.sh

set -e

echo "🔄 Restarting Clash Verge..."

# 1. Quit the GUI via AppleScript (graceful)
echo "   Quitting GUI..."
osascript -e 'tell application "Clash Verge" to quit' 2>/dev/null || true
sleep 2

# 2. Kill the core process (verge-mihomo) – requires sudo
# if pgrep -f verge-mihomo >/dev/null; then
#     echo "   Killing core process (sudo required)..."
#     sudo pkill -f verge-mihomo 2>/dev/null || true
#     sleep 1
# else
#     echo "   Core process already stopped."
# fi

# 3. Reopen the app
echo "   Opening Clash Verge..."
open -a "Clash Verge"

echo "✅ Done. The app should be starting up."
echo "   Wait ~10 seconds for the core to initialize, then run:"
echo "   python3 infrastructure/vpn/delivery/vpn_check.py"