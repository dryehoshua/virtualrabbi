import tempfile
import unittest
from pathlib import Path
import auth

class AuthTests(unittest.TestCase):
    def test_password_sessions_and_revocation(self):
        with tempfile.TemporaryDirectory() as temp:
            state=Path(temp)
            auth.create_user(state,'reader@example.com','test-only-password')
            self.assertIsNone(auth.login(state,'reader@example.com','wrong'))
            self.assertIsNone(auth.login(state,'missing@example.com','wrong'))
            one=auth.login(state,'reader@example.com','test-only-password')
            two=auth.login(state,'reader@example.com','test-only-password')
            self.assertNotEqual(one,two)
            self.assertEqual(auth.account(state,one)['reader'],auth.account(state,two)['reader'])
            self.assertIsNone(auth.account(state,'f'*64))
            auth.logout(state,one)
            self.assertIsNone(auth.account(state,one))
            self.assertIsNotNone(auth.account(state,two))
            self.assertNotIn(b'test-only-password',(state/'accounts.sqlite3').read_bytes())
