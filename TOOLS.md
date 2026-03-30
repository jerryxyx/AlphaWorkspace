# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### Clash Verge (deprecated – scripts archived)

- **Note**: Clash Verge has been replaced by Mihomo (Clash Meta) for command‑line management.
- **Archived scripts**: `clash_tun_toggle.py.bak`, `clash_speed_test.py.bak`, `vpn_check.py.bak` (original scripts renamed).
- **Fastest non‑HK selector (updated)**: `python3 infrastructure/vpn/delivery/clash_fastest_non_hk.py` – now a dry‑run tool that prints the fastest non‑HK group name (no switching).
- **IP region check**: `python3 infrastructure/vpn/delivery/ip_region_check.py` – still works for quick IP/region.
- **Restart script**: `infrastructure/vpn/delivery/restart_clash_verge.sh` – may be used to stop Clash Verge GUI.

### Mihomo (Clash Meta) – command‑line alternative

- **Installation**: `brew install mihomo`
- **Subscription URL**: `https://api.jetcamoe.com/api/v1/public/services/54066/0ff587d3efb4537fa73df5f646133051?agent=clash-hysteria`
- **Config setup**: `python3 infrastructure/vpn/delivery/mihomo_setup.py setup` – downloads remote config, merges local overrides (TUN, external‑controller, ports)
- **Management script**: `python3 infrastructure/vpn/delivery/mihomoctl.py`
  - `status` – current selector and IP
  - `list‑groups` – available country groups
  - `fastest‑non‑hk` – switch to fastest non‑HK proxy group
  - `switch <group> <target>` – switch selector
  - `latency` – test proxy latencies
  - `set‑proxy` / `unset‑proxy` – configure macOS system proxy
  - `start` / `stop` / `restart` – control launchd service (user‑level)
  - `install‑root‑daemon` – install root LaunchDaemon for TUN mode (requires sudo)
  - `root‑start` – start root daemon (requires sudo)
- **Test script**: `python3 infrastructure/vpn/delivery/test_mihomoctl.py [--verbose] [--no-switch]` – comprehensive test of all functions.
- **Service**: LaunchAgent `com.user.mihomo` loaded at login (runs as user, no TUN). For TUN mode, use root LaunchDaemon.
- **Ports**: mixed‑port 7890, SOCKS 7891, redir‑port 7892, external‑controller 9095, secret `set‑your‑secret`
- **TUN note**: TUN is enabled in config (`tun.enable: true`). To activate TUN (full traffic capture), run mihomo as root via the provided root daemon.

**Quick aliases** (add to your shell rc if desired):
```bash
alias mihomo-status='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/mihomoctl.py status'
alias mihomo-fastest='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/mihomoctl.py fastest-non-hk'
alias mihomo-proxy-on='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/mihomoctl.py set-proxy'
alias mihomo-proxy-off='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/mihomoctl.py unset-proxy'
alias mihomo-install-root='sudo /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/install_root_daemon.sh'
```

**Note**: The legacy Clash Verge scripts (`clash_tun_toggle.py`, `clash_speed_test.py`, `vpn_check.py`) have been renamed to `.bak` as they no longer work with the current setup. Use `mihomoctl` instead.

---

Add whatever helps you do your job. This is your cheat sheet.
