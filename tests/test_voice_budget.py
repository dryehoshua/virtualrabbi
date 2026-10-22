import unittest
from unittest.mock import patch
import server

class VoiceBudget(unittest.TestCase):
    def test_non_voice_spend_blocked_before_credentials_or_network(self):
        with patch.dict(server.CONFIG, {'voice_only': True}), patch.object(server, 'key') as key, patch.object(server.urllib.request, 'urlopen') as network:
            for path in ['/responses', '/audio/transcriptions', '/images/generations']:
                with self.assertRaises(ValueError):
                    server.api(path, {})
            key.assert_not_called()
            network.assert_not_called()
