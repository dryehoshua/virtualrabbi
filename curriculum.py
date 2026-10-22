"""Pure study transformations: bilingual material and original-text locations."""
import re

PHASES = ('introduction', 'hebrew', 'translation', 'explanation', 'pause')


def compact(text):
    return re.sub(r'\s+', '', text)


def validate_lines(lines, hebrew):
    if not isinstance(lines, list) or not lines:
        raise ValueError('La IA no entregó las líneas de la página. Reintenta OCR.')
    seen = set()
    for line in lines:
        if line.get('column') not in ('right', 'left', 'single') or type(line.get('line')) is not int or line['line'] < 1 or not isinstance(line.get('text'), str):
            raise ValueError('Ubicación de línea no válida en el OCR.')
        identity = (line['column'], line['line'])
        if identity in seen:
            raise ValueError('El OCR repitió una ubicación de línea.')
        seen.add(identity)
    if compact(''.join(line['text'] for line in lines)) != compact(hebrew):
        raise ValueError('El texto y las líneas del OCR no coinciden. El PDF sigue intacto; reintenta.')
    return lines


def source_blocks(pages, max_chars=5500):
    """Keep physical line locations, allow concepts to cross page/column boundaries."""
    blocks = []
    current = {'text': '', 'lines': []}
    for page in pages:
        lines = page.get('lines') or [{'column': 'single', 'line': None, 'text': page['hebrew']}]
        for line in lines:
            if len(current['text']) > max_chars and current['lines']:
                blocks.append(current)
                current = {'text': '', 'lines': []}
            start = len(current['text'])
            current['text'] += line['text'] + '\n'
            current['lines'].append({'start': start, 'end': len(current['text']), 'page': page['number'], 'column': line['column'], 'line': line['line']})
    if current['text'].strip():
        blocks.append(current)
    return blocks


def align_units(proposed, block):
    """Reject rewrites/omissions; replace AI spacing with exact source spans."""
    source = block['text']
    if not proposed or compact(''.join(u.get('hebrew', '') for u in proposed)) != compact(source):
        raise ValueError('La IA modificó u omitió hebreo al dividirlo. El original sigue intacto; reintenta.')
    positions = [i for i, char in enumerate(source) if not char.isspace()]
    consumed = 0
    start = 0
    for i, unit in enumerate(proposed):
        length = len(compact(unit.get('hebrew', '')))
        if length == 0:
            raise ValueError('No se permite una unidad hebrea vacía.')
        end = positions[consumed+length-1]+1
        if i == len(proposed)-1:
            end = len(source)
        unit['hebrew'] = source[start:end].strip()
        touched = [l for l in block['lines'] if l['start'] < end and l['end'] > start and source[max(start, l['start']):min(end, l['end'])].strip()]
        first, last = touched[0], touched[-1]
        unit['location'] = {'start': {k:first[k] for k in ('page','column','line')}, 'end': {k:last[k] for k in ('page','column','line')}, 'basis': 'AI page transcription; review available'}
        unit['pages'] = sorted(set(l['page'] for l in touched))
        consumed += length
        start = end
    return proposed


def localized(unit, field, language='es'):
    if language == 'en':
        return unit.get(field+'_en', unit.get(field, ''))
    return unit.get(field, '')


def location_matches(unit, location):
    """Known reviewed line range only; do not infer a line for unlocated text."""
    loc = unit.get('location') or {}
    start, end = loc.get('start', {}), loc.get('end', {})
    if not start.get('line') or not end.get('line'):
        return False
    def key(p):
        return (p.get('page', 0), {'right':0, 'single':0, 'left':1}.get(p.get('column'), 0), p.get('line') or 0)
    return key(start) <= key(location) <= key(end)
