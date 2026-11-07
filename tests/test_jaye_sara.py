import json
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ChayeiSarah(unittest.TestCase):
    def test_second_batch_crosses_columns_without_skipping_source(self):
        units = json.loads((ROOT / 'Estudio/jaye-sara/08-lecciones-02.json').read_text())
        source = json.loads((ROOT / 'Estudio/jaye-sara/09-lineas-02.json').read_text())
        compact = lambda s: ''.join(s.split())
        self.assertEqual(len(units), 5)
        self.assertEqual(compact(''.join(u['hebrew'] for u in units)), compact(''.join(l['text'] for l in source['lines'])))
        self.assertEqual([u['id'] for u in units], [f'jaye-sara-01-{i:02}' for i in range(6, 11)])
        self.assertTrue(units[0]['hebrew'].startswith("ובטן רשעים כו'"))
        self.assertTrue(units[-1]['hebrew'].endswith('המשכה שמלמעלה דלא יגורך רע כלל.'))
        self.assertEqual(units[1]['location']['start']['column'], 'right')
        self.assertEqual(units[1]['location']['end']['column'], 'left')
        self.assertEqual({(r['column'],r['line']) for r in units[1]['regions']}, {('right',n) for n in range(28,34)} | {('left',n) for n in range(1,7)})
        self.assertFalse(any(u['section_end'] for u in units))
        for u in units:
            for field in ('translation','translation_en','explanation','explanation_en'):
                self.assertTrue(u[field])
            for r in u['regions']:
                self.assertGreater(r['top'], .32)
                self.assertLessEqual(r['top']+r['height'], 1)
                self.assertLessEqual(r['left']+r['width'], 1)

    def test_extension_preserves_completed_first_batch_and_checkpoint(self):
        spec = importlib.util.spec_from_file_location('sarah_extension', ROOT / 'scripts/extend_jaye_sara.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        first = json.loads((ROOT / 'Estudio/jaye-sara/08-lecciones-01.json').read_text())
        doc = {'units':copy.deepcopy(first), 'pages':[], 'current_unit':4, 'completed':[u['id'] for u in first], 'cursor':{'unit_id':first[-1]['id'],'phase':'pause'}, 'location':first[-1]['location']['start'], 'study_language':'en'}
        before = copy.deepcopy(doc)
        module.refresh_content(doc)
        module.refresh_content(doc)
        self.assertEqual(len(doc['units']), 10)
        for key in ('current_unit','completed','cursor','location','study_language'):
            self.assertEqual(doc[key], before[key])
        self.assertEqual([u['hebrew'] for u in doc['units'][:5]], [u['hebrew'] for u in first])
        self.assertFalse(doc['units'][4]['installment_end'])
        self.assertEqual(doc['units'][4]['continues_to_unit'], doc['units'][5]['id'])

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
