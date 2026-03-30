#!/usr/bin/env python3
"""
Test Mihomo control functions.

Steps:
1. Switching off and on (proxy selector)
2. Test speed for proxies and return the fastest non‑HK one
3. Switch to the selected proxy via TUN mode for all traffic
4. Confirm the IP address get updated (non‑HK)

Run: python3 test_mihomoctl.py [--verbose] [--no-switch]
"""

import sys, os, subprocess, json, time, argparse, logging
from typing import Optional, Tuple, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MIHOMOCTL = os.path.join(SCRIPT_DIR, "mihomoctl.py")
FASTEST_NON_HK = os.path.join(SCRIPT_DIR, "clash_fastest_non_hk.py")

def run_cmd(cmd, capture=True, timeout=30):
    """Run command, return (stdout, stderr, returncode)."""
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
        use_shell = False  # list commands are safer without shell
    else:
        cmd_str = cmd
        use_shell = True   # string commands may contain pipes, redirects
    logging.debug(f"Running: {cmd_str}")
    try:
        if capture:
            result = subprocess.run(cmd, shell=use_shell, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        else:
            result = subprocess.run(cmd, shell=use_shell, timeout=timeout)
            return "", "", result.returncode
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout: {cmd_str}")
        return "", "timeout", -1
    except Exception as e:
        logging.error(f"Exception: {e}")
        return "", str(e), -1

def mihomoctl_cmd(subcmd: str, *args):
    """Run mihomoctl command."""
    cmd = ["python3", MIHOMOCTL, subcmd] + list(args)
    stdout, stderr, rc = run_cmd(cmd)
    if rc != 0:
        logging.warning(f"mihomoctl {subcmd} failed: {stderr}")
    return stdout, stderr, rc

def get_status():
    """Get current selector status."""
    stdout, _, rc = mihomoctl_cmd("status")
    if rc == 0:
        return stdout
    return None

def switch_selector(group: str, target: str):
    """Switch a selector group to target."""
    stdout, stderr, rc = mihomoctl_cmd("switch", group, target)
    success = rc == 0
    if not success:
        logging.warning(f"switch failed: rc={rc}, stdout={stdout}, stderr={stderr}")
    return success, stdout

def get_current_ip(use_proxy=False):
    """Get current public IP (direct or via proxy)."""
    proxy_opt = "-x http://127.0.0.1:7890" if use_proxy else ""
    cmd = f"curl -s {proxy_opt} --connect-timeout 5 http://httpbin.org/ip"
    stdout, stderr, rc = run_cmd(cmd)
    if rc != 0 or not stdout:
        return None
    try:
        data = json.loads(stdout)
        return data.get("origin")
    except:
        return None

def get_ip_country(ip: str):
    """Get country code for IP via ipinfo.io."""
    if not ip:
        return None
    cmd = f"curl -s --connect-timeout 5 https://ipinfo.io/{ip}/country"
    stdout, stderr, rc = run_cmd(cmd)
    if rc == 0:
        return stdout.strip()
    return None

def get_global_now():
    """Get current GLOBAL selector value."""
    stdout, _, rc = mihomoctl_cmd("status")
    if rc != 0:
        return None
    # Parse line like "🔀 GLOBAL: 🌏 当前选择"
    for line in stdout.split('\n'):
        if line.startswith('🔀 GLOBAL:'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                return parts[1].strip()
    return None

def test_switching_on_off():
    """Step 1: Switch GLOBAL to DIRECT (off) then back to a non‑HK group (on)."""
    logging.info("Step 1: Switching off and on")
    # Choose the country selector (🌏 当前选择) as "on" target
    on_target = "🌏 当前选择"
    
    # Switch off
    ok, msg = switch_selector("GLOBAL", "DIRECT")
    if not ok:
        logging.error(f"Failed to switch off: {msg}")
        return False
    logging.info("Switched GLOBAL → DIRECT")
    time.sleep(2)
    # Verify GLOBAL is DIRECT
    current = get_global_now()
    if current != "DIRECT":
        logging.warning(f"GLOBAL is {current}, expected DIRECT")
    ip_direct = get_current_ip(use_proxy=False)
    logging.info(f"Direct IP: {ip_direct}")
    
    # Switch on
    ok, msg = switch_selector("GLOBAL", on_target)
    if not ok:
        logging.error(f"Failed to switch on: {msg}")
        return False
    logging.info(f"Switched GLOBAL → {on_target}")
    time.sleep(2)
    current = get_global_now()
    if current != on_target:
        logging.warning(f"GLOBAL is {current}, expected {on_target}")
    ip_proxy = get_current_ip(use_proxy=True)
    logging.info(f"Proxy IP: {ip_proxy}")
    
    # Verify proxy IP is different from direct IP
    if ip_direct == ip_proxy:
        logging.warning("Proxy IP equals direct IP (proxy may not be working)")
        return False
    else:
        logging.info("Proxy IP changed (good)")
    return True

def test_fastest_non_hk(verbose=False):
    """Step 2: Find fastest non‑HK group."""
    logging.info("Step 2: Testing fastest non‑HK group")
    # First, get just the group name (non‑verbose call)
    cmd = ["python3", FASTEST_NON_HK]
    stdout, stderr, rc = run_cmd(cmd)
    logging.debug(f"fastest non-HK stdout={repr(stdout)} stderr={repr(stderr)} rc={rc}")
    if rc != 0:
        logging.error(f"fastest‑non‑hk failed: {stderr}")
        return None
    group = stdout.strip()
    # If verbose flag, also run with --verbose for detailed logging
    if verbose:
        cmd_verbose = ["python3", FASTEST_NON_HK, "--verbose"]
        stdout_verbose, stderr_verbose, rc_verbose = run_cmd(cmd_verbose)
        if rc_verbose == 0:
            logging.debug(f"Verbose output:\n{stdout_verbose}")
    logging.info(f"Fastest non‑HK group: {group}")
    return group

def test_switch_to_fastest(group):
    """Step 3: Switch country selector (🌏 当前选择) to fastest group."""
    logging.info(f"Step 3: Switching country selector to fastest group ({group})")
    ok, msg = switch_selector("🌏 当前选择", group)
    if not ok:
        logging.error(f"Switch to fastest failed: {msg}")
        return False
    logging.info(f"Switched 🌏 当前选择 → {group}")
    time.sleep(2)
    return True

def test_tun_mode():
    """Check if TUN mode is active (requires root daemon)."""
    logging.info("Checking TUN mode...")
    # Look for utun interface with mihomo routing
    stdout, stderr, rc = run_cmd("ifconfig | grep -c '^utun'")
    if rc == 0 and int(stdout) > 0:
        logging.info(f"Found {stdout} utun interfaces.")
        # Check routing table
        stdout2, _, _ = run_cmd("netstat -rn | grep -c utun")
        if int(stdout2) > 0:
            logging.info("TUN appears active in routing table.")
            return True
    logging.warning("TUN mode not active (or not running as root).")
    return False

def test_ip_non_hk():
    """Step 4: Confirm IP is non‑HK."""
    logging.info("Step 4: Verifying non‑HK IP")
    ip = get_current_ip(use_proxy=True)
    if not ip:
        logging.error("Could not fetch IP via proxy")
        return False
    country = get_ip_country(ip)
    logging.info(f"IP: {ip}, Country: {country}")
    if country and country != "HK":
        logging.info(f"✅ SUCCESS: IP is non‑HK ({country})")
        return True
    else:
        logging.warning(f"⚠️  IP may be HK ({country})")
        return False

def test_latency(group, limit=5):
    """Test latency of proxies in group."""
    logging.info(f"Step 5: Latency test for {group}")
    stdout, stderr, rc = mihomoctl_cmd("latency", "--group", group, "--limit", str(limit))
    if rc == 0:
        logging.info(f"Latency results:\n{stdout}")
        return True
    else:
        logging.warning(f"Latency test failed: {stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Mihomo control functions")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-switch", action="store_true", help="Skip switching steps (dry‑run)")
    parser.add_argument("--log", default="/tmp/mihomo_test.log", help="Log file path")
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(args.log),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=== Mihomo Control Test Start ===")
    
    # Ensure mihomo is running
    status = get_status()
    if status is None:
        logging.error("Mihomo not reachable. Starting...")
        stdout, stderr, rc = mihomoctl_cmd("start")
        if rc != 0:
            logging.error("Failed to start mihomo")
            sys.exit(1)
        time.sleep(3)
    
    results = {}
    
    # Step 1
    if not args.no_switch:
        results["switch_on_off"] = test_switching_on_off()
    else:
        logging.info("Skipping switch on/off (--no-switch)")
        results["switch_on_off"] = None
    
    # Step 2
    fastest_group = test_fastest_non_hk(verbose=args.verbose)
    results["fastest_group"] = fastest_group
    
    # Step 3
    if fastest_group and not args.no_switch:
        results["switch_to_fastest"] = test_switch_to_fastest(fastest_group)
    else:
        results["switch_to_fastest"] = None
    
    # Step 4
    results["ip_non_hk"] = test_ip_non_hk()
    
    # Step 5 (optional latency)
    if fastest_group:
        results["latency"] = test_latency(fastest_group, limit=5)
    
    # TUN mode check
    results["tun_active"] = test_tun_mode()
    
    # Summary
    logging.info("=== Test Summary ===")
    for k, v in results.items():
        if v is None:
            logging.info(f"{k}: skipped")
        elif isinstance(v, bool):
            logging.info(f"{k}: {'PASS' if v else 'FAIL'}")
        else:
            logging.info(f"{k}: {v}")
    
    # Determine overall success
    failures = [k for k, v in results.items() if isinstance(v, bool) and not v]
    if failures:
        logging.error(f"❌ Tests failed: {failures}")
        sys.exit(1)
    else:
        logging.info("✅ All tests passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()