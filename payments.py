"""One-time class grants from signed Stripe events; no browser-issued credits."""
import json
import secrets
import sqlite3
import time
from urllib.parse import urlencode
import stripe

CLASS_SECONDS = 1800
CLASS_COST_USD = 4.00  # measured API safety ceiling; not a provider billing guarantee
LINK_ID = 'plink_1UYZ5C1fJ8c9bLD8jeDbdnDv'
LINK_URL = 'https://buy.stripe.com/bJe28j9sRc5jeKb3q77kc00'


def connect(state):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = state / 'classes.sqlite3'
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    path.chmod(0o600)
    db.executescript('''
      CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, reader TEXT NOT NULL, created REAL NOT NULL);
      CREATE TABLE IF NOT EXISTS grants (id TEXT PRIMARY KEY, reader TEXT NOT NULL, payment_intent TEXT,
        remaining REAL NOT NULL, cost REAL NOT NULL DEFAULT 0, revoked INTEGER NOT NULL DEFAULT 0);
      CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, received REAL NOT NULL);
      CREATE TABLE IF NOT EXISTS refunds (payment_intent TEXT PRIMARY KEY);
      CREATE TABLE IF NOT EXISTS calls (id TEXT PRIMARY KEY, reader TEXT NOT NULL, grant_id TEXT NOT NULL,
        provider TEXT, started REAL NOT NULL, deadline REAL, heartbeat REAL, status TEXT NOT NULL, reason TEXT);
      CREATE UNIQUE INDEX IF NOT EXISTS one_active_call ON calls(reader) WHERE status IN ('starting','active','closing');
      CREATE TABLE IF NOT EXISTS usage (call_id TEXT, event_id TEXT, kind TEXT, cost REAL, details TEXT,
        PRIMARY KEY(call_id,event_id,kind));
      CREATE TABLE IF NOT EXISTS call_meter (call_id TEXT PRIMARY KEY, elapsed REAL NOT NULL DEFAULT 0,
        tick REAL NOT NULL, seen REAL NOT NULL, last_active REAL NOT NULL,
        channels TEXT NOT NULL DEFAULT '{}');
    ''')
    return db


def checkout(state, reader, language):
    reference = secrets.token_hex(24)
    with connect(state) as db:
        db.execute('INSERT INTO orders VALUES (?,?,?)', (reference, reader, time.time()))
    return LINK_URL + '?' + urlencode({'client_reference_id': reference, 'locale': language if language in ('en','es','ru','fr','he','pt') else 'en'})


def process_event(state, event):
    """Caller must verify signature first. Fulfill once per paid checkout session."""
    if event.get('livemode') is not True:
        raise ValueError('Live payment required')
    obj = event.get('data', {}).get('object', {})
    with connect(state) as db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT 1 FROM events WHERE id=?', (event['id'],)).fetchone():
            return
        kind = event.get('type')
        if kind in ('checkout.session.completed', 'checkout.session.async_payment_succeeded'):
            if obj.get('payment_status') == 'paid' and obj.get('mode') == 'payment' and obj.get('payment_link') == LINK_ID:
                # Adaptive pricing can change presentment currency; the fixed USD price on this
                # allowlisted link is authoritative. Currency conversions are Stripe-managed.
                order = db.execute('SELECT reader FROM orders WHERE id=?', (obj.get('client_reference_id'),)).fetchone()
                if order and obj.get('amount_total', 0) > 0:
                    revoked = bool(db.execute('SELECT 1 FROM refunds WHERE payment_intent=?', (obj.get('payment_intent'),)).fetchone())
                    db.execute('INSERT OR IGNORE INTO grants (id,reader,payment_intent,remaining,revoked) VALUES (?,?,?,?,?)',
                               (obj['id'], order['reader'], obj.get('payment_intent'), CLASS_SECONDS, revoked))
        elif kind in ('charge.refunded','charge.dispute.created'):
            pi = obj.get('payment_intent')
            if pi:
                db.execute('INSERT OR IGNORE INTO refunds VALUES (?)', (pi,))
                db.execute('UPDATE grants SET revoked=1 WHERE payment_intent=?', (pi,))
        db.execute('INSERT INTO events VALUES (?,?)', (event['id'], time.time()))


def webhook(state, raw, signature):
    secret = (state / 'stripe-webhook-secret').read_text().strip()
    stripe.Webhook.construct_event(raw, signature, secret, tolerance=300)
    process_event(state, json.loads(raw))


def balance(state, reader):
    with connect(state) as db:
        row = db.execute('SELECT COALESCE(SUM(remaining),0) seconds, COUNT(*) classes FROM grants WHERE reader=? AND revoked=0 AND remaining>0 AND cost<?', (reader, CLASS_COST_USD)).fetchone()
        call = db.execute("SELECT id,deadline,status,reason FROM calls WHERE reader=? AND status IN ('starting','active','closing')", (reader,)).fetchone()
        seconds = row['seconds']
        if call:
            active = get_call(state, call['id'])
            if not active['revoked'] and active['cost'] < CLASS_COST_USD:
                seconds = max(0, seconds - elapsed_seconds(active, time.time()))
        last = db.execute('SELECT reason FROM calls WHERE reader=? ORDER BY started DESC LIMIT 1', (reader,)).fetchone()
        return {'seconds': int(seconds), 'classes': row['classes'], 'active_call': dict(call) if call else None, 'last_reason': last['reason'] if last else None}


def reserve(state, reader):
    now = time.time()
    with connect(state) as db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute("SELECT COUNT(*) FROM calls WHERE status IN ('starting','active','closing')").fetchone()[0] >= 4:
            raise ValueError('All study rooms are busy. Please try again shortly.')
        grant = db.execute('SELECT * FROM grants WHERE reader=? AND revoked=0 AND remaining>0 AND cost<? ORDER BY rowid LIMIT 1', (reader,CLASS_COST_USD)).fetchone()
        if not grant:
            raise PermissionError('A confirmed US$5 contribution is required for a class.')
        call_id = secrets.token_hex(24)
        try:
            db.execute('INSERT INTO calls (id,reader,grant_id,started,heartbeat,status) VALUES (?,?,?,?,?,?)', (call_id,reader,grant['id'],now,now,'starting'))
        except sqlite3.IntegrityError:
            raise ValueError('You already have an active class. Return to that call or end it first.') from None
        return call_id, grant['remaining']


def activate(state, call_id, provider, seconds):
    now=time.time()
    with connect(state) as db:
        db.execute("UPDATE calls SET provider=?,started=?,deadline=NULL,heartbeat=?,status='active' WHERE id=?", (provider,now,now,call_id))
        db.execute('INSERT INTO call_meter(call_id,tick,seen,last_active) VALUES (?,?,?,?)', (call_id,now,now,now))


def get_call(state, call_id, reader=None):
    with connect(state) as db:
        row=db.execute('SELECT calls.*, grants.cost, grants.revoked, grants.remaining, call_meter.elapsed, call_meter.tick, call_meter.seen, call_meter.last_active, call_meter.channels FROM calls JOIN grants ON grants.id=calls.grant_id LEFT JOIN call_meter ON call_meter.call_id=calls.id WHERE calls.id=?', (call_id,)).fetchone()
        if not row or (reader is not None and row['reader'] != reader):
            raise PermissionError('Call unavailable')
        return dict(row)


def elapsed_seconds(call, now):
    if call.get('elapsed') is None:
        # Old calls retain their original accounting; new calls always have a meter.
        return max(0, now-call['started']) if call['provider'] else 0
    # A crashed/disconnected monitor cannot charge unattended downtime.
    tail = max(0, min(now, call['seen']+3)-call['tick']) if json.loads(call['channels']) else 0
    return call['elapsed'] + tail


def call_remaining(call, now):
    return max(0, call['remaining']-elapsed_seconds(call, now))


def meter_activity(state, call_id, event=None):
    """Only the trusted provider monitor may update activity, never browser heartbeats.

    Count the union of learner speech and delivered agent audio. Overlap is counted
    once. Response IDs prevent an old/duplicate stop from clearing newer playback.
    """
    now=time.time()
    with connect(state) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute("SELECT call_meter.* FROM call_meter JOIN calls ON calls.id=call_meter.call_id WHERE call_id=? AND status='active'", (call_id,)).fetchone()
        if not row: return
        channels=json.loads(row['channels'])
        elapsed=row['elapsed'] + (max(0,min(now,row['seen']+3)-row['tick']) if channels else 0)
        last_active=now if channels else row['last_active']
        if event:
            kind=event.get('type','')
            if kind in ('input_audio_buffer.speech_started','output_audio_buffer.started'):
                channel='input' if kind.startswith('input') else 'output'
                channels[channel]=event.get('item_id' if channel=='input' else 'response_id') or 'active'
                last_active=now
            elif kind in ('input_audio_buffer.speech_stopped','output_audio_buffer.stopped','output_audio_buffer.cleared'):
                channel='input' if kind.startswith('input') else 'output'
                identifier=event.get('item_id' if channel=='input' else 'response_id')
                if not identifier or channels.get(channel)==identifier:
                    channels.pop(channel,None)
        db.execute('UPDATE call_meter SET elapsed=?,tick=?,seen=?,last_active=?,channels=? WHERE call_id=?',
                   (elapsed,now,now,last_active,json.dumps(channels),call_id))


def freeze_meter(state, call_id):
    """Freeze on termination, before provider hangup/network retries."""
    now=time.time()
    with connect(state) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT * FROM call_meter WHERE call_id=?',(call_id,)).fetchone()
        if row:
            elapsed=row['elapsed']+(max(0,min(now,row['seen']+3)-row['tick']) if json.loads(row['channels']) else 0)
            db.execute("UPDATE call_meter SET elapsed=?,tick=?,channels='{}' WHERE call_id=?",(elapsed,now,call_id))


def finish(state, call_id, reason):
    freeze_meter(state, call_id)
    with connect(state) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT * FROM calls WHERE id=?', (call_id,)).fetchone()
        if not row or row['status']=='closed': return
        meter=db.execute('SELECT elapsed FROM call_meter WHERE call_id=?',(call_id,)).fetchone()
        elapsed=meter['elapsed'] if meter else (max(0, time.time()-row['started']) if row['provider'] else 0)
        db.execute('UPDATE grants SET remaining=MAX(0,remaining-?) WHERE id=?', (elapsed,row['grant_id']))
        if reason=='budget': db.execute('UPDATE grants SET remaining=0 WHERE id=?', (row['grant_id'],))
        db.execute("UPDATE calls SET status='closed',reason=? WHERE id=?", (reason,call_id))


def record_usage(state, call_id, event_id, kind, usage, cost):
    with connect(state) as db:
        db.execute('BEGIN IMMEDIATE')
        added=db.execute('INSERT OR IGNORE INTO usage VALUES (?,?,?,?,?)', (call_id,event_id,kind,cost,json.dumps(usage))).rowcount
        if added:
            db.execute('UPDATE grants SET cost=cost+? WHERE id=(SELECT grant_id FROM calls WHERE id=?)', (cost,call_id))
