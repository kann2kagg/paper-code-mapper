#!/usr/bin/env python3
"""Export authored region translations as readable Markdown (not a translator)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from source_support import validate_sources


def export_translations(data: dict, language: str | None = None) -> str:
    if data.get('localization'):
        from language_support import selected_document, validate_localization
        check = validate_localization(data)
        if check['errors']: raise ValueError('\n'.join(check['errors']))
        loc = data['localization']
        language = language or loc['default_translation']
        if language not in loc['translations']: raise ValueError('Requested language has not been authored: '+language)
        data = selected_document(data, loc['default_reading'], language)
    elif language and language != data.get('source_layer', {}).get('translation_language'):
        raise ValueError('Requested language has not been authored: '+language)
    report = validate_sources(data)
    if report['errors']:
        raise ValueError('\n'.join(report['errors']))
    lines = ['# '+data.get('title', 'Source translations'), '',
             '> Selected source regions only. Full-page images provide context, not a claim of full-page translation.', '']
    if data.get('translation_display_mode') == 'transcription':
        lines.insert(2, '> Original-language source transcription, not a translation.\n')
    shots = data.get('screenshots', {})
    translations = data.get('screenshot_translations', {})
    for rid, shot in sorted(shots.items(), key=lambda item:(item[1]['page'], item[0])):
        tr = translations.get(rid, {})
        lines += ['## '+tr.get('title_target', tr.get('title_zh', shot['title'])), '',
                  f"Source: PDF page {shot['page']} | region `{rid}` | rectangle `{shot['clip']}`", '']
        if not tr or tr.get('status') == 'unavailable':
            lines += ['Translation unavailable: '+tr.get('reason', 'No authored translation provided.'), '']
            continue
        for block in tr['blocks']:
            typ = block['type']
            if typ in {'paragraph', 'heading'}:
                lines += [('### ' if typ == 'heading' else '')+block['text'], '']
            elif typ in {'equation', 'code'}:
                fence = '`' * max(3, max((len(x) for x in __import__('re').findall(r'`+', block['text'])), default=0)+1)
                lines += [fence+'text', block['text'], fence, '']
            elif typ in {'pairs', 'table'}:
                headers = ['Source text', 'Translation'] if typ == 'pairs' else block['headers']
                if block.get('title'):
                    lines += ['### '+block['title'], '']
                escape = lambda x:x.replace('|','\\|').replace('\n','<br>')
                row = lambda cells:'| '+' | '.join(escape(c) for c in cells)+' |'
                lines += [row(headers), row(['---']*len(headers))]
                lines += [row(r) for r in block['rows']]+['']
        if tr.get('notes'):
            lines += ['**Translator notes (not source text)**', '']+[n+'\n' for n in tr['notes']]
        if tr.get('related_ids'):
            lines += ['Continuation regions: '+', '.join('`'+r+'`' for r in tr['related_ids']), '']
    return '\n'.join(lines)+'\n'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--language', help='Select an authored source-text/translation language (e.g. zh-CN or en)')
    args = ap.parse_args()
    try:
        if args.output.resolve() == args.input.resolve():
            raise ValueError('output must differ from analysis JSON')
        result = export_translations(json.loads(args.input.read_text(encoding='utf-8')), args.language)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding='utf-8')
        print(args.output)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
