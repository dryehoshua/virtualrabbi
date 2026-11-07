#!/usr/bin/env python3
"""Install all approved Chayei Sarah batches without resetting reader progress."""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
from extend_jaye_sara import reviewed_units, refresh_content

DOC_ID = '1e7e1e7a202611070000000000000002'


def seed(source):
    import pymupdf
    units = reviewed_units()
    target = server.folder(DOC_ID)
    target.mkdir(parents=True, exist_ok=True)
    pdf = pymupdf.open(source)
    if len(pdf) != 4:
        raise ValueError('Expected the supplied four-sheet Chayei Sarah PDF.')
    shutil.copyfile(source, target / 'original.pdf')
    (target / 'hojas').mkdir(exist_ok=True)
    for i, page in enumerate(pdf):
        page.get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(target / 'hojas' / f'pagina-{i+1}.jpg')
    old = json.loads((target / 'documento.json').read_text()) if (target / 'documento.json').exists() else {}
    first = units[0]
    doc = dict(id=DOC_ID, slug='jaye-sara', title='Jayé Sará · Torá Or', title_en='Chayei Sarah · Torah Or',
               author='Rabí Shneur Zalman de Liadí · Alter Rebbe', created_at=old.get('created_at', server.now()),
               filename='Torah Or -Jayeh Sarah.pdf', status='ready', preparation='curated_primary',
               units=units, pages=[dict(number=i+1, raw='', hebrew='', approved=False, ocr_done=False,
               warnings=['Facsímil de consulta; sólo las cinco lecciones publicadas están transcritas y preparadas. / Reference scan; only the five published lessons are transcribed and prepared.']) for i in range(4)],
               current_unit=0, completed=[], study_language='es', error='', location=first['location']['start'],
               cursor=dict(unit_id=first['id'], phase='hebrew', interrupted=False),
               introduction='Estudiamos el comienzo de «Inyán sedé haMajpelá», de Torá Or. El Alter Rebbe relaciona la duplicación de la letra he con la alimentación, el birur cotidiano y la vitalidad que desciende en Shabat.',
               introduction_en='We study the opening of “Inyan sedeh haMachpelah” in Torah Or. The Alter Rebbe connects the doubling of the letter he with eating, weekday birur and the vitality drawn down on Shabbat.',
               coverage='Entrega 01: cinco lecciones; hoja PDF 1, página impresa 30, columna derecha, líneas 1–22 desde יגלה לן. Termina en חיות הנפש הבאה מלמעלה. Las cuatro hojas se conservan para consulta; no se presentan como completamente preparadas. El texto superior de la primera hoja pertenece a Vayerá. El maamar continúa; la siguiente entrega empieza en ובטן רשעים כו׳.',
               coverage_en='Installment 01: five lessons; PDF sheet 1, printed page 30, right column, lines 1–22 counted from יגלה לן. Ends at חיות הנפש הבאה מלמעלה. All four sheets are retained for reference, not claimed as fully prepared. The upper text on the first sheet belongs to Vayera. The discourse continues; the next installment begins at ובטן רשעים כו׳.')
    for field in ('current_unit', 'completed', 'study_language', 'location', 'cursor', 'location_unmapped'):
        if field in old:
            doc[field] = old[field]
    refresh_content(doc)
    server.save(doc)
    print(f'Jayé Sará: {len(doc["units"])} bilingual units installed; existing progress preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf', type=Path)
    seed(parser.parse_args().pdf)
