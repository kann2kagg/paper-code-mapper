#!/usr/bin/env python3
"""Render real PDF page pixels and region manifests. Never OCR or translate.

Requires PyMuPDF and Pillow. Default: all pages for <=20-page PDFs, otherwise
only pages containing selected regions. Coordinates use displayed page points,
origin at top left. Visual review of the chosen rectangles remains mandatory.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import sys


def render_sources(pdf: Path, regions_file: Path, output_dir: Path, dpi: int = 200,
                   page_mode: str = 'auto') -> dict:
    if not 96 <= dpi <= 400:
        raise ValueError('dpi must be between 96 and 400')
    if page_mode not in {'auto', 'all', 'referenced'}:
        raise ValueError('pages must be auto, all, or referenced')
    try:
        import fitz
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('PDF rendering requires PyMuPDF and Pillow; neither is installed automatically') from exc
    raw_regions = json.loads(regions_file.read_text(encoding='utf-8'))
    entries = raw_regions.get('regions') if isinstance(raw_regions, dict) else raw_regions
    if isinstance(entries, dict):
        entries = [dict(v, id=k) for k, v in entries.items()]
    if not isinstance(entries, list) or not entries:
        raise ValueError('regions JSON must contain a nonempty array or a regions mapping')
    from source_support import valid_box
    pdf = pdf.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    shots: dict = {}
    with fitz.open(pdf) as doc:
        if doc.needs_pass:
            raise ValueError('encrypted PDF needs authorized decryption before rendering')
        for index, r in enumerate(entries):
            if not isinstance(r, dict):
                raise ValueError(f'region {index} must be an object')
            rid = r.get('id')
            if not isinstance(rid, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', rid) or rid in shots:
                raise ValueError(f'region {index} needs a unique safe id')
            page = r.get('page')
            if not isinstance(page, int) or isinstance(page, bool) or not 1 <= page <= len(doc):
                raise ValueError(f'{rid}: page must be a 1-indexed page within this PDF')
            clip = r.get('clip')
            size = doc[page-1].rect
            if (not valid_box(clip) or clip[0] < 0 or clip[1] < 0
                    or clip[2] > size.width or clip[3] > size.height):
                raise ValueError(f'{rid}: clip must lie entirely within the displayed page rectangle')
            if not isinstance(r.get('title'), str) or not r['title'].strip():
                raise ValueError(f'{rid}: source location/title required')
            shots[rid] = {'id': rid, 'page': page, 'title': r['title'], 'clip': clip,
                          'note': str(r.get('note', ''))}
        referenced = sorted({r['page'] for r in shots.values()})
        pages = list(range(1, len(doc)+1)) if page_mode == 'all' or (page_mode == 'auto' and len(doc) <= 20) else referenced
        images, sizes, hashes, pixels, rotations = {}, {}, {}, {}, {}
        (output_dir/'pages').mkdir(exist_ok=True)
        (output_dir/'regions').mkdir(exist_ok=True)
        for p in pages:
            page = doc[p-1]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), colorspace=fitz.csRGB, alpha=False)
            im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            buffer = io.BytesIO()
            im.save(buffer, 'WEBP', lossless=True, method=4)
            raw = buffer.getvalue()
            page_file = output_dir/'pages'/f'page_{p:03d}.webp'
            page_file.write_bytes(raw)
            images[str(p)] = 'data:image/webp;base64,'+base64.b64encode(raw).decode('ascii')
            sizes[str(p)] = [page.rect.width, page.rect.height]
            hashes[str(p)] = hashlib.sha256(raw).hexdigest()
            pixels[str(p)] = [pix.width, pix.height]
            rotations[str(p)] = page.rotation
            for shot in shots.values():
                if shot['page'] != p:
                    continue
                c = shot['clip']
                # Match SVG viewBox scaling. Crop coordinates stay in PDF points.
                sx, sy = pix.width/page.rect.width, pix.height/page.rect.height
                crop = im.crop((int(c[0]*sx), int(c[1]*sy), min(pix.width, int(c[2]*sx+0.999)),
                                min(pix.height, int(c[3]*sy+0.999))))
                rel = Path('regions')/(shot['id']+'.png')
                crop.save(output_dir/rel)
                shot['crop_file'] = rel.as_posix()
                shot['crop_sha256'] = hashlib.sha256((output_dir/rel).read_bytes()).hexdigest()
        provenance = {
            'source_filename': pdf.name,
            'source_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
            'page_count': len(doc), 'rendered_pages': pages,
            'render_dpi': dpi, 'format': 'lossless WebP', 'page_sha256': hashes,
            'pixel_dimensions_by_page': pixels, 'page_rotations': rotations,
            'crop_coordinate_system': 'displayed PDF page points; [x0,y0,x1,y1]; top-left origin; 1-indexed PDF pages',
            'content_policy': 'Real PDF pixels; no OCR, regenerated text, translation painted over source, or retouching.',
            'coverage': 'all source pages' if len(pages) == len(doc) else 'selected source pages only',
        }
    result = {'images': images, 'sizes': sizes, 'screenshots': shots,
              'screenshot_provenance': provenance}
    path = output_dir/'source_layer.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    manifest = {'provenance': provenance, 'regions': shots}
    (output_dir/'index.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return {'output': str(path), 'pages': len(images), 'regions': len(shots), 'source_sha256': provenance['source_sha256']}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf', type=Path, required=True)
    ap.add_argument('--regions', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--dpi', type=int, default=200)
    ap.add_argument('--pages', choices=['auto', 'all', 'referenced'], default='auto')
    args = ap.parse_args()
    try:
        print(json.dumps(render_sources(args.pdf, args.regions, args.output_dir, args.dpi, args.pages), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, TypeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
