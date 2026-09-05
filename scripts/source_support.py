"""Source-image and translation contracts for the offline reader.

Structural checks do not prove translation accuracy or the author's reasoning.
No OCR, remote requests, repository code, or translation model is executed here.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r'^[A-Za-z0-9_.-]+$')
SHA256 = re.compile(r'^[a-f0-9]{64}$')
BLOCK_TYPES = {'paragraph', 'heading', 'equation', 'code', 'pairs', 'table'}


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_box(value: Any) -> bool:
    return (isinstance(value, list) and len(value) == 4
            and all(isinstance(x, (float, int)) and not isinstance(x, bool)
                    and math.isfinite(x) for x in value)
            and value[2] > value[0] and value[3] > value[1])


def validate_sources(data: dict, source_pdf: Path | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    screenshots = data.get('screenshots', {})
    translations = data.get('screenshot_translations', {})
    images = data.get('images', {})
    sizes = data.get('sizes', {})
    layer = data.get('source_layer', {})
    provenance = data.get('screenshot_provenance', {})
    strict = data.get('schema_version') == '1.2'
    translated = 0
    references_count = 0
    missing_refs: list[str] = []
    missing_translations: list[str] = []
    hash_checked = False
    if not isinstance(screenshots, dict):
        errors.append('screenshots must be an object keyed by stable region IDs')
        screenshots = {}
    if not isinstance(translations, dict):
        errors.append('screenshot_translations must be an object keyed by region ID')
        translations = {}
    if not isinstance(images, dict):
        images = {}
    if not isinstance(sizes, dict):
        sizes = {}
    if not isinstance(layer, dict):
        errors.append('source_layer must be an object')
        layer = {}
    status = layer.get('status')
    if strict:
        if status not in {'provided', 'partial', 'unavailable', 'not-requested'}:
            errors.append('source_layer.status must be provided, partial, unavailable, or not-requested')
        if status != 'provided' and not text(layer.get('reason')):
            errors.append('source_layer.reason must explain any partial, unavailable or declined source layer')
        if status == 'provided' and not screenshots:
            errors.append('source_layer: provided requires actual screenshot regions')
    if not isinstance(provenance, dict):
        errors.append('screenshot_provenance must be an object')
        provenance = {}
    source_hash = provenance.get('source_sha256', '')
    page_count = provenance.get('page_count')
    if screenshots:
        if not isinstance(source_hash, str) or not SHA256.fullmatch(source_hash):
            errors.append('screenshot_provenance.source_sha256: actual source PDF hash required')
        if not isinstance(page_count, int) or isinstance(page_count, bool) or page_count < 1:
            errors.append('screenshot_provenance.page_count: positive PDF page count required')
        for k in ['source_filename', 'crop_coordinate_system']:
            if not text(provenance.get(k)):
                errors.append(f'screenshot_provenance.{k}: nonempty text required')
    if source_pdf is not None:
        try:
            actual_hash = hashlib.sha256(source_pdf.read_bytes()).hexdigest()
            if source_hash != actual_hash:
                errors.append('source PDF SHA256 does not match screenshot provenance')
            else:
                hash_checked = True
        except OSError as exc:
            errors.append(f'cannot read source PDF: {exc}')
    for rid, shot in screenshots.items():
        loc = f'screenshots[{rid}]'
        if not isinstance(rid, str) or not ID.fullmatch(rid):
            errors.append(f'{loc}: safe stable ID required')
        if not isinstance(shot, dict):
            errors.append(f'{loc}: object required')
            continue
        if shot.get('id', rid) != rid:
            errors.append(f'{loc}.id differs from its dictionary key')
        if not text(shot.get('title')):
            errors.append(f'{loc}.title: source location/title required')
        page = shot.get('page')
        if not isinstance(page, int) or isinstance(page, bool) or page < 1:
            errors.append(f'{loc}.page: use a positive 1-indexed PDF page number')
        elif isinstance(page_count, int) and page > page_count:
            errors.append(f'{loc}.page exceeds source PDF page count')
        if str(page) not in images or str(page) not in sizes:
            errors.append(f'{loc}: full-page image and point dimensions are missing')
        box = shot.get('clip')
        size = sizes.get(str(page))
        if not valid_box(box):
            errors.append(f'{loc}.clip: finite [x0,y0,x1,y1] rectangle required')
        elif (isinstance(size, list) and len(size) == 2
              and all(isinstance(x, (int, float)) for x in size)
              and (box[0] < 0 or box[1] < 0 or box[2] > size[0] or box[3] > size[1])):
            errors.append(f'{loc}.clip lies outside the recorded source page')
        if rid not in translations:
            missing_translations.append(rid)
    # Decode raster headers, not merely a data-URI-shaped string.
    for page, uri in images.items():
        try:
            prefix, payload = uri.split(',', 1)
            raw = base64.b64decode(payload.replace('\n', '').replace('\r', ''), validate=True)
            good = ((prefix == 'data:image/png;base64' and raw.startswith(b'\x89PNG\r\n\x1a\n'))
                    or (prefix == 'data:image/webp;base64' and raw[:4] == b'RIFF' and raw[8:12] == b'WEBP')
                    or (prefix == 'data:image/jpeg;base64' and raw.startswith(b'\xff\xd8\xff')))
            if not good and (screenshots or strict):
                errors.append(f'images[{page}]: MIME and raster file header disagree')
            recorded = provenance.get('page_sha256', {}).get(str(page))
            if recorded and hashlib.sha256(raw).hexdigest() != recorded:
                errors.append(f'images[{page}]: image hash differs from rendering manifest')
        except (AttributeError, ValueError, TypeError):
            errors.append(f'images[{page}]: malformed embedded image')
    for rid, tr in translations.items():
        loc = f'screenshot_translations[{rid}]'
        if rid not in screenshots:
            errors.append(f'{loc}: no source screenshot with this ID')
            continue
        if not isinstance(tr, dict):
            errors.append(f'{loc}: object required')
            continue
        if tr.get('status') == 'unavailable':
            if not text(tr.get('reason')):
                errors.append(f'{loc}.reason: explain why the region cannot be translated')
            missing_translations.append(rid)
            continue
        if tr.get('status', 'translated') != 'translated':
            errors.append(f'{loc}.status must be translated or unavailable')
        if not text(tr.get('title_target', tr.get('title_zh'))):
            errors.append(f'{loc}.title_target: translated region title required')
        source = tr.get('source', {})
        if not isinstance(source, dict):
            errors.append(f'{loc}.source: source binding required')
            source = {}
        shot = screenshots[rid]
        if isinstance(shot, dict):
            for key, expected in [('screenshot_id', rid), ('pdf_page', shot.get('page')),
                                  ('clip_pdf_points', shot.get('clip')), ('pdf_sha256', source_hash)]:
                if source.get(key) != expected:
                    errors.append(f'{loc}.source.{key}: does not match the screenshot source')
        blocks = tr.get('blocks')
        if not isinstance(blocks, list) or not blocks:
            errors.append(f'{loc}.blocks: nonempty translated content required; a summary is not a translation')
            blocks = []
        else:
            translated += 1
        for bi, b in enumerate(blocks):
            bloc = f'{loc}.blocks[{bi}]'
            if not isinstance(b, dict) or b.get('type') not in BLOCK_TYPES:
                errors.append(f'{bloc}: unsupported translation block')
                continue
            kind = b['type']
            if kind in {'paragraph', 'heading', 'equation', 'code'}:
                if not text(b.get('text')):
                    errors.append(f'{bloc}.text: nonempty translated text required')
            else:
                headers = ['source', 'translation'] if kind == 'pairs' else b.get('headers')
                rows = b.get('rows')
                if not isinstance(headers, list) or not headers or not all(text(h) for h in headers):
                    errors.append(f'{bloc}.headers: nonempty header strings required')
                    headers = []
                if kind == 'pairs' and not text(b.get('title')):
                    errors.append(f'{bloc}.title: label the figure/table text being translated')
                if not isinstance(rows, list) or not rows:
                    errors.append(f'{bloc}.rows: nonempty table required')
                else:
                    for ri, row in enumerate(rows):
                        if not isinstance(row, list) or len(row) != len(headers) or not all(isinstance(c, str) for c in row):
                            errors.append(f'{bloc}.rows[{ri}]: preserve a rectangular table of string cells')
        for field in ['notes', 'related_ids']:
            value = tr.get(field, [])
            if not isinstance(value, list) or not all(text(x) for x in value):
                errors.append(f'{loc}.{field}: list of nonempty strings required')
        for other in tr.get('related_ids', []) if isinstance(tr.get('related_ids', []), list) else []:
            if isinstance(other, str) and other not in screenshots:
                errors.append(f'{loc}.related_ids: unknown continuation screenshot {other}')
    references: list[tuple[str, dict]] = []
    points = data.get('paperPoints', [])
    for i, p in enumerate(points if isinstance(points, list) else []):
        if isinstance(p, dict):
            references.append((f'paperPoints[{i}]', p))
    argument = data.get('argument') or {}
    if isinstance(argument, dict):
        nodes = argument.get('nodes', [])
        for i, n in enumerate(nodes if isinstance(nodes, list) else []):
            if not isinstance(n, dict):
                continue
            refs = n.get('references', [])
            for j, ref in enumerate(refs if isinstance(refs, list) else []):
                if isinstance(ref, dict):
                    references.append((f'argument.nodes[{i}].references[{j}]', ref))
    for loc, ref in references:
        refs = ref.get('shot_ids', [])
        if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
            errors.append(f'{loc}.shot_ids: array of screenshot IDs required')
            continue
        references_count += len(refs)
        if not refs:
            missing_refs.append(loc)
        for rid in refs:
            if rid not in screenshots:
                errors.append(f'{loc}.shot_ids: unknown source screenshot {rid}')
        if refs and all(r in screenshots and isinstance(screenshots[r], dict) for r in refs):
            if ref.get('page') not in {screenshots[r].get('page') for r in refs}:
                errors.append(f'{loc}: primary PDF page must occur in the cited screenshot set')
    if strict and status == 'provided':
        if missing_refs:
            errors.append('source_layer provided but these paper locations lack screenshots: ' + ', '.join(missing_refs))
        if missing_translations:
            errors.append('source_layer provided but these screenshots lack translations: ' + ', '.join(missing_translations))
    elif missing_translations or (strict and missing_refs):
        warnings.append('Partial source/translation coverage; display the recorded reason and never claim full coverage.')
    if screenshots and not hash_checked:
        warnings.append('Source PDF hash was not checked against local PDF bytes in this build.')
    return {'errors': errors, 'warnings': warnings, 'screenshot_regions': len(screenshots),
            'translated_regions': translated, 'screenshot_references': references_count,
            'missing_screenshot_locations': missing_refs, 'missing_translations': missing_translations,
            'source_pdf_hash_checked': hash_checked,
            'translation_semantics_checked': False, 'source_pixels_reverified': False}


def ui_for(data: dict) -> tuple[dict, dict]:
    """Build generic UI messages from trusted locale assets, never a demo's constants."""
    lang = data.get('language', 'zh-CN')
    payload = json.loads((ROOT / 'assets/source-ui.json').read_text(encoding='utf-8'))[lang]
    src, tr = payload['source'], payload['translation']
    shots = data.get('screenshots', {})
    translations = data.get('screenshot_translations', {})
    count = sum(isinstance(t, dict) and bool(t.get('blocks')) and t.get('status') != 'unavailable' for t in translations.values())
    vals = {'regions': str(len(shots)), 'translated': str(count),
            'version': str(data.get('paper', {}).get('version') or ''),
            'target': str(data.get('source_layer', {}).get('translation_language', 'zh-CN'))}
    for ui in [src, tr]:
        for key, value in ui.items():
            for name, replacement in vals.items():
                value = value.replace('{'+name+'}', replacement)
            ui[key] = value
    return src, tr
