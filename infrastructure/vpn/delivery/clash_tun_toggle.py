#!/usr/bin/env python3
"""
Clash Verge TUN Mode Toggle

Toggles TUN (VPN) mode on/off via Clash Verge Unix socket API.
TUN mode is more fundamental than system proxy and ensures all traffic (including
API calls to geo‑blocked services like Claude) is routed through the proxy.

Usage:
    python3 clash_tun_toggle.py [--on | --off | --toggle] [--dry-run]

Options:
    --on         Enable TUN mode
    --off        Disable TUN mode
    --toggle     Toggle current state (default)
    --dry-run    Only show current state, don't change
    --status     Show current TUN state (same as --dry-run)

Example:
    python3 clash_tun_toggle.py --toggle   # flip TUN enable
    python3 clash_tun_toggle.py --on       # ensure TUN is on
    python3 clash_tun_toggle.py --off      # ensure TUN is off
"""

import json
import subprocess
import sys
import argparse

SOCKET_PATH = "/tmp/verge/verge-mihomo.sock"
SECRET = "set-your-secret"
BASE_URL = "http://localhost"

def curl_unix(path, method="GET", data=None):
    """Make HTTP request to Unix socket."""
    url = f"{BASE_URL}{path}"
    cmd = ["curl", "-s", "--unix-socket", SOCKET_PATH,
           "-H", f"Authorization: Bearer {SECRET}"]
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

def get_config():
    """GET /configs and return parsed JSON."""
    resp = curl_unix("/configs")
    if not resp:
        return None
    try:
        return json.loads(resp)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return None

def patch_config(payload):
    """PATCH /configs with given JSON payload."""
    data = json.dumps(payload)
    resp = curl_unix("/configs", method="PATCH", data=data)
    if resp is None:
        return False
    # Empty response is okay for PATCH
    return True

def get_tun_state(config=None):
    if config is None:
        config = get_config()
        if config is None:
            return None
    return config.get("tun", {}).get("enable", False)

def set_tun_state(enable, dry_run=False):
    """Set TUN enable to True/False."""
    current = get_tun_state()
    if current is None:
        print("❌ Cannot read current TUN state.")
        return False
    if current == enable:
        print(f"ℹ️  TUN is already {'enabled' if enable else 'disabled'}.")
        return True
    if dry_run:
        print(f"🚀 Dry‑run: would set TUN enable to {enable}")
        return True
    payload = {"tun": {"enable": enable}}
    success = patch_config(payload)
    if success:
        # Verify
        new_state = get_tun_state()
        if new_state == enable:
            print(f"✅ TUN {'enabled' if enable else 'disabled'} successfully.")
            return True
        else:
            print(f"⚠️  TUN state reported as {new_state} after change.")
            return False
    else:
        print("❌ Failed to update TUN config.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Toggle Clash Verge TUN mode")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--on", action="store_true", help="Enable TUN mode")
    group.add_argument("--off", action="store_true", help="Disable TUN mode")
    group.add_argument("--toggle", action="store_true", help="Toggle TUN mode (default)")
    group.add_argument("--status", action="store_true", help="Show current TUN state")
    parser.add_argument("--dry-run", action="store_true", help="Do not actually change config")
    args = parser.parse_args()

    # Default action is toggle
    if not (args.on or args.off or args.toggle or args.status):
        args.toggle = True

    # Check socket
    import os
    if not os.path.exists(SOCKET_PATH):
        print(f"❌ Unix socket not found at {SOCKET_PATH}")
        print("   Ensure Clash Verge is running.")
        sys.exit(1)

    # Get current state
    config = get_config()
    if config is None:
        print("❌ Failed to retrieve config.")
        sys.exit(1)
    current = get_tun_state(config)
    if current is None:
        print("❌ Could not determine TUN state.")
        sys.exit(1)
    print(f"📡 Current TUN mode: {'ENABLED' if current else 'DISABLED'}")

    if args.status or args.dry_run:
        # Already printed status
        if args.dry_run and not args.status:
            # Determine target
            if args.on:
                set_tun_state(True, dry_run=True)
            elif args.off:
                set_tun_state(False, dry_run=True)
            elif args.toggle:
                set_tun_state(not current, dry_run=True)
        sys.exit(0)

    # Determine target state
    if args.on:
        target = True
    elif args.off:
        target = False
    else:  # toggle
        target = not current

    # Apply
    success = set_tun_state(target, dry_run=args.dry_run)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()