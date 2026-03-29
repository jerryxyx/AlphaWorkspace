#!/usr/bin/env python3
"""
Test script to toggle TUN mode via Clash Verge Unix socket API.
"""

import json
import subprocess
import sys

SOCKET_PATH = "/tmp/verge/verge-mihomo.sock"
SECRET = "set-your-secret"
BASE_URL = "http://localhost"

def curl_unix(path, method="GET", data=None):
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
        print("PATCH failed")
        return False
    try:
        result = json.loads(resp)
        print(f"PATCH response: {result}")
        return True
    except:
        print(f"Response: {resp}")
        return True  # maybe still ok

def main():
    print("Current config:")
    config = get_config()
    if not config:
        sys.exit(1)
    tun_enabled = config.get("tun", {}).get("enable", False)
    print(f"TUN enabled: {tun_enabled}")
    
    # Toggle
    new_enabled = not tun_enabled
    print(f"\nToggling TUN enable to {new_enabled}")
    payload = {"tun": {"enable": new_enabled}}
    success = patch_config(payload)
    if success:
        print("Config updated. Verifying...")
        config2 = get_config()
        if config2:
            new_tun = config2.get("tun", {}).get("enable", False)
            print(f"TUN enabled after update: {new_tun}")
            if new_tun == new_enabled:
                print("✅ Successfully toggled TUN mode.")
            else:
                print("❌ TUN state did not change.")
        else:
            print("⚠️ Could not verify")
    else:
        print("❌ Failed to update config")
        sys.exit(1)

if __name__ == "__main__":
    main()