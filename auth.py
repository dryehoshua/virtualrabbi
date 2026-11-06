"""Local account store: scrypt password hashes and revocable opaque sessions."""
import hashlib
import hmac
import secrets
import sqlite3
import time


def connect(state):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = state / 'accounts.sqlite3'
    db = sqlite3.connect(path, timeout=10)
    path.chmod(0o600)
    db.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, salt TEXT, hash TEXT, reader TEXT UNIQUE)')
    db.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, email TEXT, expires INTEGER)')
    columns = {r[1] for r in db.execute('PRAGMA table_info(users)')}
    for column, default in [('name', ''), ('language', 'en')]:
        if column not in columns:
            db.execute(f"ALTER TABLE users ADD COLUMN {column} TEXT DEFAULT '{default}'")
    return db


def password_hash(password, salt):
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()


def create_user(state, email, password, name='', language='en'):
    email = email.strip().lower()
    if not isinstance(email, str) or '@' not in email or len(email)>254 or not 10 <= len(password) <= 256:
        raise ValueError('Valid email and password of at least 10 characters required.')
    salt = secrets.token_hex(16)
    with connect(state) as db:
        db.execute('INSERT INTO users (email,salt,hash,reader,name,language) VALUES (?, ?, ?, ?, ?, ?)', (email, salt, password_hash(password, salt), secrets.token_hex(32), name.strip()[:60], language if language in ('es','en','ru','fr','he','pt') else 'en'))


def login(state, email, password):
    with connect(state) as db:
        row = db.execute('SELECT salt, hash FROM users WHERE email=?', (email.strip().lower(),)).fetchone()
        actual = password_hash(password, row[0] if row else '0'*32)
        if not row or not hmac.compare_digest(actual, row[1]):
            return None
        token = secrets.token_hex(32)
        db.execute('DELETE FROM sessions WHERE expires < ?', (int(time.time()),))
        db.execute('INSERT INTO sessions VALUES (?, ?, ?)', (hashlib.sha256(token.encode()).hexdigest(), email.strip().lower(), int(time.time())+604800))
        return token


def account(state, token):
    if not token or len(token) != 64: return None
    with connect(state) as db:
        row = db.execute('SELECT users.email, users.reader, users.name, users.language FROM sessions JOIN users USING(email) WHERE token=? AND expires>?', (hashlib.sha256(token.encode()).hexdigest(), int(time.time()))).fetchone()
        return {'email': row[0], 'reader': row[1], 'name': row[2], 'language': row[3]} if row else None


def logout(state, token):
    with connect(state) as db:
        db.execute('DELETE FROM sessions WHERE token=?', (hashlib.sha256(token.encode()).hexdigest(),))
