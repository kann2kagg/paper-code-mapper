#!/usr/bin/env python3
"""Merge checked source images and authored translations into existing annotations.

Does not infer crop links, create translations, or rewrite the code/argument tracks.
The existing analysis must already carry shot_ids at its paper reference locations.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import sys
from source_support import validate_sources


def merge_sources(analysis: dict, source_layer: dict, translations: dict,
                  partial_reason: str = '', target_language: str = 'zh-CN',
                  source_language: str = 'en') -> dict:
    result = copy.deepcopy(analysis)
    if not isinstance(source_layer, dict) or not isinstance(translations, dict):
        raise ValueError('source layer and translations must be JSON objects')
    for key in ['images', 'sizes', 'screenshots', 'screenshot_provenance']:
        if key not in source_layer:
            raise ValueError(f'source layer missing {key}')
        result[key] = copy.deepcopy(source_layer[key])
    result['schema_version'] = '1.2'
    result['screenshot_translations'] = copy.deepcopy(translations)
    result['source_layer'] = {'status': 'partial' if partial_reason else 'provided',
                              'reason': partial_reason, 'translation_language': target_language,
                              'source_language': source_language}
    result['translation_provenance'] = {
        'source_pdf_sha256': result['screenshot_provenance']['source_sha256'],
        'scope': 'selected screenshot regions only; full-page viewing is context, not full-page translation',
        'translation_language': target_language,
        'source_images_unchanged_by_merge': True,
        'code_annotations_unchanged_by_merge': True,
        'author_argument_unchanged_by_merge': True,
        'runtime_claim': 'Merge does not run a model, translate text, or verify semantics.',
    }
    report = validate_sources(result)
    if report['errors']:
        raise ValueError('\n'.join(report['errors']))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--analysis', required=True, type=Path)
    ap.add_argument('--sources', required=True, type=Path)
    ap.add_argument('--translations', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--partial-reason', default='')
    ap.add_argument('--target-language', default='zh-CN')
    ap.add_argument('--source-language', default='en')
    args = ap.parse_args()
    try:
        if args.output.resolve() in {args.analysis.resolve(), args.sources.resolve(), args.translations.resolve()}:
            raise ValueError('write to a distinct output JSON; preserve the input source artifacts')
        load = lambda p: json.loads(p.read_text(encoding='utf-8'))
        result = merge_sources(load(args.analysis), load(args.sources), load(args.translations),
                               args.partial_reason, args.target_language, args.source_language)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'output':str(args.output), 'regions':len(result['screenshots']),
                          'translations':len(result['screenshot_translations'])}, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
