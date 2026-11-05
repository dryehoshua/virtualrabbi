#!/usr/bin/env python3
"""Install the isolated public reader; optionally start its authorized tunnel."""
import argparse
import os
from pathlib import Path
import plistlib
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
runtime = root / '.runtime'
parser = argparse.ArgumentParser()
parser.add_argument('--tunnel', action='store_true')
args = parser.parse_args()
agents = Path.home() / 'Library/LaunchAgents'
agents.mkdir(parents=True, exist_ok=True)
runtime.mkdir(exist_ok=True)

def install(label, arguments):
    destination = agents / (label + '.plist')
    with destination.open('wb') as output:
        plistlib.dump({'Label': label, 'ProgramArguments': arguments,
                      'WorkingDirectory': str(root), 'RunAtLoad': True,
                      'KeepAlive': True, 'ThrottleInterval': 10,
                      'StandardOutPath': str(runtime / (label + '.log')),
                      'StandardErrorPath': str(runtime / (label + '-error.log')),
                      'EnvironmentVariables': {'LANG': 'en_US.UTF-8'}}, output)
    domain = f'gui/{os.getuid()}'
    subprocess.run(['launchctl', 'bootout', domain + '/' + label], capture_output=True)
    subprocess.run(['launchctl', 'bootstrap', domain, str(destination)], check=True)
    print('Installed ' + label)

install('net.virtualrabbi.public', [sys.executable, '-u', str(root / 'public_server.py')])
if args.tunnel:
    token = runtime / 'deploy/tunnel-token'
    binary = runtime / 'bin/cloudflared'
    if not token.is_file() or not binary.is_file():
        raise RuntimeError('Authorized tunnel credential and official cloudflared binary required.')
    token.chmod(0o600)
    install('net.virtualrabbi.tunnel', [str(binary), 'tunnel', '--no-autoupdate', 'run', '--token-file', str(token)])
