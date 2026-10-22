#!/usr/bin/env python3
"""Install a local-only background service and a desktop launcher. No network hosting."""
import os
import plistlib
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
app = Path.home() / 'Desktop' / 'Virtual Rabbi.app'
contents = app / 'Contents'
(contents / 'MacOS').mkdir(parents=True, exist_ok=True)
(contents / 'Resources').mkdir(exist_ok=True)
runtime = root / '.runtime'
runtime.mkdir(exist_ok=True)
iconset = runtime / 'VirtualRabbi.iconset'
iconset.mkdir(exist_ok=True)
image = Image.open(runtime / 'virtual-rabbi.png').convert('RGBA')
for size in (16,32,128,256,512):
    for scale in (1,2):
        name = f'icon_{size}x{size}' + ('@2x' if scale == 2 else '') + '.png'
        image.resize((size*scale,size*scale),Image.Resampling.LANCZOS).save(iconset/name)
subprocess.run(['/usr/bin/iconutil','-c','icns',str(iconset),'-o',str(contents/'Resources'/'VirtualRabbi.icns')],check=True)
with (contents/'Info.plist').open('wb') as f:
    plistlib.dump({'CFBundleName':'Virtual Rabbi','CFBundleDisplayName':'Virtual Rabbi','CFBundleIdentifier':'net.virtualrabbi.local','CFBundleVersion':'1','CFBundleShortVersionString':'0.1.0','CFBundleExecutable':'VirtualRabbi','CFBundlePackageType':'APPL','CFBundleIconFile':'VirtualRabbi','LSUIElement':True}, f)
launcher = contents / 'MacOS' / 'VirtualRabbi'
launcher.write_text('''#!/bin/zsh
if ! /usr/bin/curl -fsS --max-time 2 http://127.0.0.1:8790/ >/dev/null; then
  /bin/launchctl kickstart gui/$(/usr/bin/id -u)/net.virtualrabbi.local
  for attempt in {1..40}; do
    /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:8790/ >/dev/null && break
    /bin/sleep 0.25
  done
fi
/usr/bin/open http://127.0.0.1:8790/
''')
launcher.chmod(0o755)
agent = Path.home() / 'Library' / 'LaunchAgents' / 'net.virtualrabbi.local.plist'
agent.parent.mkdir(parents=True, exist_ok=True)
python = Path(sys.executable)
with agent.open('wb') as f:
    plistlib.dump({'Label':'net.virtualrabbi.local','ProgramArguments':[str(python),'-u',str(root/'server.py')],'WorkingDirectory':str(root),'RunAtLoad':True,'KeepAlive':True,'StandardOutPath':str(runtime/'server.log'),'StandardErrorPath':str(runtime/'server-error.log'),'EnvironmentVariables':{'LANG':'en_US.UTF-8','LC_ALL':'en_US.UTF-8'}},f)
uid = str(os.getuid())
subprocess.run(['launchctl','bootout',f'gui/{uid}/net.virtualrabbi.local'],capture_output=True)
# Replace only this checkout's current preview server, if present.
pids = subprocess.run(['lsof','-tiTCP:8790','-sTCP:LISTEN'],capture_output=True,text=True).stdout.split()
for pid in pids:
    cmd = subprocess.run(['ps','-p',pid,'-o','command='],capture_output=True,text=True).stdout
    if 'server.py' not in cmd:
        raise RuntimeError('El puerto 8790 pertenece a otra aplicación.')
    os.kill(int(pid),15)
subprocess.run(['launchctl','bootstrap',f'gui/{uid}',str(agent)],check=True)
for _ in range(50):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8790/',timeout=1) as r:
            if r.status == 200:
                print('Instalado: '+str(app))
                print('Disponible: http://127.0.0.1:8790')
                break
    except Exception:
        time.sleep(.2)
else:
    raise RuntimeError('El servicio no respondió; revisar .runtime/server-error.log.')
