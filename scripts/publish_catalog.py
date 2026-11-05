#!/usr/bin/env python3
"""Publish only curated teaching content, never the operator's personal state."""
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
from public_server import CATALOG

DOC_ID = '1e7e1e7a202610240000000000000001'
CONTENT_FIELDS = ('id', 'slug', 'title', 'title_en', 'author', 'created_at', 'units', 'pages', 'introduction', 'introduction_en', 'coverage', 'coverage_en', 'preparation')


def publish():
    source = server.DATA / DOC_ID
    original = json.loads((source / 'documento.json').read_text())
    if original.get('preparation') != 'curated_primary' or not original.get('units'):
        raise ValueError('Only reviewed primary-source lessons can be published.')
    doc = {k: original[k] for k in CONTENT_FIELDS if k in original}
    first = doc['units'][0]
    doc.update(status='ready', updated_at=server.now(), current_unit=0, completed=[], study_language='es', location=first['location']['start'], location_unmapped=False, cursor={'unit_id': first['id'], 'phase': 'hebrew', 'interrupted': False}, error='')
    destination = CATALOG / DOC_ID
    destination.mkdir(parents=True, exist_ok=True)
    server.dump(destination / 'documento.json', doc)
    for name in ('original.pdf', 'guia-estudio-es.md', 'guia-estudio-en.md', 'hebreo-revisado.txt', 'exegesis.md'):
        shutil.copyfile(source / name, destination / name)
    (destination / 'hojas').mkdir(exist_ok=True)
    for page in doc['pages']:
        name = f"pagina-{page['number']}.jpg"
        image = source / 'hojas' / name
        if not image.is_file():
            raise ValueError(f'Render the original sheet first: {name}')
        shutil.copyfile(image, destination / 'hojas' / name)
    print(f'Public catalog: {len(doc["units"])} units; personal progress and conversations excluded.')


if __name__ == '__main__':
    publish()
