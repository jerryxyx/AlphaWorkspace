# Clash Verge Operations Guide
*Last updated: 2026‑03‑29*

## Basics

**Application**: `/Applications/Clash Verge.app`  
**Config directory**: `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/`  
**Unix socket**: `/tmp/verge/verge‑mihomo.sock`  
**Secret**: `set‑your‑secret` (default; change in `config.yaml`)

## Proxy Groups & Latency Testing

### List all proxies
```bash
curl -s --unix-socket /tmp/verge/verge-mihomo.sock \
  -H "Authorization: Bearer set-your-secret" \
  http://localhost/proxies | jq .
```

### Test latency of a specific proxy
```bash
curl -s --unix-socket /tmp/verge/verge-mihomo.sock \
  -H "Authorization: Bearer set-your-secret" \
  "http://localhost/proxies/TG-HK-1(https)/delay?timeout=5000&url=https://cp.cloudflare.com/generate_204"
```

### Python script for batch testing
See `/Users/xyx/.openclaw/workspace/temp/clash_speed_test.py`

## System Proxy Control

### Enable via config file
1. Edit `verge.yaml`:
   ```yaml
   enable_system_proxy: true
   system_proxy_bypass: null   # or [] for empty bypass list
   use_default_bypass: true    # bypass localhost, 127.0.0.1, etc.
   proxy_host: 127.0.0.1
   verge_mixed_port: 7897      # HTTP/SOCKS proxy port
   ```
2. **Restart Clash Verge** (kill `verge‑mihomo` process and relaunch app).

### Verify system proxy settings (macOS)
```bash
networksetup -getwebproxy Wi-Fi
networksetup -getsocksfirewallproxy Wi-Fi
```

### Enable via macOS CLI (fallback)
```bash
# HTTP proxy
networksetup -setwebproxy Wi-Fi 127.0.0.1 7897
networksetup -setwebproxystate Wi-Fi on

# SOCKS proxy
networksetup -setsocksfirewallproxy Wi-Fi 127.0.0.1 7897
networksetup -setsocksfirewallproxystate Wi-Fi on
```

**Bypass domains** (optional):
```bash
networksetup -setproxybypassdomains Wi-Fi "localhost" "127.0.0.1" "*.local"
```

## TUN (VPN) Mode Control

TUN mode routes all traffic (including API calls) through the proxy at the network‑layer, eliminating geo‑blocking leaks that can occur with system‑proxy only. Essential for accessing Claude API from Hong Kong.

**Sync Guarantee:** The script below updates both the YAML config file (read by the GUI) and the runtime config via `PUT /configs?force=true`, ensuring the Clash Verge GUI reflects the actual TUN state.

### Check current TUN state
```bash
curl -s --unix-socket /tmp/verge/verge-mihomo.sock \
  -H "Authorization: Bearer set-your-secret" \
  http://localhost/configs | jq '.tun.enable'
```

### Toggle TUN mode with Python script (recommended)
A ready‑to‑use script is available in the VPN toolkit:
```bash
cd /Users/xyx/.openclaw/workspace
python3 infrastructure/vpn/delivery/clash_tun_toggle.py [--on|--off|--toggle] [--dry-run]
```

**Examples:**
- `python3 infrastructure/vpn/delivery/clash_tun_toggle.py --toggle` – flip TUN state (syncs GUI)
- `python3 infrastructure/vpn/delivery/clash_tun_toggle.py --on` – ensure TUN enabled
- `python3 infrastructure/vpn/delivery/clash_tun_toggle.py --off` – ensure TUN disabled
- `python3 infrastructure/vpn/delivery/clash_tun_toggle.py --status` – show current state

**How it works:** The script modifies `tun.enable` in `config.yaml`, then sends a `PUT /configs?force=true` request with the updated YAML content, forcing the `verge‑mihomo` process to reload the configuration. This keeps the GUI and runtime in sync.

### Manual toggle via API (runtime‑only)
```bash
# Enable TUN (runtime only; GUI may stay out‑of‑sync)
curl -X PATCH --unix-socket /tmp/verge/verge-mihomo.sock \
  -H "Authorization: Bearer set-your-secret" \
  -H "Content-Type: application/json" \
  -d '{"tun":{"enable":true}}' http://localhost/configs

# Disable TUN (runtime only)
curl -X PATCH --unix-socket /tmp/verge/verge-mihomo.sock \
  -H "Authorization: Bearer set-your-secret" \
  -H "Content-Type: application/json" \
  -d '{"tun":{"enable":false}}' http://localhost/configs
```

### Reload config from file (after manual YAML edit)
```bash
# Read current YAML, send PUT to reload (syncs runtime with file)
curl -X PUT --unix-socket /tmp/verge/verge-mihomo.sock \
  -H "Authorization: Bearer set-your-secret" \
  -H "Content-Type: application/json" \
  -d '{"path":"","payload":"$(cat ~/Library/Application\ Support/io.github.clash-verge-rev.clash-verge-rev/config.yaml)"}' \
  "http://localhost/configs?force=true"
```

### Integration with cron jobs
To ensure TUN is enabled before a scheduled task (e.g., morning report), add a pre‑hook:
```bash
python3 infrastructure/vpn/delivery/clash_tun_toggle.py --on
```

## Current Configuration (2026‑03‑12)

### Active profile
- **Remote**: `JetStream20251123` (`RgZwNAPzWx5C.yaml`)
- **Selected group**: `🌏 当前选择` → `🇺🇸 美国自动` → `TG‑US‑1(hysteria)`
- **Mixed port**: `7897`

### Proxy groups
| Group | Type | Current selection | Latency (ms) |
|-------|------|-------------------|--------------|
| 🌏 当前选择 | Selector | 🇺🇸 美国自动 | – |
| 🇭🇰 香港自动 | Fallback | XG‑HK‑1(https) | 183 |
| 🇨🇳 台湾自动 | Fallback | TG‑TW‑1(https) | 195 |
| 🇸🇬 新加坡自动 | Fallback | TG‑SG‑1(https) | 222 |
| 🇯🇵 日本自动 | Fallback | TG‑JP‑1(https) | 224 |
| 🇺🇸 美国自动 | Fallback | TG‑US‑1(hysteria) | 452 |

### Fastest proxies (per region)
- **Hong Kong**: XG‑HK‑1(https) – 177 ms
- **Taiwan**: TG‑TW‑1(https) – 195 ms
- **Singapore**: TG‑SG‑1(https) – 222 ms
- **Japan**: TG‑JP‑1(https) – 224 ms
- **USA**: TG‑US‑1(hysteria) – 452 ms

## Troubleshooting

### Socket not found
- Ensure Clash Verge is running (`ps aux | grep verge‑mihomo`).
- Socket path may change after restart.

### “Failed to connect” errors
- Check secret token in `config.yaml` matches the one used in requests.
- Verify the `verge‑mihomo` process is listening (`lsof -U | grep verge`).

### System proxy not applying
- Restart Clash Verge after config change.
- Check `sysproxy_tray_icon` setting (should be `false` unless you want tray indicator).
- Manually enable via macOS System Preferences → Network → Advanced → Proxies.

## Automation Ideas

1. **Periodic latency tests** – cron job that logs fastest proxy per region.
2. **Auto‑switch on high latency** – script that changes group selection when current proxy exceeds threshold.
3. **System proxy toggle** – keyboard shortcut to enable/disable via CLI.

## Notes

- The `enable_proxy_guard` setting (when `true`) will automatically disable system proxy after `proxy_guard_duration` seconds (default 30).
- `verge_http_enabled` and `verge_socks_enabled` control separate HTTP/SOCKS ports; `mixed‑port` handles both.