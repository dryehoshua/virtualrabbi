#!/usr/bin/env python3
"""Publish reviewed installments while preserving all personal checkpoints."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

DOC_ID = '1e7e1e7a202611070000000000000002'
BATCHES = ('08-lecciones-01.json', '08-lecciones-02.json', '08-lecciones-03.json')


def reviewed_units():
    units = []
    for name, expected_count in zip(BATCHES, (5, 5, 4)):
        batch = json.loads((server.ROOT / 'Estudio/jaye-sara' / name).read_text())
        if len(batch) != expected_count:
            raise ValueError('Unexpected lesson count in reviewed installment.')
        units.extend(batch)
    if [u['id'] for u in units] != [f'jaye-sara-01-{i:02}' for i in range(1, len(units)+1)]:
        raise ValueError('Lesson IDs must be consecutive and unique.')
    return units


def refresh_content(doc):
    existing = {u['id'] for u in doc['units']}
    doc['units'].extend(u for u in reviewed_units() if u['id'] not in existing)
    fifth = next(u for u in doc['units'] if u['id'] == 'jaye-sara-01-05')
    fifth.update(installment_end=False, continues_to_unit='jaye-sara-01-06',
        explanation='La elevación de los mundos en Shabat permite recibir la vitalidad del alimento desde su raíz superior. El maamar vincula esta hamshajá con los doce panes y con «saciar su alma». La siguiente lección desarrolla el contraste con la otra forma de comer.',
        explanation_en='The ascent of the worlds on Shabbat enables the vitality of food to be received from its higher root. The discourse connects this hamshachah with the twelve loaves and “satisfying his soul.” The next lesson develops the contrast with the other form of eating.')
    for current, following in zip(doc['units'], doc['units'][1:]):
        current['installment_end'] = False
        current['continues_to_unit'] = following['id']
        current.pop('next_source_text', None)
    doc['coverage']='Maamar «ענין שדה המכפלה» completo en 14 lecciones: hoja PDF 1, página impresa 30, desde la columna derecha, línea 1 (יגלה לן), hasta la columna izquierda, línea 33 (ההוא יהיה כו׳). La izquierda se cuenta desde ובני מעיים. Se excluye Vayerá, impreso arriba. Las hojas 2–4 son de consulta y contienen otros discursos todavía no preparados; no está completa toda la parashá.'
    doc['coverage_en']='The complete discourse “Inyan sedeh haMachpelah” in 14 lessons: PDF sheet 1, printed page 30, from right-column line 1 (יגלה לן) through left-column line 33 (ההוא יהיה כו׳). Left-column lines are counted from ובני מעיים. Vayera, printed above, is excluded. Sheets 2–4 are for reference and contain other discourses not yet prepared; the entire Torah portion is not complete.'
    for page in doc.get('pages', []):
        page['warnings']=['El primer maamar está completo en 14 lecciones; los demás discursos son sólo de consulta. / The first discourse is complete in 14 lessons; the other discourses are for reference only.']


def extend():
    server.update(DOC_ID, refresh_content)


if __name__ == '__main__':
    extend()
    print('Jayé Sará: first discourse complete in 14 lessons; existing progress preserved.')
