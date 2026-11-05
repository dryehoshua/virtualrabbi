"""Exercise public privacy boundaries without touching the owner's library."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import public_server as public
import server


class PublicReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.doc_id = 'a' * 32
        catalog = self.root / 'catalog' / self.doc_id
        catalog.mkdir(parents=True)
        (catalog / 'documento.json').write_text(json.dumps({
            'id': self.doc_id, 'slug': 'test', 'title': 'Test', 'pages': [],
            'units': [{'id': 'u1'}, {'id': 'u2'}], 'current_unit': 0,
            'completed': [], 'status': 'ready'}))
        self.patches = [patch.object(public, 'STATE', self.root / 'state'),
                        patch.object(public, 'CATALOG', self.root / 'catalog')]
        self.originals = {k: getattr(server, k) for k in ('load', 'save', 'folder', 'library', 'MARKDOWN_ROOT')}
        for p in self.patches: p.start()
        public.LIMITS.clear()
        public.configure()
        self.http = server.ThreadingHTTPServer(('127.0.0.1', 0), public.PublicHandler)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        for k, value in self.originals.items(): setattr(server, k, value)
        for p in self.patches: p.stop()
        self.temp.cleanup()

    def request(self, path, body=None, cookie='', host='virtualrabbi.net', origin='https://virtualrabbi.net'):
        c = http.client.HTTPConnection('127.0.0.1', self.http.server_port, timeout=3)
        headers = {'Host': host, 'Cookie': cookie}
        if origin: headers['Origin'] = origin
        if body is not None: headers['Content-Type'] = 'application/json'
        c.request('POST' if body is not None else 'GET', path, json.dumps(body) if body is not None else None, headers)
        r = c.getresponse()
        result = (r.status, json.loads(r.read()), r.getheader('Set-Cookie', '').split(';')[0])
        c.close()
        return result

    def test_progress_and_history_are_separate(self):
        a = self.request('/api/status')[2]
        b = self.request('/api/status')[2]
        self.assertNotEqual(a, b)
        self.assertEqual(self.request('/api/progress', {'id': self.doc_id, 'current_unit': 1}, a)[0], 200)
        self.assertEqual(self.request('/api/transcript', {'id': self.doc_id, 'text': 'private A'}, a)[0], 200)
        self.assertEqual(self.request('/api/document?id=' + self.doc_id, cookie=a)[1]['current_unit'], 1)
        self.assertEqual(self.request('/api/document?id=' + self.doc_id, cookie=b)[1]['current_unit'], 0)
        self.assertEqual(self.request('/api/history?id=' + self.doc_id, cookie=b)[1], [])
        self.assertEqual(self.request('/api/history?id=' + self.doc_id, cookie=a)[1][0]['text'], 'private A')
        self.assertEqual(json.loads((public.CATALOG / self.doc_id / 'documento.json').read_text())['current_unit'], 0)

    def test_forged_identity_and_cross_site_are_rejected(self):
        a = self.request('/api/status')[2]
        forged = a[:-1] + ('0' if a[-1] != '0' else '1')
        self.assertNotEqual(self.request('/api/status', cookie=forged)[2], '')
        self.assertEqual(self.request('/api/status', host='evil.example')[0], 403)
        self.assertEqual(self.request('/api/progress', {}, origin='https://evil.example')[0], 403)
        self.assertEqual(self.request('/api/progress', {}, origin='')[0], 403)

    def test_voice_admin_and_private_downloads_closed(self):
        with patch.object(server, 'key', side_effect=AssertionError('Must not access owner key')):
            self.assertFalse(self.request('/api/status')[1]['configured'])
            self.assertEqual(self.request('/api/call', {})[0], 503)
            self.assertEqual(self.request('/api/chat', {})[0], 503)
        for route in ('/api/upload', '/api/review', '/api/call-context'):
            self.assertEqual(self.request(route, {})[0], 404)
        self.assertEqual(self.request('/api/download?id=' + self.doc_id + '&file=conversaciones.json')[0], 404)
        self.assertEqual(self.request('/api/history?id=../../Biblioteca')[0], 404)

if __name__ == '__main__': unittest.main()
