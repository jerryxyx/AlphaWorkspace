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

### Clash Verge

- **Socket path**: `/tmp/verge/verge‑mihomo.sock`
- **Secret**: `set‑your‑secret` (default)
- **TUN toggle script**: `python3 infrastructure/vpn/delivery/clash_tun_toggle.py`
  - `--toggle` – flip TUN state (default) – **syncs GUI and runtime**
  - `--on` – ensure TUN enabled (for cron jobs)
  - `--off` – ensure TUN disabled
  - `--status` – show current state (API + YAML)
- **Fastest non‑HK proxy selector**: `python3 infrastructure/vpn/delivery/clash_fastest_non_hk.py [--switch]`
- **VPN status check**: `python3 infrastructure/vpn/delivery/vpn_check.py` – detailed health (IP, TUN, proxies)
- **IP region check**: `python3 infrastructure/vpn/delivery/ip_region_check.py` – quick IP/country
- **System proxy toggle (legacy)**: macOS `networksetup` commands (see `infrastructure/vpn/topics/clash‑verge‑ops.md`)
- **Restart script**: `infrastructure/vpn/delivery/restart_clash_verge.sh` – quits GUI, kills core, reopens (sudo required)

**Quick aliases** (add to your shell rc if desired):
```bash
alias tun-on='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/clash_tun_toggle.py --on'
alias tun-off='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/clash_tun_toggle.py --off'
alias tun-toggle='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/clash_tun_toggle.py --toggle'
alias tun-status='python3 /Users/xyx/.openclaw/workspace/infrastructure/vpn/delivery/clash_tun_toggle.py --status'
```

---

Add whatever helps you do your job. This is your cheat sheet.
