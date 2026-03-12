# VPN Infrastructure Toolkit
*General‑purpose proxy/VPN tools for accessing restricted APIs and surviving in the real‑world network environment.*

## Purpose
Some APIs and web services restrict access based on geography or IP reputation. This toolkit provides scripts and knowledge to manage Clash Verge (a proxy client) programmatically, enabling automated proxy selection, latency testing, and system‑proxy configuration.

## Contents

### Topics (Knowledge)
- `clash‑verge‑ops.md` – Comprehensive guide to Clash Verge’s Unix‑socket API, configuration keys, macOS system‑proxy commands, and latency‑testing methodology.

### Delivery (Scripts)
- `clash_speed_test.py` – Batch latency test for all proxy groups; reports fastest per region.
- `clash_fastest_non_hk.py` – **Primary selector**: Pings all non‑Hong Kong proxies, prioritizes US proxies, and selects the fastest available; can optionally switch the global selector.

## How to Use

### Fastest Non‑HK Proxy Selection
```bash
cd /Users/xyx/.openclaw/workspace
python3 infrastructure/vpn/delivery/clash_fastest_non_hk.py [--switch] [--dry-run]
```

**Options:**
- `--switch` – Actually switch the GLOBAL selector to the chosen proxy.
- `--dry-run` – Only print results (default).
- `--fast` – *(planned)* Test only the currently selected proxy of each group.

### System Proxy Toggle
The scripts do **not** automatically enable macOS system proxy; that must be done via:
- Clash Verge tray‑icon UI, or
- The `networksetup` commands documented in `clash‑verge‑ops.md`.

## Dependencies
- Clash Verge (or any mihomo‑compatible client) running with Unix socket at `/tmp/verge/verge‑mihomo.sock`.
- Secret token `set‑your‑secret` (default; adjust in script if changed).
- Python 3 with standard libraries.

## Integration with OpenClaw
- These scripts can be called manually or via OpenClaw’s `exec` tool.
- The knowledge file is referenced in the workspace’s main knowledge index (`knowledge/INDEX.md`).
- No scheduled automation is configured by default; the Operator may trigger selection on demand.

## Future Enhancements
- Auto‑switch cron job (e.g., every 5 minutes) to maintain lowest‑latency non‑HK proxy.
- Proxy‑guard integration (automatically disable system proxy after a timeout).
- Health checks and fallback to direct connection if all proxies fail.

---

*Created: 2026‑03‑12 · Part of the Infrastructure toolkit under the OpenClaw workspace.*