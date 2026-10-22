#!/usr/bin/env python3
"""Append reviewed continuation; keep existing units and personal progress."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
DOC_ID='1e7e1e7a202610240000000000000001'
CONTINUATIONS=('09-continuacion.json', '10-hoja-2.json')

def additions():
    return [unit for name in CONTINUATIONS for unit in json.loads((server.ROOT/'Estudio/lej-leja'/name).read_text())]

def extend():
    new_units=additions()
    def apply(doc):
        ids={u['id'] for u in doc['units']}
        doc['units'].extend(u for u in new_units if u['id'] not in ids)
        doc['coverage']='28 unidades bilingües: texto del maamar de la hoja 1 y toda la hoja 2 (página impresa 22), hasta «מן שכל הנעלם». El último párrafo continúa en la hoja 3, aún pendiente de preparación; no es cierre de sección álef/bet ni del maamar. Seis hojas disponibles para consulta.'
        doc['coverage_en']='28 bilingual units: the discourse on sheet 1 and all of sheet 2 (printed page 22), through “מן שכל הנעלם”. The last paragraph continues on sheet 3, still awaiting preparation; this is not an aleph/bet section ending or the end of the discourse. Six sheets available for reference.'
    server.update(DOC_ID,apply)

if __name__=='__main__':
    extend()
    print('Continuación instalada sin reiniciar el progreso.')
