#!/usr/bin/env python3
"""Install the reviewed Vaietzé opening from its supplied one-page facsimile."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

DOC_ID = '1e7e1e7a202611200000000000000003'
BANDS = [(330,343),(352,363),(375,385),(397,406),(419,428),(441,450),
         (463,472),(485,494),(507,516),(528,538),(550,560),(572,582),
         (594,604),(616,625),(638,647),(660,669)]


def seed(source):
    target = server.folder(DOC_ID)
    scans = target / 'hojas'
    scans.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-scale-to', '1400',
                    '-jpeg', '-singlefile', str(source), str(scans / 'pagina-1')], check=True)
    shutil.copyfile(source, target / 'original.pdf')
    old = server.load(DOC_ID) if (target / 'documento.json').exists() else {}
    units = json.loads((server.ROOT / 'Estudio/vaietze/08-lecciones-01.json').read_text())
    for index, unit in enumerate(units, 1):
        start, end = unit.pop('lines')
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
                'start': dict(page=1, column='right', line=start),
                'end': dict(page=1, column='right', line=end),
                'printed_page': 'כא',
                'basis': 'Líneas contadas desde ושבתי בשלום; las franjas cubren líneas completas. / Lines counted from ושבתי בשלום; highlights cover whole lines.'},
            regions=[dict(page=1, column='right', line=line, left=.500,
                          top=(BANDS[line-1][0]-2)/1400, width=.445,
                          height=(BANDS[line-1][1]-BANDS[line-1][0]+4)/1400)
                     for line in range(start, end+1)])
    units[-1]['installment_end'] = True
    first = units[0]
    doc = dict(id=DOC_ID, slug='vaietze', title='Vaietzé · Torá Or',
               title_en='Vayeitzei · Torah Or', author='Rabí Shneur Zalman de Liadí · Alter Rebbe',
               created_at=old.get('created_at', server.now()), filename=source.name,
               status='ready', preparation='curated_primary', units=units,
               pages=[dict(number=1, raw='', hebrew='', approved=False, ocr_done=False,
                           warnings=['Preparadas las primeras 16 líneas de la columna derecha. / The first 16 right-column lines are prepared.'])],
               current_unit=0, completed=[], study_language='es', error='',
               location=first['location']['start'],
               cursor=dict(unit_id=first['id'], phase='hebrew', interrupted=False),
               introduction='Estudiamos el comienzo del maamar sobre el regreso de Yaakov y la piedra que puso como monumento.',
               introduction_en='We study the opening of the discourse on Jacob’s return and the stone he set as a pillar.',
               coverage='Cinco lecciones iniciales de «ושבתי בשלום אל בית אבי». Hoja 1, página impresa כא, columna derecha, líneas 1–16 desde ושבתי בשלום. El maamar continúa.',
               coverage_en='Five opening lessons of “Veshavti Veshalom el Beit Avi.” Sheet 1, printed page כא, right column, lines 1–16 from ושבתי בשלום. The discourse continues.')
    for field in ('current_unit', 'completed', 'study_language', 'location', 'cursor', 'location_unmapped'):
        if field in old:
            doc[field] = old[field]
    server.save(doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    seed(parser.parse_args().pdf)
