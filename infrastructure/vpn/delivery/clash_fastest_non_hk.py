#!/usr/bin/env python3
"""
Clash Verge Fastest Non‑HK Proxy Selector

Pings all proxies, excludes Hong Kong (HK) proxies, prioritizes US proxies,
and selects the fastest available. Switches the GLOBAL selector to that proxy.

Usage:
    python3 clash_fastest_non_hk.py [--switch] [--dry-run]

Options:
    --switch    Actually switch GLOBAL selector (default: dry‑run)
    --dry-run   Only print results, don't switch (default)
"""

import json
import subprocess
import sys
import time
import argparse
from typing import Dict, List, Tuple, Optional

SOCKET_PATH = "/tmp/verge/verge-mihomo.sock"
SECRET = "set-your-secret"
BASE_URL = "http://localhost"

def curl_unix(path: str, params: Optional[Dict] = None, method: str = "GET", data: Optional[str] = None) -> Optional[str]:
    """Make HTTP request to Unix socket."""
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    cmd = ["curl", "-s", "--unix-socket", SOCKET_PATH, "-H", f"Authorization: Bearer {SECRET}"]
    if method != "GET":
        cmd.extend(["-X", method])
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", data])
    cmd.append(url)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"Timeout for {path}", file=sys.stderr)
        return None

def get_proxies() -> Optional[Dict]:
    resp = curl_unix("/proxies")
    if not resp:
        return None
    try:
        data = json.loads(resp)
        return data.get("proxies", {})
    except json.JSONDecodeError:
        print(f"Invalid JSON: {resp[:200]}", file=sys.stderr)
        return None

def test_proxy(name: str) -> Optional[int]:
    """Test latency for a single proxy. Returns ms or None if failed."""
    resp = curl_unix(f"/proxies/{name}/delay", {"timeout": "5000", "url": "https://cp.cloudflare.com/generate_204"})
    if not resp:
        return None
    try:
        data = json.loads(resp)
        return data.get("delay")
    except:
        return None

def is_hk_proxy(name: str) -> bool:
    """Heuristic: proxy name contains HK or group is Hong Kong."""
    # Proxy names like TG-HK-1(https), XG-HK-1(hysteria), etc.
    return "HK" in name.upper()

def get_proxy_group_mapping(proxies: Dict) -> Dict[str, str]:
    """Map proxy name → group name."""
    mapping = {}
    for group_name, info in proxies.items():
        if "all" not in info:
            continue
        for proxy in info.get("all", []):
            mapping[proxy] = group_name
    return mapping

def main():
    parser = argparse.ArgumentParser(description="Select fastest non‑HK proxy")
    parser.add_argument("--switch", action="store_true", help="Switch GLOBAL selector to chosen proxy")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    parser.add_argument("--fast", action="store_true", help="Test only the 'now' proxy of each group (faster)")
    args = parser.parse_args()
    if args.switch:
        args.dry_run = False

    print("=== Clash Verge Fastest Non‑HK Proxy Selector ===\n")
    proxies = get_proxies()
    if not proxies:
        print("Failed to fetch proxies")
        sys.exit(1)

    # Identify country groups (exclude Hong Kong, exclude GLOBAL and selector groups)
    country_groups = []
    for name, info in proxies.items():
        if "all" not in info:
            continue
        # Exclude Hong Kong group
        if "香港" in name or "🇭🇰" in name:
            continue
        # Exclude GLOBAL and "🌏 当前选择" (selector groups)
        if name in ["GLOBAL", "🌏 当前选择"]:
            continue
        # Include only groups that look like country groups (have flag emoji)
        # This catches 🇺🇸 美国自动, 🇨🇳 台湾自动, 🇸🇬 新加坡自动, 🇯🇵 日本自动
        if any(flag in name for flag in ["🇺🇸", "🇨🇳", "🇸🇬", "🇯🇵", "🇩🇪", "🇹🇼", "🇭🇰"]):
            country_groups.append((name, info))
        # If you want to include other groups like "MSK-DE-1" etc., adjust accordingly

    print(f"Found {len(country_groups)} non‑HK country groups:")
    for name, _ in country_groups:
        print(f"  - {name}")

    # Build list of all proxies in these groups, mapping to group
    proxy_group_map = get_proxy_group_mapping(proxies)
    candidates = []
    for group_name, info in country_groups:
        for proxy in info.get("all", []):
            # Skip if proxy name itself contains HK (just in case)
            if is_hk_proxy(proxy):
                continue
            candidates.append((proxy, group_name))

    print(f"\nTesting {len(candidates)} non‑HK proxies...")
    results = []
    for i, (proxy, group) in enumerate(candidates):
        print(f"  [{i+1}/{len(candidates)}] {proxy} ({group}) ... ", end="", flush=True)
        delay = test_proxy(proxy)
        if delay is None or delay == 0:
            print("failed")
        else:
            print(f"{delay} ms")
            results.append((proxy, group, delay))
        time.sleep(0.1)  # be nice to the API

    if not results:
        print("\n❌ No working non‑HK proxies found.")
        sys.exit(1)

    # Separate US proxies from others
    us_results = [(p, g, d) for p, g, d in results if "美国" in g or "🇺🇸" in g or "US" in p.upper()]
    other_results = [(p, g, d) for p, g, d in results if (p, g, d) not in us_results]

    print("\n--- Results ---")
    if us_results:
        print("US proxies:")
        for p, g, d in sorted(us_results, key=lambda x: x[2]):
            print(f"  {p:30} {g:20} {d:>6} ms")
    if other_results:
        print("Other non‑HK proxies:")
        for p, g, d in sorted(other_results, key=lambda x: x[2]):
            print(f"  {p:30} {g:20} {d:>6} ms")

    # Pick winner: fastest US if any, otherwise fastest other
    if us_results:
        winner = min(us_results, key=lambda x: x[2])
        print(f"\n✅ Fastest US proxy: {winner[0]} ({winner[1]}) – {winner[2]} ms")
    else:
        winner = min(other_results, key=lambda x: x[2])
        print(f"\n✅ Fastest non‑HK proxy (no US available): {winner[0]} ({winner[1]}) – {winner[2]} ms")

    # Switch GLOBAL selector if requested
    if not args.dry_run:
        print(f"\n🔄 Switching GLOBAL selector to {winner[0]}...")
        resp = curl_unix("/proxies/GLOBAL", method="PUT", data=json.dumps({"name": winner[0]}))
        if resp is None:
            print("⚠️  Switch may have failed (no response)")
        else:
            print("✅ Switch command sent.")
        # Verify
        time.sleep(1)
        check = curl_unix("/proxies/GLOBAL")
        if check:
            try:
                data = json.loads(check)
                now = data.get("now")
                print(f"   GLOBAL now points to: {now}")
            except:
                pass
    else:
        print(f"\n📋 Dry run – to actually switch, run with --switch")

    # Also show current IP via proxy (optional)
    print("\n🌐 Testing current proxy IP...")
    try:
        ip_result = subprocess.run(
            ["curl", "-s", "-x", "http://127.0.0.1:7897", "http://httpbin.org/ip", "--connect-timeout", "5"],
            capture_output=True, text=True, timeout=10
        )
        if ip_result.returncode == 0:
            ip_data = json.loads(ip_result.stdout)
            print(f"   Current outgoing IP: {ip_data.get('origin')}")
        else:
            print("   Could not fetch IP")
    except:
        print("   IP test failed")

if __name__ == "__main__":
    main()