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
        self.assertEqual(len(doc['units']),4)
        self.assertEqual(doc['units'][0],before['units'][0])
        for key in ('cursor','current_unit','completed','location'):
            self.assertEqual(doc[key],before[key])
        for unit in doc['units'][1:]:
            for field in ('hebrew','translation','translation_en','explanation','explanation_en'):
                self.assertTrue(unit[field])
            for region in unit['regions']:
                self.assertLessEqual(region['left']+region['width'],1)
                self.assertLessEqual(region['top']+region['height'],1)
