#!/usr/bin/env python3
"""
Mihomo CLI control tool.

Commands:
  status              Show current selector and proxy status
  list-groups         List available proxy groups (country selectors)
  list-proxies        List individual proxies in a group
  switch <group>      Switch global selector to given group (e.g., '🇺🇸 美国自动')
  fastest-non-hk      Find fastest non‑HK proxy group and switch to it
  latency             Test latency of proxies in a group
  set-proxy           Configure system proxy (macOS networksetup) to mihomo's mixed‑port
  unset-proxy         Disable system proxy
  start               Start mihomo via launchctl
  stop                Stop mihomo via launchctl
  restart             Restart service
"""

import sys, os, json, subprocess, time, argparse, urllib.parse, yaml, requests

MIHOMO_API = "http://127.0.0.1:9095"
SECRET = "set-your-secret"  # must match config.yaml
CONFIG_PATH = os.path.expanduser("~/.config/mihomo/config.yaml")
LAUNCH_AGENT = "com.user.mihomo"

# --------------------------------------------------------------------------
# API helpers
# --------------------------------------------------------------------------

def api_request(method, endpoint, data=None):
    url = f"{MIHOMO_API}{endpoint}"
    headers = {"Authorization": f"Bearer {SECRET}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, data=json.dumps(data), timeout=10)
        else:
            raise ValueError(f"Unsupported method {method}")
        if resp.status_code == 204:
            return True, {}
        if resp.status_code == 200:
            return True, resp.json()
        return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)

def get_proxies():
    ok, res = api_request("GET", "/proxies")
    if not ok:
        return {}
    return res.get("proxies", {})

def get_group(name):
    ok, res = api_request("GET", f"/proxies/{urllib.parse.quote(name)}")
    if not ok:
        return {}
    return res

def switch_group(group_name, target_proxy):
    """Switch a selector group to a specific proxy."""
    ok, res = api_request("PUT", f"/proxies/{urllib.parse.quote(group_name)}", {"name": target_proxy})
    return ok, res

def test_latency(proxy_name, timeout=5000):
    """Test latency of a single proxy."""
    ok, res = api_request("GET", f"/proxies/{urllib.parse.quote(proxy_name)}/delay?timeout={timeout}&url=https://cp.cloudflare.com/generate_204")
    if not ok:
        return None
    return res.get("delay")

# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_status(args):
    """Show current selector and proxy status."""
    proxies = get_proxies()
    if not proxies:
        print("❌ Cannot reach mihomo API. Is it running?")
        return 1
    # Find selector groups
    for name, info in proxies.items():
        if info.get("type") == "Selector":
            now = info.get("now")
            print(f"🔀 {name}: {now}")
            # Show latency of the current selection if it's a proxy
            if now and now in proxies and proxies[now].get("type") == "Fallback":
                # fallback group, show its current proxy
                sub_now = proxies[now].get("now")
                if sub_now:
                    delay = test_latency(sub_now)
                    print(f"   └─ {now} → {sub_now}" + (f" ({delay} ms)" if delay else ""))
    # Show global selector
    if "GLOBAL" in proxies:
        print(f"🌍 GLOBAL: {proxies['GLOBAL'].get('now')}")
    # Show IP info
    try:
        import subprocess
        ip_out = subprocess.run(["curl", "-s", "-x", "http://127.0.0.1:7895", "http://httpbin.org/ip"], capture_output=True, text=True)
        if ip_out.returncode == 0:
            ip_data = json.loads(ip_out.stdout)
            ip = ip_data.get("origin", "").split(",")[0]
            country_out = subprocess.run(["curl", "-s", "-x", "http://127.0.0.1:7895", "https://ipinfo.io/country"], capture_output=True, text=True)
            country = country_out.stdout.strip() if country_out.returncode == 0 else "unknown"
            print(f"📍 Proxy IP: {ip} ({country})")
    except:
        pass
    return 0

def cmd_list_groups(args):
    proxies = get_proxies()
    for name, info in proxies.items():
        if info.get("type") in ("Selector", "Fallback"):
            now = info.get("now")
            print(f"{name} ({info['type']}) → {now}")
    return 0

def cmd_list_proxies(args):
    if not args.group:
        print("❌ Specify a group name.")
        return 1
    group = get_group(args.group)
    if not group:
        print(f"❌ Group '{args.group}' not found.")
        return 1
    proxies = group.get("all", [])
    print(f"Proxies in '{args.group}':")
    for p in proxies:
        delay = test_latency(p)
        print(f"  {p}" + (f" ({delay} ms)" if delay else " (failed)"))
    return 0

def cmd_switch(args):
    if not args.group or not args.target:
        print("❌ Usage: mihomoctl switch <group> <target>")
        return 1
    ok, msg = switch_group(args.group, args.target)
    if ok:
        print(f"✅ Switched {args.group} → {args.target}")
    else:
        print(f"❌ Failed: {msg}")
    return 0 if ok else 1

def cmd_fastest_non_hk(args):
    """Find fastest non‑HK proxy group and switch to it."""
    proxies = get_proxies()
    # Identify country groups (🇺🇸 美国自动, 🇯🇵 日本自动, 🇸🇬 新加坡自动, 🇨🇳 台湾自动)
    # Exclude 🇭🇰 香港自动
    candidate_groups = []
    for name, info in proxies.items():
        if info.get("type") == "Fallback" and "香港" not in name and "HK" not in name:
            candidate_groups.append(name)
    if not candidate_groups:
        print("❌ No non‑HK country groups found.")
        return 1
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
        print(f"  {group}: {delay} ms")
        if delay < best_latency:
            best_latency = delay
            best_group = group
    if not best_group:
        print("❌ All latency tests failed.")
        return 1
    print(f"🏆 Fastest non‑HK group: {best_group} ({best_latency} ms)")
    # Switch global selector to this group
    ok, msg = switch_group("🌏 当前选择", best_group)
    if ok:
        print(f"✅ Switched 🌏 当前选择 → {best_group}")
    else:
        print(f"❌ Switch failed: {msg}")
        return 1
    return 0

def cmd_latency(args):
    group_name = args.group or "🌏 当前选择"
    group = get_group(group_name)
    if not group:
        print(f"❌ Group '{group_name}' not found.")
        return 1
    proxies = group.get("all", [])
    for p in proxies[:args.limit]:
        delay = test_latency(p)
        if delay is None:
            print(f"  {p}: failed")
        else:
            print(f"  {p}: {delay} ms")
    return 0

def cmd_set_proxy(args):
    """Configure macOS system proxy to mihomo's mixed‑port."""
    # Determine network service
    out = subprocess.run(["networksetup", "-listallnetworkservices"], capture_output=True, text=True)
    services = [s.strip() for s in out.stdout.split('\n') if s and not s.startswith('*')]
    if not services:
        print("❌ No network services found.")
        return 1
    service = services[0]  # usually Ethernet or Wi‑Fi
    print(f"📶 Using network service: {service}")
    # Set proxy (ports from config: mixed-port 7890, socks-port 7891)
    subprocess.run(["networksetup", "-setwebproxy", service, "127.0.0.1", "7890"])
    subprocess.run(["networksetup", "-setsecurewebproxy", service, "127.0.0.1", "7890"])
    subprocess.run(["networksetup", "-setsocksfirewallproxy", service, "127.0.0.1", "7891"])
    subprocess.run(["networksetup", "-setwebproxystate", service, "on"])
    subprocess.run(["networksetup", "-setsecurewebproxystate", service, "on"])
    subprocess.run(["networksetup", "-setsocksfirewallproxystate", service, "on"])
    print("✅ System proxy configured.")
    print("   Note: Some apps may not respect system proxy; set env vars:")
    print("     export http_proxy=http://127.0.0.1:7890")
    print("     export https_proxy=http://127.0.0.1:7890")
    print("     export all_proxy=socks5://127.0.0.1:7891")
    return 0

def cmd_unset_proxy(args):
    out = subprocess.run(["networksetup", "-listallnetworkservices"], capture_output=True, text=True)
    services = [s.strip() for s in out.stdout.split('\n') if s and not s.startswith('*')]
    for service in services:
        subprocess.run(["networksetup", "-setwebproxystate", service, "off"])
        subprocess.run(["networksetup", "-setsecurewebproxystate", service, "off"])
        subprocess.run(["networksetup", "-setsocksfirewallproxystate", service, "off"])
    print("✅ System proxy disabled.")
    return 0

def cmd_start(args):
    subprocess.run(["launchctl", "load", os.path.expanduser(f"~/Library/LaunchAgents/{LAUNCH_AGENT}.plist")])
    print("✅ Started mihomo (launchctl).")
    return 0

def cmd_stop(args):
    subprocess.run(["launchctl", "unload", os.path.expanduser(f"~/Library/LaunchAgents/{LAUNCH_AGENT}.plist")])
    print("✅ Stopped mihomo.")
    return 0

def cmd_restart(args):
    cmd_stop(None)
    time.sleep(2)
    cmd_start(None)
    return 0

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Mihomo CLI control tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # status
    subparsers.add_parser("status", help="Show current selector and proxy status")
    
    # list-groups
    subparsers.add_parser("list-groups", help="List available proxy groups")
    
    # list-proxies
    p_list = subparsers.add_parser("list-proxies", help="List proxies in a group")
    p_list.add_argument("group", help="Group name")
    
    # switch
    p_switch = subparsers.add_parser("switch", help="Switch a group to a target proxy")
    p_switch.add_argument("group", help="Group name")
    p_switch.add_argument("target", help="Target proxy name")
    
    # fastest-non-hk
    subparsers.add_parser("fastest-non-hk", help="Find fastest non‑HK proxy group and switch")
    
    # latency
    p_lat = subparsers.add_parser("latency", help="Test latency of proxies in a group")
    p_lat.add_argument("--group", help="Group name (default: 🌏 当前选择)")
    p_lat.add_argument("--limit", type=int, default=20, help="Max proxies to test")
    
    # set-proxy
    subparsers.add_parser("set-proxy", help="Configure system proxy to mihomo")
    
    # unset-proxy
    subparsers.add_parser("unset-proxy", help="Disable system proxy")
    
    # start / stop / restart
    subparsers.add_parser("start", help="Start mihomo via launchctl")
    subparsers.add_parser("stop", help="Stop mihomo via launchctl")
    subparsers.add_parser("restart", help="Restart mihomo")
    
    args = parser.parse_args()
    
    # Map command to function
    cmd_map = {
        "status": cmd_status,
        "list-groups": cmd_list_groups,
        "list-proxies": cmd_list_proxies,
        "switch": cmd_switch,
        "fastest-non-hk": cmd_fastest_non_hk,
        "latency": cmd_latency,
        "set-proxy": cmd_set_proxy,
        "unset-proxy": cmd_unset_proxy,
        "start": cmd_start,
        "stop": cmd_stop,
        "restart": cmd_restart,
    }
    func = cmd_map[args.command]
    return func(args)

if __name__ == "__main__":
    sys.exit(main())