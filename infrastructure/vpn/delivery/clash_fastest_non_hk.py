#!/usr/bin/env python3
"""
Mihomo Fastest Non‑HK Group Selector (Dry‑Run)

Pings current proxy of each non‑HK country group, selects the fastest.
Outputs only the winning group name (for use in scripts) unless --verbose.

Usage:
    python3 clash_fastest_non_hk.py [--verbose]
"""

import json
import subprocess
import sys
import argparse
from typing import Optional

SECRET = "set-your-secret"
BASE_URL = "http://127.0.0.1:9095"

def api_request(path: str, method: str = "GET", data: Optional[str] = None) -> Optional[str]:
    """Make HTTP request to Mihomo API."""
    cmd = ["curl", "-s", "-H", f"Authorization: Bearer {SECRET}", f"{BASE_URL}{path}"]
    if method != "GET":
        cmd.extend(["-X", method])
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", data])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"Timeout for {path}", file=sys.stderr)
        return None

def get_proxies():
    resp = api_request("/proxies")
    if not resp:
        return None
    try:
        data = json.loads(resp)
        return data.get("proxies", {})
    except json.JSONDecodeError:
        print(f"Invalid JSON: {resp[:200]}", file=sys.stderr)
        return None

def test_latency(proxy_name: str) -> Optional[int]:
    """Test latency for a single proxy. Returns ms or None if failed."""
    resp = api_request(f"/proxies/{proxy_name}/delay?timeout=5000&url=https://cp.cloudflare.com/generate_204")
    if not resp:
        return None
    try:
        data = json.loads(resp)
        return data.get("delay")
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description="Select fastest non‑HK group (dry‑run)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed progress")
    args = parser.parse_args()

    proxies = get_proxies()
    if not proxies:
        print("Failed to fetch proxies", file=sys.stderr)
        sys.exit(1)

    # Identify country groups (Fallback type, exclude Hong Kong)
    candidate_groups = []
    for name, info in proxies.items():
        if info.get("type") == "Fallback" and "香港" not in name and "HK" not in name:
            candidate_groups.append(name)
    
    if not candidate_groups:
        print("No non‑HK country groups found", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Found {len(candidate_groups)} non‑HK country groups:")
        for name in candidate_groups:
            print(f"  - {name}")

    # Test latency of each group's current proxy
    best_group = None
    best_latency = float('inf')
    for group in candidate_groups:
        now = proxies[group].get("now")
        if not now:
            continue
        delay = test_latency(now)
        if delay is None:
            continue
        if args.verbose:
            print(f"  {group}: {delay} ms")
        if delay < best_latency:
            best_latency = delay
            best_group = group

    if not best_group:
        print("All latency tests failed", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"\n🏆 Fastest non‑HK group: {best_group} ({best_latency} ms)")
    else:
        # Output only the group name for scripting
        print(best_group)

    sys.exit(0)

if __name__ == "__main__":
    main()