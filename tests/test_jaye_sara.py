import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ChayeiSarah(unittest.TestCase):
    def test_five_bilingual_units_preserve_the_transcribed_source(self):
        units = json.loads((ROOT / 'Estudio/jaye-sara/08-lecciones-01.json').read_text())
        source = json.loads((ROOT / 'Estudio/jaye-sara/09-lineas-01.json').read_text())
        compact = lambda s: ''.join(s.split())
        self.assertEqual(len(units), 5)
        self.assertEqual(compact(''.join(u['hebrew'] for u in units)), compact(''.join(l['text'] for l in source['lines'])))
        self.assertTrue(units[0]['hebrew'].startswith('יגלה לן טעמיה'))
        self.assertTrue(units[-1]['hebrew'].endswith('חיות הנפש הבאה מלמעלה.'))
        self.assertEqual([u['id'] for u in units], [f'jaye-sara-01-{i:02}' for i in range(1, 6)])
        self.assertFalse(any(u['section_end'] for u in units))
        self.assertTrue(units[-1]['installment_end'])
        for u in units:
            for field in ('translation', 'translation_en', 'explanation', 'explanation_en', 'source_notes', 'source_notes_en'):
                self.assertTrue(u[field])
            self.assertEqual(u['pages'], [1])
            self.assertEqual([r['line'] for r in u['regions']], list(range(u['location']['start']['line'], u['location']['end']['line']+1)))
            for r in u['regions']:
                self.assertGreater(r['top'], .32, 'Never highlight the preceding Vayera discourse')
                self.assertLessEqual(r['top']+r['height'], 1)
                self.assertLessEqual(r['left']+r['width'], 1)
