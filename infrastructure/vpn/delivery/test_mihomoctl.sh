#!/bin/bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(pwd)"
MIHOMOCTL="$SCRIPT_DIR/mihomoctl.py"
FASTEST="$SCRIPT_DIR/clash_fastest_non_hk.py"
LOG="/tmp/mihomo_test_$(date +%Y%m%d_%H%M%S).log"

echo "=== Mihomo Control Test ===" | tee "$LOG"

# 0. Ensure mihomo is running
echo "0. Checking mihomo status..." | tee -a "$LOG"
python3 "$MIHOMOCTL" status 2>&1 | tee -a "$LOG"
if [ $? -ne 0 ]; then
    echo "⚠️  Mihomo not reachable, starting..." | tee -a "$LOG"
    python3 "$MIHOMOCTL" start 2>&1 | tee -a "$LOG"
    sleep 3
fi

# 1. Switching off and on (proxy selector)
echo "" | tee -a "$LOG"
echo "1. Switching GLOBAL selector to DIRECT (off)..." | tee -a "$LOG"
python3 "$MIHOMOCTL" switch GLOBAL DIRECT 2>&1 | tee -a "$LOG"
sleep 2
echo "   Current IP (direct):" | tee -a "$LOG"
curl -s --connect-timeout 5 http://httpbin.org/ip 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "   Switching GLOBAL selector to 🇯🇵 日本自动 (on)..." | tee -a "$LOG"
python3 "$MIHOMOCTL" switch GLOBAL "🇯🇵 日本自动" 2>&1 | tee -a "$LOG"
sleep 2
echo "   Current IP (via proxy):" | tee -a "$LOG"
curl -x http://127.0.0.1:7890 -s --connect-timeout 5 http://httpbin.org/ip 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

# 2. Test speed for proxies and return the fastest non‑HK one
echo "" | tee -a "$LOG"
echo "2. Testing fastest non‑HK group (dry‑run)..." | tee -a "$LOG"
FASTEST_GROUP=$(python3 "$FASTEST" 2>&1 | tee -a "$LOG")
echo "   Fastest non‑HK group: $FASTEST_GROUP" | tee -a "$LOG"

# 3. Switch to the selected proxy via TUN mode for all traffic
#    Since TUN requires root daemon, we'll switch GLOBAL selector as user‑level simulation.
echo "" | tee -a "$LOG"
echo "3. Switching GLOBAL selector to fastest group ($FASTEST_GROUP)..." | tee -a "$LOG"
python3 "$MIHOMOCTL" switch GLOBAL "$FASTEST_GROUP" 2>&1 | tee -a "$LOG"
sleep 2

# 4. Confirm the IP address get updated (non‑HK)
echo "" | tee -a "$LOG"
echo "4. Verifying IP address (non‑HK)..." | tee -a "$LOG"
IP_OUT=$(curl -x http://127.0.0.1:7890 -s --connect-timeout 5 http://httpbin.org/ip 2>&1)
echo "$IP_OUT" | tee -a "$LOG"
if echo "$IP_OUT" | grep -q '"origin"'; then
    IP=$(echo "$IP_OUT" | jq -r .origin 2>/dev/null || echo "")
    if [ -n "$IP" ]; then
        echo "   IP address: $IP" | tee -a "$LOG"
        # Optional: geolocation lookup
        COUNTRY=$(curl -s --connect-timeout 5 "https://ipinfo.io/$IP/country" 2>&1)
        echo "   Country code: $COUNTRY" | tee -a "$LOG"
        if [[ "$COUNTRY" != "HK" && "$COUNTRY" != "Hong Kong" ]]; then
            echo "✅ SUCCESS: IP is non‑HK ($COUNTRY)." | tee -a "$LOG"
        else
            echo "⚠️  WARNING: IP appears to be HK ($COUNTRY)." | tee -a "$LOG"
        fi
    fi
fi

# Additional: latency test of current group
echo "" | tee -a "$LOG"
echo "5. Latency test of current group ($FASTEST_GROUP)..." | tee -a "$LOG"
python3 "$MIHOMOCTL" latency --group "$FASTEST_GROUP" --limit 5 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "=== Test complete ===" | tee -a "$LOG"
echo "Log saved to $LOG" | tee -a "$LOG"