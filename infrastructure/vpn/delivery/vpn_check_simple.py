#!/usr/bin/env python3
"""
VPN/TUN Status Check

Checks:
- Direct IP geolocation (country)
- Proxy IP geolocation (via 127.0.0.1:7897)
- TUN interface existence (utun10)
- Clash Verge API tun.enable status
- YAML config tun.enable status
- Routing table entries for utun10
"""

import os, sys, json, subprocess, re, yaml, time

SOCKET_PATH = '/tmp/verge/verge-mihomo.sock'
SECRET = 'set-your-secret'
CONFIG_PATH = os.path.expanduser('~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/config.yaml')
PROXY = 'http://127.0.0.1:7897'

def run_cmd(cmd, timeout=10):
    """Run shell command, return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return '', 'timeout', -1
    except Exception as e:
        return '', str(e), -1

def get_ip_info(use_proxy=False):
    """Get IP and country via ipinfo.io."""
    proxy_opt = f'-x {PROXY}' if use_proxy else ''
    # Get IP
    cmd = f'curl -s {proxy_opt} --connect-timeout 5 http://httpbin.org/ip'
    ip_out, ip_err, ip_code = run_cmd(cmd)
    ip = None
    if ip_code == 0 and ip_out:
        try:
            data = json.loads(ip_out)
            ip = data.get('origin', '').split(',')[0].strip()
        except:
            ip = None
    
    # Get country
    cmd = f'curl -s {proxy_opt} --connect-timeout 5 https://ipinfo.io/country'
    country_out, country_err, country_code = run_cmd(cmd)
    country = country_out.strip() if country_code == 0 else None
    
    return ip, country

def get_tun_interface():
    """Check if utun10 exists."""
    out, err, code = run_cmd('ifconfig utun10 2>/dev/null')
    exists = code == 0 and 'utun10' in out
    return exists, out[:500] if exists else None

def get_routes():
    """Get routing table entries for utun10."""
    out, err, code = run_cmd('netstat -nr | grep -E "utun10|default" | head -20')
    return out

def get_api_tun():
    """Get tun.enable from Clash API."""
    if not os.path.exists(SOCKET_PATH):
        return None, 'socket_not_found'
    cmd = f'curl -s --unix-socket {SOCKET_PATH} -H "Authorization: Bearer {SECRET}" http://localhost/configs'
    out, err, code = run_cmd(cmd)
    if code != 0 or not out:
        return None, f'api_error:{err}'
    try:
        data = json.loads(out)
        enable = data.get('tun', {}).get('enable', None)
        device = data.get('tun', {}).get('device', '')
        return enable, device
    except:
        return None, 'parse_error'

def get_yaml_tun():
    """Get tun.enable from YAML config."""
    if not os.path.exists(CONFIG_PATH):
        return None, 'file_not_found'
    try:
        with open(CONFIG_PATH, 'r') as f:
            data = yaml.safe_load(f)
        enable = data.get('tun', {}).get('enable', None)
        return enable, 'ok'
    except Exception as e:
        return None, f'yaml_error:{e}'

def main():
    result = {
        'timestamp': time.time(),
        'direct': {},
        'proxy': {},
        'tun': {},
        'routes': '',
        'summary': ''
    }
    
    # Direct IP
    ip_direct, country_direct = get_ip_info(use_proxy=False)
    result['direct']['ip'] = ip_direct
    result['direct']['country'] = country_direct
    
    # Proxy IP
    ip_proxy, country_proxy = get_ip_info(use_proxy=True)
    result['proxy']['ip'] = ip_proxy
    result['proxy']['country'] = country_proxy
    
    # TUN interface
    tun_exists, tun_info = get_tun_interface()
    result['tun']['interface_exists'] = tun_exists
    result['tun']['interface_info'] = tun_info
    
    # Routes
    result['routes'] = get_routes()
    
    # API status
    api_enable, api_detail = get_api_tun()
    result['tun']['api_enable'] = api_enable
    result['tun']['api_detail'] = api_detail
    
    # YAML status
    yaml_enable, yaml_detail = get_yaml_tun()
    result['tun']['yaml_enable'] = yaml_enable
    result['tun']['yaml_detail'] = yaml_detail
    
    # Summary
    summary_parts = []
    if country_direct:
        summary_parts.append(f'Direct: {country_direct}')
    if country_proxy:
        summary_parts.append(f'Proxy: {country_proxy}')
    summary_parts.append(f'TUN interface: {tun_exists}')
    summary_parts.append(f'API enable: {api_enable}')
    summary_parts.append(f'YAML enable: {yaml_enable}')
    result['summary'] = ' | '.join(summary_parts)
    
    # Print JSON
    print(json.dumps(result, indent=2))
    
    # Exit code 0 if TUN appears working (interface exists and proxy country != direct country?)
    # We'll just return 0 always; interpretation is up to caller.
    sys.exit(0)

if __name__ == '__main__':
    main()