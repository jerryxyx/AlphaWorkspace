#!/usr/bin/env python3
"""
Simple IP region check.

Returns JSON with direct and proxy IP/country.
Usage: python3 ip_region_check.py [--proxy-only] [--direct-only]
"""

import sys, json, subprocess, argparse

PROXY = 'http://127.0.0.1:7897'

def curl_with_proxy(use_proxy):
    """Return (ip, country) using ipinfo.io."""
    proxy_opt = f'-x {PROXY}' if use_proxy else ''
    # IP
    cmd = f'curl -s {proxy_opt} --connect-timeout 5 http://httpbin.org/ip'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    ip = None
    if result.returncode == 0 and result.stdout:
        try:
            data = json.loads(result.stdout)
            ip = data.get('origin', '').split(',')[0].strip()
        except:
            ip = None
    # Country
    cmd = f'curl -s {proxy_opt} --connect-timeout 5 https://ipinfo.io/country'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    country = result.stdout.strip() if result.returncode == 0 else None
    return ip, country

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy-only', action='store_true', help='Only check via proxy')
    parser.add_argument('--direct-only', action='store_true', help='Only check direct')
    args = parser.parse_args()
    
    out = {}
    if not args.proxy_only:
        ip_direct, country_direct = curl_with_proxy(False)
        out['direct'] = {'ip': ip_direct, 'country': country_direct}
    if not args.direct_only:
        ip_proxy, country_proxy = curl_with_proxy(True)
        out['proxy'] = {'ip': ip_proxy, 'country': country_proxy}
    
    print(json.dumps(out, indent=2))
    sys.exit(0)

if __name__ == '__main__':
    main()