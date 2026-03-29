#!/usr/bin/env python3
import json, subprocess, os, sys, yaml

SOCKET_PATH = '/tmp/verge/verge-mihomo.sock'
SECRET = 'set-your-secret'
CONFIG_PATH = os.path.expanduser('~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/config.yaml')

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

# Read YAML file
with open(CONFIG_PATH, 'r') as f:
    yaml_content = f.read()

print(f'YAML length: {len(yaml_content)}')
print('First 200 chars:', yaml_content[:200])

# Build payload
payload = {
    'path': '',  # default config
    'payload': yaml_content
}
json_payload = json.dumps(payload)
print(f'Sending PUT /configs?force=true with payload length {len(json_payload)}')

resp = curl_unix('/configs?force=true', method='PUT', data=json_payload)
print('Response:', resp)

# Check if tun.enable changed after reload
resp2 = curl_unix('/configs')
if resp2:
    data = json.loads(resp2)
    print('New tun.enable:', data.get('tun', {}).get('enable'))