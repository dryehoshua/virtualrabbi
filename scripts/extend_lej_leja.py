#!/usr/bin/env python3
"""Append reviewed continuation; keep existing units and personal progress."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
DOC_ID='1e7e1e7a202610240000000000000001'

def extend():
    additions=json.loads((server.ROOT/'Estudio/lej-leja/09-continuacion.json').read_text())
    def apply(doc):
        ids={u['id'] for u in doc['units']}
        doc['units'].extend(u for u in additions if u['id'] not in ids)
        doc['coverage']='13 unidades: primer párrafo y comienzo del segundo, hasta «והתענוג הוא למעלה מן החכמה». Continuación parcial: no equivale a una sección álef/bet completa. Seis hojas disponibles para consulta.'
        doc['coverage_en']='13 units: the first paragraph and the beginning of the second, through “והתענוג הוא למעלה מן החכמה”. Partial continuation, not a complete aleph/bet section. Six sheets available for reference.'
    server.update(DOC_ID,apply)

if __name__=='__main__':
    extend()
    print('Continuación instalada sin reiniciar el progreso.')
