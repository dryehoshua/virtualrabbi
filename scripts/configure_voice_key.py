#!/usr/bin/env python3
"""Operator-only setup; secrets are read without echo and stored in macOS Keychain."""
import getpass
import re
import subprocess

secret = getpass.getpass('Clave API exclusiva de Virtual Rabbi (entrada oculta): ').strip()
if not re.fullmatch(r'sk-[A-Za-z0-9_-]{22,500}', secret):
    raise SystemExit('Formato de clave no válido. No se guardó nada.')
command = f'add-generic-password -U -a virtualrabbi.net -s virtualrabbi.net.openai -w "{secret}"\n'
result = subprocess.run(['security', '-i'], input=command, text=True, capture_output=True)
if result.returncode or 'error' in result.stderr.lower() or 'SecKeychain' in result.stderr:
    raise SystemExit('No se pudo guardar la clave en el llavero.')
print('Clave guardada en el llavero. Recarga Virtual Rabbi para activar la llamada.')
