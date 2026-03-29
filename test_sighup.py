#!/usr/bin/env python3
import os, sys, yaml, subprocess, json, signal, time

CONFIG_PATH = os.path.expanduser('~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/config.yaml')
SOCKET_PATH = '/tmp/verge/verge-mihomo.sock'
SECRET = 'set-your-secret'

def get_pid():
    out = subprocess.run(['pgrep', '-f', 'verge-mihomo'], capture_output=True, text=True)
    if out.returncode == 0:
        return int(out.stdout.strip().split('\n')[0])
    return None

def curl_unix(path, method='GET', data=None):
    url = f'http://localhost{path}'
    cmd = ['curl', '-s', '--unix-socket', SOCKET_PATH, '-H', f'Authorization: Bearer {SECRET}']
    if method != 'GET':
        cmd.extend(['-X', method])
    if data:
        cmd.extend(['-H', 'Content-Type: application/json', '-d', data])
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        print(f'Error: {result.stderr}', file=sys.stderr)
        return None
    return result.stdout

def get_api_tun():
    resp = curl_unix('/configs')
    if not resp:
        return None
    try:
        data = json.loads(resp)
        return data.get('tun', {}).get('enable', None)
    except:
        return None

def get_yaml_tun():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('tun', {}).get('enable', None)

def update_yaml_tun(enable):
    if not os.path.exists(CONFIG_PATH):
        print('Config file missing')
        return False
    with open(CONFIG_PATH, 'r') as f:
        data = yaml.safe_load(f)
    if 'tun' not in data:
        data['tun'] = {}
    data['tun']['enable'] = enable
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    return True

def send_sighup(pid):
    try:
        os.kill(pid, signal.SIGHUP)
        return True
    except Exception as e:
        print(f'Error sending SIGHUP: {e}')
        return False

print('=== Current state ===')
print(f'PID: {get_pid()}')
print(f'YAML tun.enable: {get_yaml_tun()}')
print(f'API tun.enable: {get_api_tun()}')

# Toggle YAML value
new_val = not get_yaml_tun()
print(f'\nUpdating YAML tun.enable to {new_val}')
if update_yaml_tun(new_val):
    print('YAML updated')
    pid = get_pid()
    if pid:
        print(f'Sending SIGHUP to {pid}')
        if send_sighup(pid):
            print('SIGHUP sent')
            time.sleep(2)
            print(f'API tun.enable after reload: {get_api_tun()}')
        else:
            print('Failed to send SIGHUP')
    else:
        print('No PID')
else:
    print('Failed to update YAML')