#!/usr/bin/env python3
"""
Setup mihomo (Clash Meta) with a remote subscription URL.

Generates config.yaml at ~/.config/mihomo/config.yaml with:
- Remote subscription content (proxies, proxy-groups, rules)
- Local overrides: TUN mode, external controller, secret, ports
- Option to start/stop mihomo service
"""

import os, sys, yaml, subprocess, json, time, shutil, tempfile, hashlib

REMOTE_URL = "https://api.jetcamoe.com/api/v1/public/services/54066/0ff587d3efb4537fa73df5f646133051?agent=clash-hysteria"
CONFIG_PATH = os.path.expanduser("~/.config/mihomo/config.yaml")
MIHOMO_BIN = shutil.which("mihomo") or "/opt/homebrew/bin/mihomo"

LOCAL_OVERRIDES = {
    "mixed-port": 7895,               # avoid conflict with Clash Verge (7897)
    "socks-port": 7896,
    "redir-port": 7894,
    "allow-lan": False,
    "mode": "rule",
    "log-level": "info",
    "ipv6": False,
    "external-controller": "127.0.0.1:9095",
    "external-controller-unix": "",   # disable unix socket (or set your own)
    "secret": "set-your-secret",      # same as Clash Verge for compatibility
    "tun": {
        "enable": True,
        "stack": "gvisor",
        "auto-route": True,
        "auto-detect-interface": True,
        "strict-route": False,
        "dns-hijack": ["any:53"],
    }
}

def fetch_remote_config():
    """Download remote config as YAML."""
    import requests
    try:
        resp = requests.get(REMOTE_URL, timeout=30)
        resp.raise_for_status()
        return yaml.safe_load(resp.content)
    except ImportError:
        # fallback to curl
        import subprocess
        curl = ["curl", "-s", "-L", REMOTE_URL]
        result = subprocess.run(curl, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to fetch remote config: {result.stderr}")
            sys.exit(1)
        return yaml.safe_load(result.stdout)
    except Exception as e:
        print(f"❌ Failed to fetch remote config: {e}")
        sys.exit(1)

def merge_configs(remote, local):
    """Merge remote config with local overrides (deep merge)."""
    # Start with remote config
    merged = remote.copy()
    
    # Override top-level keys
    for key, value in local.items():
        if key == "tun" and isinstance(value, dict) and isinstance(merged.get(key), dict):
            # Deep merge tun dict
            merged.setdefault(key, {}).update(value)
        elif key == "dns" and isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged.setdefault(key, {}).update(value)
        else:
            merged[key] = value
    return merged

def write_config(merged):
    """Write merged YAML to config path."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(merged, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=float("inf"))
    print(f"✅ Config written to {CONFIG_PATH}")

def validate_config():
    """Validate config with mihomo -t (test)."""
    if not os.path.exists(MIHOMO_BIN):
        print(f"⚠️  mihomo binary not found at {MIHOMO_BIN}")
        return False
    result = subprocess.run([MIHOMO_BIN, "-d", os.path.dirname(CONFIG_PATH), "-f", CONFIG_PATH, "-t"],
                           capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Config validation passed.")
        return True
    else:
        print(f"❌ Config validation failed:\n{result.stderr}")
        return False

def start_mihomo():
    """Start mihomo as a background daemon."""
    if is_running():
        print("⚠️  mihomo already running.")
        return True
    print("🚀 Starting mihomo...")
    # Use nohup or launchd? For now simple background.
    cmd = [MIHOMO_BIN, "-d", os.path.dirname(CONFIG_PATH), "-f", CONFIG_PATH]
    try:
        # Start detached
        import subprocess
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        time.sleep(2)
        if proc.poll() is None:
            print("✅ mihomo started (PID: {})".format(proc.pid))
            # Write PID file
            pid_path = os.path.expanduser("~/.config/mihomo/mihomo.pid")
            with open(pid_path, "w") as f:
                f.write(str(proc.pid))
            return True
        else:
            print("❌ mihomo exited immediately.")
            return False
    except Exception as e:
        print(f"❌ Failed to start mihomo: {e}")
        return False

def stop_clash_verge():
    """Quit Clash Verge GUI and kill its core."""
    print("🛑 Stopping Clash Verge...")
    # Quit via AppleScript
    subprocess.run(["osascript", "-e", 'tell application "Clash Verge" to quit'], 
                   capture_output=True, timeout=5)
    time.sleep(2)
    # Kill core process (requires sudo)
    subprocess.run(["sudo", "pkill", "-f", "verge-mihomo"], 
                   capture_output=True, timeout=5)
    time.sleep(1)
    print("✅ Clash Verge stopped.")

def stop_mihomo():
    """Stop running mihomo process."""
    pid_path = os.path.expanduser("~/.config/mihomo/mihomo.pid")
    if os.path.exists(pid_path):
        with open(pid_path, "r") as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 15)  # SIGTERM
            time.sleep(1)
            os.remove(pid_path)
            print(f"✅ Stopped mihomo (PID: {pid})")
            return True
        except ProcessLookupError:
            print(f"⚠️  Process {pid} not found.")
            os.remove(pid_path)
            return True
        except Exception as e:
            print(f"❌ Failed to stop mihomo: {e}")
            return False
    else:
        # fallback to pkill
        result = subprocess.run(["pkill", "-f", "mihomo"], capture_output=True)
        if result.returncode == 0:
            print("✅ Stopped mihomo via pkill.")
            return True
        else:
            print("⚠️  No mihomo process found.")
            return True

def is_running():
    """Check if mihomo is already running (by port)."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", 9095))
        sock.close()
        return True
    except ConnectionRefusedError:
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manage mihomo with remote subscription")
    parser.add_argument("action", choices=["setup", "start", "stop", "restart", "status", "validate"],
                       help="Action to perform")
    args = parser.parse_args()
    
    if args.action == "setup":
        print("📥 Fetching remote config...")
        remote = fetch_remote_config()
        print("🔄 Merging with local overrides...")
        merged = merge_configs(remote, LOCAL_OVERRIDES)
        write_config(merged)
        validate_config()
        print("\n🎉 Setup complete.")
        print("   You can start mihomo with: python3 mihomo_setup.py start")
        
    elif args.action == "start":
        if not os.path.exists(CONFIG_PATH):
            print("❌ Config not found. Run 'setup' first.")
            sys.exit(1)
        if validate_config():
            stop_clash_verge()
            start_mihomo()
            # Wait a bit and check status
            time.sleep(3)
            if is_running():
                print("✅ mihomo is running. External controller: 127.0.0.1:9095")
                print("   Use secret: set-your-secret")
            else:
                print("❌ mihomo failed to start.")
        else:
            sys.exit(1)
            
    elif args.action == "stop":
        stop_mihomo()
        
    elif args.action == "restart":
        stop_mihomo()
        time.sleep(2)
        start_mihomo()
        
    elif args.action == "status":
        if is_running():
            print("✅ mihomo is running (port 9095).")
        else:
            print("❌ mihomo is not running.")
            
    elif args.action == "validate":
        if os.path.exists(CONFIG_PATH):
            validate_config()
        else:
            print("❌ Config not found.")

if __name__ == "__main__":
    main()