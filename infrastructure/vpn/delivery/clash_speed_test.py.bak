#!/usr/bin/env python3
import json
import subprocess
import sys
import time

SOCKET_PATH = "/tmp/verge/verge-mihomo.sock"
SECRET = "set-your-secret"
BASE_URL = "http://localhost"

def curl_unix(path, params=None):
    """Make HTTP request to Unix socket."""
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    cmd = [
        "curl", "-s", "--unix-socket", SOCKET_PATH,
        "-H", f"Authorization: Bearer {SECRET}",
        url
    ]
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
    resp = curl_unix("/proxies")
    if not resp:
        return None
    data = json.loads(resp)
    return data.get("proxies", {})

def test_proxy(name):
    """Test latency for a single proxy."""
    resp = curl_unix(f"/proxies/{name}/delay", {"timeout": "5000", "url": "https://cp.cloudflare.com/generate_204"})
    if not resp:
        return None
    try:
        data = json.loads(resp)
        return data.get("delay")
    except:
        return None

def main():
    proxies = get_proxies()
    if not proxies:
        print("Failed to fetch proxies")
        sys.exit(1)
    
    # Identify groups (Selector, Fallback, URLTest, LoadBalance)
    groups = []
    for name, info in proxies.items():
        if "all" in info:  # It's a group
            groups.append((name, info))
    
    print(f"Found {len(groups)} groups")
    print("\nTesting 'now' proxy for each group:")
    results = []
    for name, info in groups:
        group_type = info.get("type", "unknown")
        now = info.get("now")
        if not now:
            continue
        print(f"  {name} ({group_type}) → {now} ... ", end="", flush=True)
        delay = test_proxy(now)
        if delay is None:
            print("failed")
        else:
            print(f"{delay} ms")
            results.append((name, group_type, now, delay))
        time.sleep(0.5)  # be nice
    
    print("\n--- Results ---")
    for name, typ, now, delay in sorted(results, key=lambda x: x[3] if x[3] is not None else 9999):
        print(f"{name:20} {typ:12} {now:30} {delay if delay else 'fail':>6} ms")
    
    # Also test a few individual proxies from each region
    print("\n--- Testing top proxies per region ---")
    region_groups = ["🇭🇰 香港自动", "🇨🇳 台湾自动", "🇸🇬 新加坡自动", "🇯🇵 日本自动", "🇺🇸 美国自动"]
    for rg in region_groups:
        if rg not in proxies:
            continue
        all_proxies = proxies[rg].get("all", [])
        # test first 3 proxies in each region
        for proxy in all_proxies[:3]:
            print(f"  {proxy} ... ", end="", flush=True)
            delay = test_proxy(proxy)
            if delay is None:
                print("failed")
            else:
                print(f"{delay} ms")
            time.sleep(0.3)

if __name__ == "__main__":
    main()