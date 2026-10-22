import copy
import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from pypdf import PdfWriter
import server
from curriculum import align_units, source_blocks, validate_lines


class StudyIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.old_data, cls.old_markdown, cls.old_port = server.DATA, server.MARKDOWN_ROOT, server.PORT
        server.DATA = Path(cls.temp.name) / 'library'
        server.MARKDOWN_ROOT = Path(cls.temp.name) / 'markdown'
        cls.http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        server.PORT = cls.http.server_port
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        server.DATA, server.MARKDOWN_ROOT, server.PORT = cls.old_data, cls.old_markdown, cls.old_port
        cls.temp.cleanup()

    def call(self, path, body=None, origin=None):
        headers = {}
        if body is not None:
            headers['Content-Type'] = 'application/json'
        if origin:
            headers['Origin'] = origin
        req = urllib.request.Request(f'http://127.0.0.1:{server.PORT}'+path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def make_doc(self):
        doc_id = __import__('uuid').uuid4().hex
        page = {'number':1,'hebrew':'אב גד\nהו זח','raw':'אב גד\nהו זח','warnings':[],'lines':[{'column':'right','line':1,'text':'אב גד'},{'column':'right','line':2,'text':'הו זח'}],'approved':True,'ocr_done':True}
        unit = {'id':'unit-one','title':'Prueba','title_en':'Test','hebrew':'אב גד\nהו זח','translation':'Prueba','translation_en':'Test','explanation':'Explicación','explanation_en':'Explanation','source_notes':'Sin verificar','source_notes_en':'Unverified','questions':['¿Qué?'],'questions_en':['What?'],'sources':[],'pages':[1],'location':{'start':{'page':1,'column':'right','line':1},'end':{'page':1,'column':'right','line':2}}}
        d = {'id':doc_id,'title':'Prueba','created_at':server.now(),'status':'ready','pages':[page],'units':[unit],'current_unit':0,'completed':[],'location':{'page':1,'column':'right','line':2},'cursor':{'unit_id':'unit-one','phase':'translation','interrupted':True},'study_language':'es'}
        server.save(d)
        return d

    def test_questions_do_not_move_checkpoint_and_transcripts_deduplicate(self):
        d = self.make_doc()
        body = {'id':d['id'],'message_id':'same','text':'¿Qué significa?','role':'user','unit_id':'unit-one'}
        self.call('/api/transcript',body)
        self.call('/api/transcript',body)
        with patch('server.api', return_value={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'Explicación del texto.'}]}]}):
            code, result = self.call('/api/chat', {'id':d['id'],'unit_id':'unit-one','message':'¿Qué significa?','history':[]})
            self.assertEqual(code,200)
            self.assertEqual(result['text'],'Explicación del texto.')
        _, reloaded = self.call('/api/document?id='+d['id'])
        self.assertEqual(reloaded['cursor'],d['cursor'])
        self.assertEqual(reloaded['location'],d['location'])
        _, history = self.call('/api/history?id='+d['id'])
        self.assertEqual(len(history),1)

    def test_cursor_and_language_survive_reload_and_markdown_export(self):
        d = self.make_doc()
        self.call('/api/cursor',{'id':d['id'],'unit_id':'unit-one','phase':'explanation','interrupted':True})
        self.call('/api/language',{'id':d['id'],'language':'en'})
        _, reloaded = self.call('/api/document?id='+d['id'])
        self.assertEqual(reloaded['location']['line'],2)
        self.assertEqual(reloaded['cursor']['phase'],'explanation')
        self.assertTrue(reloaded['cursor']['interrupted'])
        self.assertEqual(reloaded['study_language'],'en')
        checkpoint = (server.MARKDOWN_ROOT/d['id']/'05-progreso.md').read_text()
        self.assertIn('"phase": "explanation"',checkpoint)
        self.assertTrue((server.MARKDOWN_ROOT/d['id']/'03-study-en.md').exists())

    def test_unknown_location_is_saved_without_inventing_reading(self):
        d=self.make_doc()
        _, result=self.call('/api/location',{'id':d['id'],'location':{'page':1,'column':'left','line':30}})
        self.assertTrue(result['location_unmapped'])
        self.assertEqual(result['location']['line'],30)

    def test_revised_source_invalidates_exegesis_and_keeps_history(self):
        d=self.make_doc()
        _, updated=self.call('/api/review',{'id':d['id'],'page':1,'hebrew':'אב חדש','approved':True})
        self.assertEqual(updated['units'],[])
        self.assertEqual(updated['pages'][0]['lines'],[])
        self.assertEqual(updated['status'],'review')
        self.assertTrue(list((server.MARKDOWN_ROOT/d['id']/'.historial').glob('*01-hebreo.md')))

    def test_bilingual_preparation_preserves_hebrew_and_physical_lines(self):
        d=self.make_doc()
        u=copy.deepcopy(d['units'][0])
        with patch('server.ask',return_value=({'units':[u]},{})):
            server.prepare(d['id'])
        latest=server.load(d['id'])
        self.assertEqual(latest['units'][0]['hebrew'],'אב גד\nהו זח')
        self.assertEqual(latest['units'][0]['location']['end']['line'],2)
        self.assertIn('Translation',(server.MARKDOWN_ROOT/d['id']/'03-study-en.md').read_text())

    def test_failed_generation_keeps_existing_lesson(self):
        d=self.make_doc()
        wrong=copy.deepcopy(d['units'][0]);wrong['hebrew']='אב'
        with patch('server.ask',return_value=({'units':[wrong]},{})):
            with self.assertRaises(ValueError):server.prepare(d['id'])
        self.assertEqual(server.load(d['id'])['units'],d['units'])

    def test_cross_origin_and_traversal_rejected(self):
        code,_=self.call('/api/upload',{},'https://attacker.example')
        self.assertEqual(code,403)
        code,_=self.call('/api/document?id=../../private')
        self.assertEqual(code,400)

    def test_pipeline_ocr_to_bilingual_guides_without_human_gate(self):
        d=self.make_doc();d['pages'][0].update(hebrew='',raw='',lines=[],approved=False,ocr_done=False);d['units']=[];server.save(d)
        writer=PdfWriter();writer.add_blank_page(width=100,height=100)
        with (server.folder(d['id'])/'original.pdf').open('wb') as f:writer.write(f)
        ocr_result={'raw':'אב גד\nהו זח','hebrew':'אב גד\nהו זח','warnings':[],'lines':[{'column':'right','line':1,'text':'אב גד'},{'column':'right','line':2,'text':'הו זח'}]}
        u={'title':'Uno','title_en':'One','hebrew':'אב גד\nהו זח','translation':'Uno','translation_en':'One','explanation':'Explicación','explanation_en':'Explanation','source_notes':'Pendiente','source_notes_en':'Pending','questions':[],'questions_en':[]}
        with patch('server.ask',side_effect=[(ocr_result,{'id':'mock-ocr'}),({'units':[u]}, {})]):server.process_document(d['id'])
        latest=server.load(d['id'])
        self.assertEqual(latest['status'],'ready')
        self.assertEqual(latest['units'][0]['review_state'],'ai')
        self.assertFalse(latest['pages'][0]['approved'])
        self.assertTrue((server.MARKDOWN_ROOT/d['id']/'02-estudio-es.md').exists())


class OriginalTextMapping(unittest.TestCase):
    def test_concept_can_cross_columns_and_pages(self):
        pages=[{'number':1,'hebrew':'אב גד','lines':[{'column':'left','line':7,'text':'אב גד'}]}, {'number':2,'hebrew':'הו זח','lines':[{'column':'right','line':1,'text':'הו זח'}]}]
        block=source_blocks(pages)[0]
        u=align_units([{'hebrew':'אב גד הו זח'}],block)[0]
        self.assertEqual(u['location']['start'],{'page':1,'column':'left','line':7})
        self.assertEqual(u['location']['end'],{'page':2,'column':'right','line':1})
        self.assertEqual(u['pages'],[1,2])

    def test_missing_and_duplicate_ocr_lines_are_rejected(self):
        with self.assertRaises(ValueError):validate_lines([{'column':'right','line':1,'text':'אב'}],'אב גד')
        with self.assertRaises(ValueError):validate_lines([{'column':'right','line':1,'text':'אב'},{'column':'right','line':1,'text':'גד'}],'אב גד')

    def test_real_seed_cross_column_mapping(self):
        from scripts.seed_lesson import DATA
        self.assertEqual(len(DATA),10)
        self.assertEqual(DATA[7][-4:],('right',15,'left',3))
        self.assertEqual(DATA[9][-4:],('left',5,'left',9))


if __name__=='__main__':unittest.main()
