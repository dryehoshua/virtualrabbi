#!/usr/bin/env python3
"""Public reading service. Never exposes the operator's writable library or API key.

Runs in a separate process from server.py. Anonymous reader identities are signed,
HttpOnly cookies; they are browser profiles, not cross-device accounts. Voice and
checkout intentionally stay closed until funding and usage controls are configured.
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from contextvars import ContextVar
from http.cookies import SimpleCookie, CookieError
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import server
import auth

ROOT = server.ROOT
STATE = Path(os.environ.get('RABBI_PUBLIC_STATE', ROOT / '.runtime/public'))
CATALOG = Path(os.environ.get('RABBI_PUBLIC_CATALOG', ROOT / '.runtime/public-catalog'))
PORT = int(os.environ.get('RABBI_PUBLIC_PORT', '8791'))
HOSTS = {'virtualrabbi.net', 'www.virtualrabbi.net'}
READER = ContextVar('reader')
SECRET = b''
COOKIE = '__Host-rabbi_reader'
PERSONAL = ('current_unit', 'completed', 'cursor', 'location', 'location_unmapped', 'study_language', 'updated_at')
GET_PATHS = {'/', '/study', '/landing.css', '/landing.js', '/api/me', '/app.js', '/style.css', '/icon.svg', '/rabbi-portrait.png', '/api/status', '/api/library', '/api/document', '/api/history', '/api/page', '/api/download'}
POST_PATHS = {'/api/login', '/api/logout', '/api/progress', '/api/cursor', '/api/location', '/api/language', '/api/note', '/api/transcript'}
LIMIT_LOCK = threading.Lock()
LIMITS = {}
SUPPORT_AMOUNTS = ('5', '18', '52', '100', '260', '450', '1800', 'other')


def support_links():
    """Only public Stripe payment links; never keys or arbitrary redirects."""
    path = STATE / 'support-links.json'
    if not path.is_file():
        return {}
    data = json.loads(path.read_text())
    return {amount: url for amount, url in data.items()
            if amount in SUPPORT_AMOUNTS and isinstance(url, str)
            and urlparse(url).scheme == 'https' and urlparse(url).netloc == 'buy.stripe.com'}


def catalog_folder(doc_id):
    if not re.fullmatch(r'[0-9a-f]{32}', doc_id or '') or not (CATALOG / doc_id / 'documento.json').is_file():
        raise FileNotFoundError('Lección no disponible.')
    return CATALOG / doc_id


def reader_folder(doc_id):
    catalog_folder(doc_id)
    return STATE / 'readers' / READER.get() / doc_id


def read_document(doc_id):
    doc = json.loads((catalog_folder(doc_id) / 'documento.json').read_text())
    state_file = reader_folder(doc_id) / 'progress.json'
    if state_file.exists():
        state = json.loads(state_file.read_text())
        doc.update({k: state[k] for k in PERSONAL if k in state})
    return doc


def save_progress(doc):
    doc['updated_at'] = server.now()
    target = reader_folder(doc['id'])
    server.dump(target / 'progress.json', {k: doc[k] for k in PERSONAL if k in doc})


def public_library():
    documents = []
    for path in sorted(CATALOG.glob('*/documento.json')):
        d = read_document(path.parent.name)
        documents.append({k: d.get(k) for k in ('id', 'title', 'author', 'status', 'created_at', 'updated_at', 'current_unit', 'completed')} | {'page_count': len(d['pages']), 'unit_count': len(d['units'])})
    return documents


class ReaderMarkdown:
    def __truediv__(self, slug):
        if not re.fullmatch(r'[a-z0-9-]+', slug):
            raise ValueError('Nombre no válido.')
        path = STATE / 'readers' / READER.get() / 'markdown' / slug
        path.mkdir(parents=True, exist_ok=True)
        return path


def limited(key, maximum, window=60):
    now = time.monotonic()
    with LIMIT_LOCK:
        if len(LIMITS) > 10000:
            for stale in [k for k, v in LIMITS.items() if now - v[0] > 86400]:
                del LIMITS[stale]
            if len(LIMITS) > 10000:
                return True
        started, count = LIMITS.get(key, (now, 0))
        if now - started >= window:
            started, count = now, 0
        LIMITS[key] = (started, count + 1)
        return count >= maximum


class PublicHandler(server.Handler):
    def end_headers(self):
        if getattr(self, 'new_cookie', None):
            self.send_header('Set-Cookie', self.new_cookie)
        self.send_header('Strict-Transport-Security', 'max-age=31536000')
        self.send_header('Permissions-Policy', 'camera=(), geolocation=(), microphone=(self)')
        super().end_headers()

    def allowed(self):
        # The connector forwards the original host. No wildcard hosts or origins.
        host = self.headers.get('Host', '')
        if host not in HOSTS or (self.command == 'POST' and self.headers.get('Sec-Fetch-Site') == 'cross-site'):
            self.reply({'error': 'Solicitud no permitida.'}, 403)
            return False
        origin = self.headers.get('Origin')
        if (origin and origin != 'https://' + host) or (self.command == 'POST' and not origin):
            self.reply({'error': 'Origen no permitido.'}, 403)
            return False
        return True

    def session_token(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', '')[:4096])
        except CookieError:
            return ''
        return cookie['__Host-rabbi_session'].value if '__Host-rabbi_session' in cookie else ''

    def identity(self):
        self.account = auth.account(STATE, self.session_token())
        if self.account:
            return self.account['reader']
        self.new_cookie = None
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', '')[:4096])
        except CookieError:
            pass
        value = cookie[COOKIE].value if COOKIE in cookie else ''
        parts = value.split('.')
        valid = len(parts) == 2 and re.fullmatch(r'[0-9a-f]{64}', parts[0]) and hmac.compare_digest(hmac.new(SECRET, parts[0].encode(), hashlib.sha256).hexdigest(), parts[1])
        if valid:
            return parts[0]
        ip = self.headers.get('CF-Connecting-IP', self.client_address[0])
        if limited(('new-reader', ip), 60, 86400):
            self.reply({'error': 'Demasiadas sesiones nuevas. Inténtalo más tarde.'}, 429)
            return None
        identity = secrets.token_hex(32)
        signature = hmac.new(SECRET, identity.encode(), hashlib.sha256).hexdigest()
        self.new_cookie = f'{COOKIE}={identity}.{signature}; Path=/; Max-Age=31536000; Secure; HttpOnly; SameSite=Lax'
        return identity

    def dispatch(self):
        self.new_cookie = None
        if not self.allowed():
            return
        if self.command == 'GET' and (self.headers.get('Host') == 'www.virtualrabbi.net'
                                     or self.headers.get('X-Forwarded-Proto') == 'http'):
            self.send_response(308)
            self.send_header('Location', 'https://virtualrabbi.net' + self.path)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        parsed = urlparse(self.path)
        if parsed.path in ('/api/call', '/api/chat', '/api/checkout'):
            self.reply({'error': 'Las llamadas estarán disponibles próximamente. / Voice study is coming soon.', 'code': 'voice_not_available'}, 503)
            return
        permitted = GET_PATHS if self.command == 'GET' else POST_PATHS
        if parsed.path not in permitted:
            self.reply({'error': 'Ruta no disponible.'}, 404)
            return
        if self.command == 'POST':
            try:
                length = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                length = 0
            if not 0 < length <= 65536:
                self.reply({'error': 'Solicitud demasiado grande.'}, 413)
                return
        if parsed.path in ('/api/login', '/api/logout'):
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.reply({'error': 'JSON required'}, 400)
            ip = self.headers.get('CF-Connecting-IP', self.client_address[0])
            if limited(('login', ip), 10, 600):
                return self.reply({'error': 'Espera unos minutos. / Try again in a few minutes.'}, 429)
            try:
                body = json.loads(self.rfile.read(length))
                if parsed.path == '/api/logout':
                    auth.logout(STATE, self.session_token())
                    self.new_cookie = '__Host-rabbi_session=; Path=/; Max-Age=0; Secure; HttpOnly; SameSite=Lax'
                    return self.reply({'ok': True})
                email, password = body.get('email', ''), body.get('password', '')
                if not isinstance(email, str) or not isinstance(password, str) or len(email)>254 or len(password)>256:
                    raise ValueError()
                session = auth.login(STATE, email, password)
                if not session:
                    return self.reply({'error': 'Correo o contraseña incorrectos. / Invalid email or password.'}, 401)
                self.new_cookie = f'__Host-rabbi_session={session}; Path=/; Max-Age=604800; Secure; HttpOnly; SameSite=Lax'
                return self.reply({'ok': True})
            except (ValueError, TypeError, AttributeError):
                return self.reply({'error': 'Solicitud no válida.'}, 400)
        identity = self.identity()
        if not identity:
            return
        token = READER.set(identity)
        try:
            if limited(('requests', identity), 180):
                self.reply({'error': 'Espera un momento antes de continuar.'}, 429)
                return
            if self.command == 'POST':
                if parsed.path in ('/api/note', '/api/transcript') and limited(('notes', identity), 1000, 86400):
                    self.reply({'error': 'Límite diario de mensajes alcanzado.'}, 429)
                    return
                return super().do_POST()
            if parsed.path == '/api/me':
                return self.reply({'email': self.account['email'] if self.account else None})
            if parsed.path in ('/', '/study', '/landing.css', '/landing.js'):
                filename = {'/': 'landing.html', '/study': 'index.html'}.get(parsed.path, parsed.path[1:])
                mime = 'text/html; charset=utf-8' if filename.endswith('.html') else ('text/css' if filename.endswith('.css') else 'text/javascript')
                return self.reply((ROOT / 'web' / filename).read_bytes(), mime=mime)
            if parsed.path == '/api/status':
                return self.reply({'configured': False, 'voice_only': True, 'public': True, 'billing_status': 'coming_soon', 'identity_mode': 'browser', 'voice_model': server.CONFIG['voice_model'], 'support_links': support_links()})
            params = parse_qs(parsed.query)
            if parsed.path == '/api/page':
                path = catalog_folder(params.get('id', [''])[0])
                number = int(params.get('page', ['0'])[0])
                if not 1 <= number <= 150:
                    raise ValueError('Página no válida.')
                return self.reply((path / 'hojas' / f'pagina-{number}.jpg').read_bytes(), mime='image/jpeg')
            if parsed.path == '/api/download':
                path = catalog_folder(params.get('id', [''])[0])
                name = params.get('file', [''])[0]
                if name not in ('original.pdf', 'guia-estudio-es.md', 'guia-estudio-en.md', 'hebreo-revisado.txt', 'exegesis.md'):
                    self.reply({'error': 'Archivo no disponible.'}, 404)
                    return
                return self.reply((path / name).read_bytes(), mime='application/pdf' if name.endswith('.pdf') else 'text/plain; charset=utf-8')
            return super().do_GET()
        except (ValueError, FileNotFoundError):
            self.reply({'error': 'Contenido no disponible.'}, 404)
        except Exception:
            self.reply({'error': 'No se pudo completar la solicitud.'}, 500)
        finally:
            READER.reset(token)

    do_GET = dispatch
    do_POST = dispatch


def configure():
    global SECRET
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    secret_path = STATE / 'cookie-secret'
    if not secret_path.exists():
        fd = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as f:
            f.write(secrets.token_bytes(32))
    SECRET = secret_path.read_bytes()
    # These hooks exist only in this public process; the local operator service
    # continues to use its original library and Markdown writer on port 8790.
    server.load = read_document
    server.save = save_progress
    server.folder = reader_folder
    server.library = public_library
    server.MARKDOWN_ROOT = ReaderMarkdown()


if __name__ == '__main__':
    configure()
    print(f'Virtual Rabbi public reader · 127.0.0.1:{PORT}', flush=True)
    server.ThreadingHTTPServer(('127.0.0.1', PORT), PublicHandler).serve_forever()
