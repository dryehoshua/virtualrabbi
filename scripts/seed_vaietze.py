#!/usr/bin/env python3
"""Install the reviewed Vaietzé lessons from the original scan and continuation pages of the edition."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

DOC_ID = '1e7e1e7a202611200000000000000003'


def seed(source, edition):
    from pypdf import PdfReader, PdfWriter

    original = PdfReader(source)
    continuation = PdfReader(edition)
    if len(original.pages) != 1 or len(continuation.pages) < 51:
        raise ValueError('Provide the original scan and the indexed digital edition.')
    target = server.folder(DOC_ID)
    scans = target / 'hojas'
    scans.mkdir(parents=True, exist_ok=True)
    # The original scan is kept first. Edition PDF pages 50–51 follow it.
    writer = PdfWriter()
    writer.add_page(original.pages[0])
    for edition_page in (49, 50):
        writer.add_page(continuation.pages[edition_page])
    combined = target / 'original.pdf'
    writer.write(combined)
    for page in (1, 2, 3):
        subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-scale-to',
                        '1400', '-jpeg', '-singlefile', str(combined),
                        str(scans / f'pagina-{page}')], check=True)
    old = server.load(DOC_ID) if (target / 'documento.json').exists() else {}
    corpus = server.ROOT / 'Estudio/vaietze'
    units = []
    batches = (
        (1, '08-lecciones-01.json', '09-franjas.json'),
        (1, '08-lecciones-02.json', '09-franjas.json'),
        (2, '08-lecciones-03.json', '10-franjas-42.json'),
        (3, '08-lecciones-04.json', '11-franjas-43.json'),
    )
    lesson_rows = []
    for page, name, band_file in batches:
        bands = json.loads((corpus / band_file).read_text())
        lesson_rows.extend((page, bands, unit) for unit in json.loads((corpus / name).read_text()))
    layout = {
        1: ({'right': .500, 'left': .042}, .441, 'כא',
            'Derecha desde ושבתי בשלום; izquierda desde צבאות. / Right starts at ושבתי בשלום; left at צבאות.'),
        2: ({'right': .489, 'left': .067}, .405, '42 (כא ג–ד)',
            'Derecha desde קאי על יצחק; izquierda desde שלום במרומיו, sin contar el título del Biur. / Right starts at קאי על יצחק; left at שלום במרומיו, excluding the Biur heading.'),
        3: ({'right': .524, 'left': .094}, .405, 'כב (כב א–ב)',
            'Derecha desde צוה ישועות יעקב; izquierda desde והשערה עצמה, sin contar el título de la glosa. / Right starts at צוה ישועות יעקב; left at והשערה עצמה, excluding the gloss heading.'),
    }
    for index, (page, bands, unit) in enumerate(lesson_rows, 1):
        units.append(unit)
        biur = unit.get('discourse') == 'biur-veshavti'
        source_id = '5899156' if biur else '5899155'
        left_edge, width, printed_page, basis = layout[page]
        spans = unit.pop('spans', None)
        if spans is None:
            spans = [['right', *unit.pop('lines')]]
        first_column, start, _ = spans[0]
        last_column, _, end = spans[-1]
        regions = []
        for column, low, high in spans:
            for line in range(low, high+1):
                top, bottom = bands[column][line-1]
                regions.append(dict(page=page, column=column, line=line,
                                    left=left_edge[column],
                                    top=(top-2)/1400, width=width, height=(bottom-top+4)/1400))
        unit.update(
            id=f'vaietze-01-{index:02}', pages=[page], discourse=unit.get('discourse', 'veshavti-veshalom'),
            section_end=False, review_state='curated', source_status='primary_text',
            questions=[], questions_en=[], sources=[{
                'title': 'Torá Or · ביאור על הנ״ל · Chabad / Kehot' if biur else 'Torá Or · ושבתי בשלום אל בית אבי · Chabad / Kehot',
                'url': 'https://he.chabad.org/library/article_cdo/aid/' + source_id,
                'kind': 'primary_text', 'checked_at': '2026-11-20'}],
            source_notes='Hebreo transcrito del facsímil y cotejado con Chabad/Kehot. Traducción y comentario de estudio.',
            source_notes_en='Hebrew transcribed from the facsimile and checked against Chabad/Kehot. Study translation and commentary.',
            location={
                'start': dict(page=page, column=first_column, line=start),
                'end': dict(page=page, column=last_column, line=end),
                'printed_page': printed_page,
                'basis': basis},
            regions=regions)
    units[-1]['installment_end'] = True
    first = units[0]
    doc = dict(id=DOC_ID, slug='vaietze', title='Vaietzé · Torá Or',
               title_en='Vayeitzei · Torah Or', author='Rabí Shneur Zalman de Liadí · Alter Rebbe',
               created_at=old.get('created_at', server.now()), filename=source.name,
               status='ready', preparation='curated_primary', units=units,
               pages=[dict(number=page, raw='', hebrew='', approved=False, ocr_done=False,
                           warnings=[]) for page in (1, 2, 3)],
               current_unit=0, completed=[], study_language='es', error='',
               location=first['location']['start'],
               cursor=dict(unit_id=first['id'], phase='hebrew', interrupted=False),
               introduction='Estudiamos el comienzo del maamar sobre el regreso de Yaakov y la piedra que puso como monumento.',
               introduction_en='We study the opening of the discourse on Jacob’s return and the stone he set as a pillar.',
               coverage='Tres hojas de Vaietzé. Primer maamar y resumen completos; el Biur continúa por la hoja כב (22a–b) hasta ובחי׳ זו. Cuarenta y cinco lecciones.',
               coverage_en='Three Vaietzé sheets. The first discourse and summary are complete; the Biur continues through sheet כב (22a–b), ending at ובחי׳ זו. Forty-five lessons.')
    for field in ('current_unit', 'completed', 'study_language', 'location', 'cursor', 'location_unmapped'):
        if field in old:
            doc[field] = old[field]
    server.save(doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('edition', type=Path)
    args = parser.parse_args()
    seed(args.pdf, args.edition)
