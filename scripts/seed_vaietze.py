#!/usr/bin/env python3
"""Install the reviewed Vaietzé lessons from its supplied one-page facsimile."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

DOC_ID = '1e7e1e7a202611200000000000000003'


def seed(source):
    target = server.folder(DOC_ID)
    scans = target / 'hojas'
    scans.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-scale-to', '1400',
                    '-jpeg', '-singlefile', str(source), str(scans / 'pagina-1')], check=True)
    shutil.copyfile(source, target / 'original.pdf')
    old = server.load(DOC_ID) if (target / 'documento.json').exists() else {}
    corpus = server.ROOT / 'Estudio/vaietze'
    units = []
    for name in ('08-lecciones-01.json', '08-lecciones-02.json'):
        units.extend(json.loads((corpus / name).read_text()))
    bands = json.loads((corpus / '09-franjas.json').read_text())
    for index, unit in enumerate(units, 1):
        spans = unit.pop('spans', None)
        if spans is None:
            spans = [['right', *unit.pop('lines')]]
        first_column, start, _ = spans[0]
        last_column, _, end = spans[-1]
        regions = []
        for column, low, high in spans:
            for line in range(low, high+1):
                top, bottom = bands[column][line-1]
                regions.append(dict(page=1, column=column, line=line,
                                    left=.500 if column=='right' else .042,
                                    top=(top-2)/1400, width=.441, height=(bottom-top+4)/1400))
        unit.update(
            id=f'vaietze-01-{index:02}', pages=[1], discourse='veshavti-veshalom',
            section_end=False, review_state='curated', source_status='primary_text',
            questions=[], questions_en=[], sources=[{
                'title': 'Torá Or · ושבתי בשלום אל בית אבי · Chabad / Kehot',
                'url': 'https://he.chabad.org/library/article_cdo/aid/5899155',
                'kind': 'primary_text', 'checked_at': '2026-11-20'}],
            source_notes='Hebreo transcrito del facsímil y cotejado con Chabad/Kehot. Traducción y comentario de estudio.',
            source_notes_en='Hebrew transcribed from the facsimile and checked against Chabad/Kehot. Study translation and commentary.',
            location={
                'start': dict(page=1, column=first_column, line=start),
                'end': dict(page=1, column=last_column, line=end),
                'printed_page': 'כא',
                'basis': 'Derecha desde ושבתי בשלום; izquierda desde צבאות. / Right starts at ושבתי בשלום; left at צבאות.'},
            regions=regions)
    units[-1]['installment_end'] = True
    first = units[0]
    doc = dict(id=DOC_ID, slug='vaietze', title='Vaietzé · Torá Or',
               title_en='Vayeitzei · Torah Or', author='Rabí Shneur Zalman de Liadí · Alter Rebbe',
               created_at=old.get('created_at', server.now()), filename=source.name,
               status='ready', preparation='curated_primary', units=units,
               pages=[dict(number=1, raw='', hebrew='', approved=False, ocr_done=False,
                           warnings=['Texto de Vaietzé de ambas columnas. / Vaietzé text in both columns.'])],
               current_unit=0, completed=[], study_language='es', error='',
               location=first['location']['start'],
               cursor=dict(unit_id=first['id'], phase='hebrew', interrupted=False),
               introduction='Estudiamos el comienzo del maamar sobre el regreso de Yaakov y la piedra que puso como monumento.',
               introduction_en='We study the opening of the discourse on Jacob’s return and the stone he set as a pillar.',
               coverage='«ושבתי בשלום אל בית אבי», página impresa כא. Se cubre el texto de Vaietzé de la hoja aportada, desde ושבתי בשלום hasta כי הנה אבי. El maamar continúa en la hoja siguiente.',
               coverage_en='“Veshavti Veshalom el Beit Avi,” printed page כא. Covers the Vaietzé text of the supplied sheet, from ושבתי בשלום through כי הנה אבי. The discourse continues on the next sheet.')
    for field in ('current_unit', 'completed', 'study_language', 'location', 'cursor', 'location_unmapped'):
        if field in old:
            doc[field] = old[field]
    server.save(doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    seed(parser.parse_args().pdf)
