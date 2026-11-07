#!/usr/bin/env python3
"""Publish approved five-lesson batches while preserving all personal checkpoints."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

DOC_ID = '1e7e1e7a202611070000000000000002'
BATCHES = ('08-lecciones-01.json', '08-lecciones-02.json')


def reviewed_units():
    units = []
    for name in BATCHES:
        batch = json.loads((server.ROOT / 'Estudio/jaye-sara' / name).read_text())
        if len(batch) != 5:
            raise ValueError('Each approved batch must contain five lessons.')
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
    doc['coverage']='Dos entregas, diez lecciones: hoja PDF 1, página impresa 30, desde la columna derecha, línea 1 (יגלה לן), hasta la columna izquierda, línea 19 (המשכה שמלמעלה דלא יגורך רע כלל). La columna izquierda se cuenta desde ובני מעיים. Cuatro hojas disponibles como facsímil; la parashá y el maamar siguen incompletos. Próxima entrega desde והנה המשכה זו היא בב׳ בחי׳ כפילא וקלישא.'
    doc['coverage_en']='Two installments, ten lessons: PDF sheet 1, printed page 30, from right-column line 1 (יגלה לן) through left-column line 19 (המשכה שמלמעלה דלא יגורך רע כלל). Left-column lines are counted from ובני מעיים. Four facsimile sheets are available; the portion and discourse are not yet complete. The next installment starts at והנה המשכה זו היא בב׳ בחי׳ כפילא וקלישא.'
    for page in doc.get('pages', []):
        page['warnings']=['Facsímil de consulta; sólo las diez lecciones publicadas están preparadas. / Reference facsimile; only the ten published lessons are prepared.']


def extend():
    server.update(DOC_ID, refresh_content)


if __name__ == '__main__':
    extend()
    print('Jayé Sará: lessons 6–10 added; existing progress preserved.')
