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

    def test_selected_voice_and_speed_are_validated(self):
        for voice in server.VOICE_CHOICES:
            for speed in server.VOICE_SPEEDS:
                self.assertEqual(server.call_audio_options({'voice':voice,'speed':speed}),{'voice':voice,'speed':speed})
        for invalid in [{'voice':'coral'},{'speed':True},{'speed':2},{'speed':'1.25'},{'speed':float('nan')}]:
            with self.assertRaises(ValueError):
                server.call_audio_options(invalid)
