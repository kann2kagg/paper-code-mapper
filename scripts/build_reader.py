#!/usr/bin/env python3
"""Validate authored annotations and render a self-contained code-first reader.

This renderer does not perform repository analysis or run the inspected project.
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import base64
import copy
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import urlparse
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_support import validate_sources, ui_for
STATUSES = {
    'Exact match', 'Equivalent implementation', 'Partial match', 'Runtime override',
    'Implementation extension', 'Potential mismatch', 'No direct paper counterpart',
    'Unresolved',
}
KINDS = {'verbatim', 'pseudocode', 'teaching'}


def is_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if not value:
        return True
    try:
        u = urlparse(value)
    except ValueError:
        return False
    return u.scheme in {'http', 'https'} and bool(u.netloc) and not u.username and not u.password


def validate_data(data: Any, repo_root: Path | None = None, source_pdf: Path | None = None) -> dict[str, Any]:
    """Check structure and, optionally, exact local verbatim source ranges."""
    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    verbatim = 0
    row_count = 0
    blocks_count = 0

    def require_text(obj: dict, field: str, where: str) -> None:
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            errors.append(f'{where}.{field}: nonempty text required')

    def valid_path(path: Any, where: str) -> bool:
        if not isinstance(path, str) or not path or '\\' in path:
            errors.append(f'{where}: repository-relative POSIX path required')
            return False
        p = PurePosixPath(path)
        if p.is_absolute() or '..' in p.parts or ':' in path:
            errors.append(f'{where}: unsafe source path')
            return False
        return True

    if not isinstance(data, dict):
        return {'valid': False, 'errors': ['root must be an object'], 'warnings': [],
                'source_ranges_checked': 0, 'statements': 0, 'blocks': 0}
    if data.get('schema_version') not in {'1.0', '1.1', '1.2'}:
        errors.append('schema_version must be 1.0, 1.1 or 1.2')
    for field in ['title', 'scope', 'evidence_level']:
        require_text(data, field, 'root')
    if data.get('language', 'zh-CN') not in {'zh-CN', 'en'}:
        errors.append('language must be zh-CN or en; add a reviewed UI locale before using another value')
    repository = data.get('repository', {})
    if not isinstance(repository, dict):
        errors.append('repository must be an object')
        repository = {}
    if not is_url(repository.get('url', '')):
        errors.append('repository.url must be an http(s) URL without credentials or empty')
    commit = repository.get('commit', '')
    if not isinstance(commit, str):
        errors.append('repository.commit must be a string (empty when unknown)')
    elif not commit:
        warnings.append('No commit recorded; do not describe source links as commit-pinned.')
    paper = data.get('paper', {})
    if not isinstance(paper, dict) or not is_url(paper.get('url', '')):
        errors.append('paper must be an object with an optional safe http(s) url')

    points = data.get('paperPoints', [])
    if not isinstance(points, list):
        errors.append('paperPoints must be an array')
        points = []
    for i, point in enumerate(points):
        where = f'paperPoints[{i}]'
        if not isinstance(point, dict):
            errors.append(f'{where}: object required')
            continue
        for field in ['section', 'paperSummary', 'relation']:
            require_text(point, field, where)
        if point.get('status') not in STATUSES:
            errors.append(f'{where}.status: unrecognized evidence status')
        if not isinstance(point.get('page'), int) or isinstance(point.get('page'), bool) or point['page'] < 1:
            errors.append(f'{where}.page: positive PDF page index required')
        if not is_url(point.get('paperUrl', '')):
            errors.append(f'{where}.paperUrl: unsafe URL')
        for k in ('rect', 'clip'):
            if k in point:
                box = point[k]
                if (not isinstance(box, list) or len(box) != 4 or
                    not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in box) or
                    box[2] <= box[0] or box[3] <= box[1]):
                    errors.append(f'{where}.{k}: valid [x0,y0,x1,y1] required')

    images = data.get('images', {})
    sizes = data.get('sizes', {})
    if not isinstance(images, dict) or not isinstance(sizes, dict):
        errors.append('images and sizes must be objects')
    else:
        for page, uri in images.items():
            if not isinstance(uri, str) or not re.fullmatch(r'data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/=\r\n]+', uri):
                errors.append(f'images[{page}]: only embedded PNG/JPEG/WebP allowed')
                continue
            try:
                base64.b64decode(uri.split(',', 1)[1].replace('\n', '').replace('\r', ''), validate=True)
            except ValueError:
                errors.append(f'images[{page}]: invalid base64')
            size = sizes.get(page)
            if not isinstance(size, list) or len(size) != 2 or not all(isinstance(v, (float, int)) and v > 0 and math.isfinite(v) for v in size):
                errors.append(f'sizes[{page}]: positive page width and height required')

    lessons = data.get('lessons', [])
    if not isinstance(lessons, list) or not lessons:
        errors.append('lessons must be a nonempty array')
        lessons = []
    ids: set[str] = set()
    base = repo_root.resolve() if repo_root is not None else None
    if base is not None and not base.is_dir():
        errors.append('repo-root must be an existing directory')
    for i, lesson in enumerate(lessons):
        loc = f'lessons[{i}]'
        if not isinstance(lesson, dict):
            errors.append(f'{loc}: object required')
            continue
        for field in ['id', 'title', 'file', 'role', 'before', 'after']:
            require_text(lesson, field, loc)
        lid = lesson.get('id', '')
        if not isinstance(lid, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', lid):
            errors.append(f'{loc}.id: use letters, numbers, dot, underscore or hyphen')
        elif lid in ids:
            errors.append(f'{loc}.id: duplicate {lid}')
        else:
            ids.add(lid)
        valid_path(lesson.get('file'), loc + '.file')
        variables = lesson.get('variables', [])
        if not isinstance(variables, list) or not all(isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) and x.strip() for x in v) for v in variables):
            errors.append(f'{loc}.variables: [name, explanation] pairs required')
        chain = lesson.get('chain', [])
        if not isinstance(chain, list) or not chain or not all(isinstance(v, str) and v.strip() for v in chain):
            errors.append(f'{loc}.chain: nonempty strings required; state missing caller explicitly')
        refs = lesson.get('papers', [])
        if not isinstance(refs, list) or not all(isinstance(p, int) and not isinstance(p, bool) and 0 <= p < len(points) for p in refs):
            errors.append(f'{loc}.papers: out-of-range paperPoints reference')
        ex = lesson.get('example', '')
        if not isinstance(ex, str):
            if not isinstance(ex, dict) or ex.get('kind') != 'steps' or not isinstance(ex.get('steps'), list) or not ex['steps']:
                errors.append(f'{loc}.example: string or a nonempty steps example required')
            else:
                for j, step in enumerate(ex['steps']):
                    if not isinstance(step, dict):
                        errors.append(f'{loc}.example.steps[{j}]: object required')
                    else:
                        require_text(step, 'title', loc + '.example')
                        require_text(step, 'state', loc + '.example')
        blocks = lesson.get('blocks', [])
        if not isinstance(blocks, list) or not blocks:
            errors.append(f'{loc}.blocks: nonempty array required')
            continue
        for bi, block in enumerate(blocks):
            blocks_count += 1
            bloc = f'{loc}.blocks[{bi}]'
            if not isinstance(block, dict):
                errors.append(f'{bloc}: object required')
                continue
            require_text(block, 'title', bloc)
            require_text(block, 'summary', bloc)
            path_ok = valid_path(block.get('path'), bloc + '.path')
            kind = block.get('source_kind')
            if kind not in KINDS:
                errors.append(f'{bloc}.source_kind: choose verbatim, pseudocode or teaching')
            url = block.get('url', '')
            if not is_url(url):
                errors.append(f'{bloc}.url: unsafe URL')
            elif commit and url and '/blob/' in url and commit not in urlparse(url).path:
                warnings.append(f'{bloc}: source URL is not pinned to recorded commit')
            rows = block.get('rows', [])
            if not isinstance(rows, list) or not rows:
                errors.append(f'{bloc}.rows: nonempty array required')
                continue
            for ri, row in enumerate(rows):
                row_count += 1
                rloc = f'{bloc}.rows[{ri}]'
                if not isinstance(row, dict):
                    errors.append(f'{rloc}: object required')
                    continue
                for field in ['code', 'meaning', 'why', 'result']:
                    require_text(row, field, rloc)
                start, end = row.get('start_line'), row.get('end_line')
                has_range = start is not None or end is not None
                range_ok = all(isinstance(v, int) and not isinstance(v, bool) for v in [start, end]) and start >= 1 and end >= start
                if kind == 'verbatim':
                    verbatim += 1
                    if not range_ok:
                        errors.append(f'{rloc}: verbatim code needs real start_line and end_line')
                elif has_range and not range_ok:
                    errors.append(f'{rloc}: invalid line range')
                if kind == 'verbatim' and range_ok and base is not None and path_ok:
                    path = (base / block['path']).resolve()
                    if not path.is_relative_to(base):
                        errors.append(f'{rloc}: source resolves outside repo-root')
                        continue
                    try:
                        lines = path.read_text(encoding='utf-8').splitlines()
                        expected = '\n'.join(lines[start - 1:end])
                        if end > len(lines) or row.get('code', '').rstrip('\n') != expected:
                            errors.append(f'{rloc}: excerpt differs from {block["path"]}:{start}-{end}')
                        else:
                            checked += 1
                    except (OSError, UnicodeError) as exc:
                        errors.append(f'{rloc}: cannot read source: {exc}')
    argument = data.get('argument')
    n_argument = 0
    if argument is None:
        if data.get('schema_version') in {'1.1', '1.2'} and isinstance(paper, dict) and paper.get('title'):
            errors.append('argument: provide the author argument or explicitly mark unavailable with a reason')
        elif points:
            warnings.append('Legacy reader has local paper links but no complete author argument.')
    elif not isinstance(argument, dict):
        errors.append('argument must be an object')
    elif argument.get('status') == 'unavailable':
        require_text(argument, 'reason', 'argument')
    elif argument.get('status') != 'provided':
        errors.append('argument.status must be provided or unavailable')
    else:
        for key in ['title', 'question', 'takeaway', 'scope']:
            require_text(argument, key, 'argument')
        nodes = argument.get('nodes', [])
        if not isinstance(nodes, list) or not nodes:
            errors.append('argument.nodes must be a nonempty array')
            nodes = []
        node_ids = set()
        lesson_by_id = {l.get('id'): l for l in lessons if isinstance(l, dict)}
        for ni, node in enumerate(nodes):
            loc = f'argument.nodes[{ni}]'
            if not isinstance(node, dict):
                errors.append(f'{loc}: object required')
                continue
            for key in ['id', 'title', 'stage', 'question', 'claim', 'because', 'consequence', 'boundary']:
                require_text(node, key, loc)
            nid = node.get('id')
            if not isinstance(nid, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', nid):
                errors.append(f'{loc}.id: safe anchor ID required')
            elif nid in node_ids:
                errors.append(f'{loc}.id: duplicate node ID')
            else:
                node_ids.add(nid)
            basis = node.get('basis')
            if basis not in {'author-stated', 'source-analysis', 'teaching'}:
                errors.append(f'{loc}.basis: author-stated, source-analysis or teaching required')
            refs = node.get('references', [])
            if not isinstance(refs, list):
                errors.append(f'{loc}.references: array required')
                refs = []
            if basis in {'author-stated', 'source-analysis'} and not refs:
                errors.append(f'{loc}: source-derived claims require paper references')
            for ri, ref in enumerate(refs):
                rl = f'{loc}.references[{ri}]'
                if not isinstance(ref, dict):
                    errors.append(f'{rl}: object required')
                    continue
                for key in ['section', 'locator']:
                    require_text(ref, key, rl)
                page = ref.get('page')
                if not isinstance(page, int) or isinstance(page, bool) or page < 1:
                    errors.append(f'{rl}.page: positive PDF page required')
                if not is_url(ref.get('url', '')):
                    errors.append(f'{rl}.url: safe http(s) URL or empty required')
            links = node.get('code_links', [])
            if not isinstance(links, list):
                errors.append(f'{loc}.code_links: array required')
                links = []
            if not links:
                require_text(node, 'code_note', loc)
            for li, link in enumerate(links):
                ll = f'{loc}.code_links[{li}]'
                if not isinstance(link, dict):
                    errors.append(f'{ll}: object required')
                    continue
                target = lesson_by_id.get(link.get('lesson'))
                if target is None:
                    errors.append(f'{ll}.lesson: unknown code unit')
                block = link.get('block')
                if block is not None and (not isinstance(block, int) or isinstance(block, bool) or block < 0 or target is None or block >= len(target.get('blocks', []))):
                    errors.append(f'{ll}.block: unknown code block')
                if link.get('role') not in {'implements', 'configures', 'measures', 'infrastructure'}:
                    errors.append(f'{ll}.role: explicit correspondence role required')
                require_text(link, 'explanation', ll)
        n_argument = len(nodes)
        edges = argument.get('edges', [])
        if not isinstance(edges, list):
            errors.append('argument.edges must be an array')
            edges = []
        for ei, edge in enumerate(edges):
            loc = f'argument.edges[{ei}]'
            if not isinstance(edge, dict):
                errors.append(f'{loc}: object required')
                continue
            if edge.get('from') not in node_ids or edge.get('to') not in node_ids:
                errors.append(f'{loc}: unknown argument node')
            for key in ['relation', 'explanation']:
                require_text(edge, key, loc)
            if edge.get('basis') not in {'author-stated', 'source-analysis', 'teaching'}:
                errors.append(f'{loc}.basis: explicit attribution required')
        if argument.get('default_node') and argument['default_node'] not in node_ids:
            errors.append('argument.default_node: unknown node')
    if data.get('default_view', 'code') not in {'code', 'argument'}:
        errors.append('default_view must be code or argument')
    if data.get('default_lesson') and data['default_lesson'] not in ids:
        errors.append('default_lesson does not name a reading unit')
    if base is None and verbatim:
        warnings.append('No repo-root: verbatim source ranges were not compared with local files.')
    src = validate_sources(data, source_pdf)
    errors.extend(src.pop('errors'))
    warnings.extend(src.pop('warnings'))
    warnings.append('Schema/range checks do not verify explanation semantics, paper alignment, or experimental results.')
    from language_support import validate_localization
    locales_report = validate_localization(data)
    errors.extend(locales_report.pop('errors'))
    warnings.extend(locales_report.pop('warnings'))
    return {'valid': not errors, 'errors': errors, 'warnings': warnings,
            'source_ranges_checked': checked, 'verbatim_statements': verbatim,
            'statements': row_count, 'blocks': blocks_count, 'lessons': len(lessons), 'argument_nodes': n_argument, **src, **locales_report}


def render(data: dict[str, Any]) -> str:
    if data.get("localization"):
        from language_support import render_multilingual
        return render_multilingual(data, render_single)
    return render_single(data)


def render_single(data: dict[str, Any]) -> str:
    safe = copy.deepcopy(data)
    language = safe.get('language', 'zh-CN')
    locales = json.loads((ROOT / 'assets' / 'ui.json').read_text(encoding='utf-8'))
    safe['ui'] = locales[language]
    safe['source_ui'], safe['translation_ui'] = ui_for(safe)
    payload = json.dumps(safe, ensure_ascii=False, allow_nan=False)
    for char, escaped in [('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'), ('\u2028', '\\u2028'), ('\u2029', '\\u2029')]:
        payload = payload.replace(char, escaped)
    template = (ROOT / 'assets' / 'reader-template.html').read_text(encoding='utf-8')
    marker = '__READER_JSON__'
    if template.count(marker) != 1:
        raise ValueError('reader template must contain exactly one data marker')
    template = template.replace('__ARGUMENT_CSS__', (ROOT / 'assets' / 'argument-view.css').read_text(encoding='utf-8'))
    template = template.replace('__ARGUMENT_JS__', (ROOT / 'assets' / 'argument-view.js').read_text(encoding='utf-8'))
    source_css = ''
    source_js = (ROOT / 'assets/source-status.js').read_text(encoding='utf-8')
    if safe.get('screenshots') and safe.get('images'):
        source_css = '\n'.join((ROOT / 'assets' / name).read_text(encoding='utf-8')
                               for name in ['source-view.css', 'translation-view.css'])
        source_js += '\n' + '\n'.join((ROOT / 'assets' / name).read_text(encoding='utf-8')
                              for name in ['source-view.js', 'translation-view.js'])
    template = template.replace('__SOURCE_CSS__', source_css).replace('__SOURCE_JS__', source_js)
    return template.replace(marker, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--repo-root', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--source-pdf', type=Path, help='Optional local PDF to verify source SHA256; does not certify translation semantics')
    args = parser.parse_args()
    try:
        if args.output.suffix.lower() != '.html' or args.output.resolve() == args.input.resolve():
            raise ValueError('output must be a distinct .html file')
        data = json.loads(args.input.read_text(encoding='utf-8'))
        report = validate_data(data, args.repo_root, args.source_pdf)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        if not report['valid']:
            print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
        html = render(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temp = args.output.with_suffix('.html.tmp')
        temp.write_text(html, encoding='utf-8')
        temp.replace(args.output)
        print(json.dumps({'output': str(args.output), **report}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
