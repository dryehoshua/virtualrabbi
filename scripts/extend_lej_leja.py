#!/usr/bin/env python3
"""Append reviewed continuation; keep existing units and personal progress."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
DOC_ID='1e7e1e7a202610240000000000000001'
CONTINUATIONS=('09-continuacion.json', '10-hoja-2.json', '11-hoja-3.json', '13-hoja-4.json')

def additions():
    return [unit for name in CONTINUATIONS for unit in json.loads((server.ROOT/'Estudio/lej-leja'/name).read_text())]

def extend():
    new_units=additions()
    revisions=json.loads((server.ROOT/'Estudio/lej-leja/12-notas-revisadas.json').read_text())
    def apply(doc):
        ids={u['id'] for u in doc['units']}
        doc['units'].extend(u for u in new_units if u['id'] not in ids)
        for unit in doc['units']:
            unit.update(revisions.get(unit['id'], {}))
            if unit['id']=='lej-leja-01-28':
                unit['continues_to_unit']='lej-leja-01-29'
            if unit['id']=='lej-leja-01-45':
                unit['continues_to_unit']='lej-leja-01-46'
        doc['coverage']='62 unidades bilingües: maamar de la hoja 1 y hojas 2, 3 y 4 completas. Incluye «ענין לך לך», «אנכי מגן לך» y «ולא יקרא עוד שמך אברם» completos, y el comienzo de «והבדילה הפרוכת». La unidad 62 continúa en la hoja 5, aún pendiente; el cambio de hoja no equivale a un cierre de sección. Seis hojas disponibles para consulta.'
        doc['coverage_en']='62 bilingual units: the discourse on sheet 1 and complete sheets 2, 3 and 4. Includes all of “ענין לך לך”, “אנכי מגן לך” and “ולא יקרא עוד שמך אברם”, and the beginning of “והבדילה הפרוכת”. Unit 62 continues on sheet 5, still awaiting preparation; a page boundary is not a section ending. Six sheets available for reference.'
    server.update(DOC_ID,apply)

if __name__=='__main__':
    extend()
    print('Continuación instalada sin reiniciar el progreso.')
