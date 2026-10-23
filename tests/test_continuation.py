import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('extension',Path(__file__).resolve().parents[1]/'scripts/extend_lej_leja.py')
extension=importlib.util.module_from_spec(spec)
spec.loader.exec_module(extension)

class Continuation(unittest.TestCase):
    def test_append_is_idempotent_and_preserves_existing_study(self):
        doc={'units':[{'id':'old','hebrew':'אב'}],'cursor':{'unit_id':'old','phase':'translation'},'current_unit':0,'completed':['old'],'location':{'page':1,'line':5}}
        before=copy.deepcopy(doc)
        with patch.object(extension.server,'update',side_effect=lambda _id,fn:fn(doc)):
            extension.extend()
            extension.extend()
        self.assertEqual(len(doc['units']),36)
        self.assertEqual(len({u['id'] for u in doc['units']}),36)
        self.assertEqual(doc['units'][0],before['units'][0])
        for key in ('cursor','current_unit','completed','location'):
            self.assertEqual(doc[key],before[key])
        for unit in doc['units'][1:]:
            for field in ('hebrew','translation','translation_en','explanation','explanation_en'):
                self.assertTrue(unit[field])
            for region in unit['regions']:
                self.assertLessEqual(region['left']+region['width'],1)
                self.assertLessEqual(region['top']+region['height'],1)

    def test_full_second_sheet_and_open_paragraph_boundary(self):
        units=extension.additions()[3:18]
        self.assertEqual([u['id'] for u in units],[f'lej-leja-01-{n}' for n in range(14,29)])
        for column,total in [('right',49),('left',50)]:
            lines={r['line'] for u in units for r in u['regions'] if r['page']==2 and r['column']==column}
            self.assertEqual(lines,set(range(1,total+1)))
        self.assertTrue(units[0]['hebrew'].startswith('ובחכמה עצמה'))
        self.assertTrue(units[-1]['hebrew'].endswith('מן שכל הנעלם'))
        self.assertEqual(units[-1]['continues_on_page'],3)
        self.assertFalse(units[-1]['paragraph_complete'])
        self.assertFalse(any(u.get('section_end') for u in units))

    def test_third_sheet_discourses_and_continuity(self):
        units=extension.additions()[18:]
        self.assertEqual([u['id'] for u in units],[f'lej-leja-01-{n}' for n in range(29,46)])
        for column in ('right','left'):
            lines={r['line'] for u in units for r in u['regions'] if r['page']==3 and r['column']==column}
            self.assertEqual(lines,set(range(1,51)))
        self.assertEqual(units[0]['continues_from_unit'],'lej-leja-01-28')
        self.assertTrue(units[1]['discourse_end'])
        self.assertTrue(units[2]['discourse_start'])
        self.assertTrue(units[5]['discourse_end'])
        self.assertTrue(units[6]['discourse_start'])
        self.assertEqual(units[-1]['continues_on_page'],4)
        self.assertTrue(units[-1]['hebrew'].endswith('שהוא'))
        self.assertFalse(any(u['section_end'] for u in units))

    def test_commentary_revision_preserves_source_and_cursor(self):
        doc={'units':[{'id':'lej-leja-01-05','hebrew':'מקור','explanation':'old','explanation_en':'old'}], 'cursor':{'unit_id':'lej-leja-01-05','phase':'translation'}}
        with patch.object(extension.server,'update',side_effect=lambda _id,fn:fn(doc)):
            extension.extend()
        self.assertEqual(doc['units'][0]['hebrew'],'מקור')
        self.assertEqual(doc['cursor'],{'unit_id':'lej-leja-01-05','phase':'translation'})
        self.assertIn('milah',doc['units'][0]['explanation_en'])
        self.assertNotEqual(doc['units'][0]['explanation'],'old')
