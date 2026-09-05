"""Authored locale overlays for an offline reader. Never translates or calls APIs.

Only prose leaves may be localized. Source code, images, equations, source IDs,
line ranges and graph edges stay in one shared source document.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any
from source_support import validate_sources, ui_for

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r'^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$')

def prose_fields(data: dict) -> dict[str, str]:
    """Return an allowlist of JSON-pointer paths to authored teaching prose."""
    result: dict[str, str] = {}
    def take(obj, prefix, fields):
        if isinstance(obj, dict):
            for key in fields:
                val = obj.get(key)
                if isinstance(val, str) and val.strip():
                    result[f'{prefix}/{key}'] = val
    take(data, '', ['title', 'scope', 'evidence_level'])
    for i, lesson in enumerate(data.get('lessons', [])):
        p = f'/lessons/{i}'
        take(lesson, p, ['title', 'role', 'before', 'after', 'caution'])
        for j, value in enumerate(lesson.get('chain', [])):
            if isinstance(value, str) and value.strip(): result[f'{p}/chain/{j}'] = value
        for j, pair in enumerate(lesson.get('variables', [])):
            if isinstance(pair, list) and len(pair) == 2 and isinstance(pair[1], str):
                result[f'{p}/variables/{j}/1'] = pair[1]
        example = lesson.get('example')
        if isinstance(example, str) and example.strip():
            result[f'{p}/example'] = example
        elif isinstance(example, dict):
            for j, step in enumerate(example.get('steps', [])):
                take(step, f'{p}/example/steps/{j}', ['title', 'explanation'])
        for j, block in enumerate(lesson.get('blocks', [])):
            q = f'{p}/blocks/{j}'
            take(block, q, ['title', 'summary', 'note'])
            for k, row in enumerate(block.get('rows', [])):
                take(row, f'{q}/rows/{k}', ['meaning', 'why', 'result'])
    for i, point in enumerate(data.get('paperPoints', [])):
        take(point, f'/paperPoints/{i}', ['section', 'paperSummary', 'relation'])
    argument = data.get('argument') or {}
    if isinstance(argument, dict):
        take(argument, '/argument', ['title', 'question', 'takeaway', 'scope', 'reason'])
        for i, node in enumerate(argument.get('nodes', [])):
            p = f'/argument/nodes/{i}'
            take(node, p, ['title', 'stage', 'question', 'claim', 'because', 'consequence', 'boundary', 'code_note'])
            for j, ref in enumerate(node.get('references', [])):
                take(ref, f'{p}/references/{j}', ['section', 'locator'])
            for j, link in enumerate(node.get('code_links', [])):
                take(link, f'{p}/code_links/{j}', ['explanation'])
        for i, edge in enumerate(argument.get('edges', [])):
            take(edge, f'/argument/edges/{i}', ['relation', 'explanation'])
    take(data.get('source_layer'), '/source_layer', ['reason'])
    return result

def patch_prose(data: dict, patch: dict) -> dict:
    out = copy.deepcopy(data)
    allowed = prose_fields(data)
    for path, value in patch.items():
        if path not in allowed or not isinstance(value, str) or not value.strip():
            raise ValueError(f'Not a valid localizable prose leaf: {path}')
        keys = path.lstrip('/').split('/')
        obj = out
        for key in keys[:-1]: obj = obj[int(key)] if isinstance(obj, list) else obj[key]
        if isinstance(obj, list): obj[int(keys[-1])] = value
        else: obj[keys[-1]] = value
    return out

def without_localization(data: dict) -> dict:
    out = copy.deepcopy(data)
    out.pop('localization', None)
    return out

def selected_document(data: dict, reading: str, translation: str) -> dict:
    loc = data['localization']
    out = patch_prose(without_localization(data), loc['readings'][reading].get('patch', {}))
    out['language'] = reading
    if translation:
        pack = loc['translations'][translation]
        out['screenshot_translations'] = copy.deepcopy(pack['regions'])
        out.setdefault('source_layer', {})['translation_language'] = translation
        out.setdefault('translation_provenance', {})['translation_language'] = translation
        out['translation_display_mode'] = pack.get('mode', 'translation')
    if any(isinstance(t, dict) and t.get('status') == 'unavailable' for t in out.get('screenshot_translations', {}).values()):
        out.setdefault('source_layer', {}).update(status='partial', reason='Some regions are explicitly unavailable in the selected language.')
    return out

def _shape_errors(value: Any, reference: Any, prefix: str) -> list[str]:
    errors = []
    if isinstance(reference, dict):
        if not isinstance(value, dict): return [f'{prefix}: complete UI object required']
        for key, ref in reference.items(): errors += _shape_errors(value.get(key), ref, f'{prefix}.{key}')
    elif not isinstance(value, str) or not value.strip(): errors.append(f'{prefix}: nonempty UI text required')
    return errors

def validate_localization(data: dict) -> dict:
    loc = data.get('localization')
    if loc is None: return {'errors': [], 'warnings': [], 'reading_languages': [], 'translation_languages': []}
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(loc, dict):
        return {'errors': ['localization must be an object'], 'warnings': [], 'reading_languages': [], 'translation_languages': []}
    if loc.get('version') != '1.0': errors.append('localization.version must be 1.0')
    readers = loc.get('readings')
    trans = loc.get('translations')
    if not isinstance(readers, dict) or not readers: errors.append('localization.readings must be a nonempty object'); readers = {}
    if not isinstance(trans, dict): errors.append('localization.translations must be an object'); trans = {}
    base_lang = data.get('language', 'zh-CN')
    if base_lang not in readers: errors.append('Include the base language in localization.readings')
    if loc.get('default_reading') not in readers: errors.append('default_reading is not an authored reading language')
    if trans and loc.get('default_translation') not in trans: errors.append('default_translation is not an authored translation language')
    if not trans and loc.get('default_translation', ''): errors.append('default_translation must be empty without translated regions')
    if data.get('screenshots') and not trans: errors.append('Provide localization.translations for a source-backed multilingual reader')
    fields = prose_fields(data)
    templates = json.loads((ROOT/'assets/ui.json').read_text())
    source_templates = json.loads((ROOT/'assets/source-ui.json').read_text())
    argument_templates = json.loads((ROOT/'assets/argument-ui.json').read_text())
    shell_templates = json.loads((ROOT/'assets/language-ui.json').read_text())
    for lang, entry in readers.items():
        where = f'localization.readings[{lang}]'
        if not isinstance(lang, str) or not TAG.fullmatch(lang): errors.append(f'{where}: valid language tag required')
        if not isinstance(entry, dict): errors.append(f'{where}: object required'); continue
        if not isinstance(entry.get('label'), str) or not entry['label'].strip(): errors.append(f'{where}.label required')
        patch = entry.get('patch', {})
        if not isinstance(patch, dict): errors.append(f'{where}.patch must be an object'); continue
        if lang == base_lang and patch: errors.append('The base reading language must use an empty patch')
        if lang != base_lang:
            missing = fields.keys() - patch.keys()
            if missing: errors.append(f'{where}: untranslated prose fields: '+', '.join(sorted(missing)))
        for path, val in patch.items():
            if path not in fields: errors.append(f'{where}: forbidden or unknown localization path {path}')
            if not isinstance(val, str) or not val.strip(): errors.append(f'{where}.{path}: nonempty translation required')
        custom = entry.get('ui')
        if lang not in templates and custom is None: errors.append(f'{where}: this language needs complete reviewed UI catalogs')
        if custom is not None:
            reference = {'reader': templates['en'], 'source': source_templates['en'], 'argument': argument_templates['en'], 'shell': shell_templates['en']}
            errors += _shape_errors(custom, reference, where+'.ui')
    shots = data.get('screenshots', {})
    base_trans = data.get('screenshot_translations', {})
    for lang, pack in trans.items():
        where = f'localization.translations[{lang}]'
        if not isinstance(lang, str) or not TAG.fullmatch(lang): errors.append(f'{where}: valid language tag required')
        if not isinstance(pack, dict): errors.append(f'{where}: object required'); continue
        if not isinstance(pack.get('label'), str) or not pack['label'].strip(): errors.append(f'{where}.label required')
        mode = pack.get('mode', 'translation')
        if mode not in {'translation', 'transcription'}: errors.append(f'{where}.mode must be translation or transcription')
        if mode == 'transcription' and lang != data.get('source_layer', {}).get('source_language'):
            errors.append(f'{where}: source transcription must use the source language')
        regions = pack.get('regions')
        if not isinstance(regions, dict): errors.append(f'{where}.regions must be an object'); continue
        if set(regions) != set(shots): errors.append(f'{where}: every selected region needs translated content or an explicit unavailable record')
        variant = without_localization(data)
        variant['screenshot_translations'] = regions
        if any(isinstance(t, dict) and t.get('status') == 'unavailable' for t in regions.values()):
            # The displayed per-region notice explains missing coverage; do not silently use another language.
            variant.setdefault('source_layer', {}).update(status='partial', reason='Some selected regions are explicitly unavailable in this language.')
            warnings.append(f'{where}: partial translations; unavailable notices must remain visible')
        check = validate_sources(variant)
        errors += [f'{where}: {e}' for e in check['errors']]
        if check['errors']: continue
        for rid, record in regions.items():
            if not isinstance(record, dict) or record.get('status') == 'unavailable': continue
            ref = base_trans.get(rid, {})
            ref_blocks = ref.get('blocks', []) if isinstance(ref, dict) else []
            new_blocks = record.get('blocks', [])
            immutable = lambda blocks: [(b.get('type'), b.get('text')) for b in blocks if isinstance(b, dict) and b.get('type') in {'equation','code'}]
            if immutable(ref_blocks) != immutable(new_blocks): errors.append(f'{where}.{rid}: equation/code literals must stay unchanged across locales')
            old_tables = [b for b in ref_blocks if b.get('type')=='table']
            new_tables = [b for b in new_blocks if b.get('type')=='table']
            if len(old_tables) != len(new_tables): errors.append(f'{where}.{rid}: translated table structure changed')
            for old,new in zip(old_tables,new_tables):
                if len(old.get('headers', [])) != len(new.get('headers', [])) or len(old.get('rows', [])) != len(new.get('rows', [])):
                    errors.append(f'{where}.{rid}: translated table dimensions changed'); continue
                for row_o,row_n in zip(old.get('rows', []),new.get('rows', [])):
                    for a,b in zip(row_o,row_n):
                        if re.fullmatch(r'[\d\s.,%+\-\u00b1eE]+', str(a)) and a != b:
                            errors.append(f'{where}.{rid}: a numerical table value changed')
    return {'errors': errors, 'warnings': warnings, 'reading_languages': list(readers), 'translation_languages': list(trans),
            'localized_prose_fields': len(fields), 'translation_language_semantics_checked': False}

def catalog_for(data: dict, reading: str, translation: str) -> dict:
    entry = data['localization']['readings'][reading]
    doc = selected_document(data, reading, translation)
    custom = entry.get('ui')
    if custom:
        reader = copy.deepcopy(custom['reader']); arg = copy.deepcopy(custom['argument']); shell = copy.deepcopy(custom['shell'])
        raw = copy.deepcopy(custom['source'])
        src, tr = raw['source'], raw['translation']
    else:
        reader = json.loads((ROOT/'assets/ui.json').read_text())[reading]
        arg = json.loads((ROOT/'assets/argument-ui.json').read_text())[reading]
        shell = json.loads((ROOT/'assets/language-ui.json').read_text())[reading]
        src, tr = ui_for(doc)
    label = data['localization']['translations'].get(translation, {}).get('label', '')
    mode = doc.get('translation_display_mode', 'translation')
    kind = shell['transcript'] if mode == 'transcription' else shell['translation']
    tr['heading'] = f'{kind} | {label}' if label else kind
    tr['badge'] = shell['transcriptBadge'] if mode == 'transcription' else shell['translationBadge']
    tr['sourceHeading'] = shell['source']+' + '+kind
    tr['noTranslation'] = shell['missing'].replace('{language}', label)
    tr['galleryHint'] = shell['galleryHint']
    tr['shortcut'] = shell['sourceShortcut']
    tr['tableHint'] = shell['tableHint']
    if mode == 'transcription':
        for target,key in {'cropScope':'transcriptCropScope','fullScope':'transcriptFullScope','pageScope':'transcriptPageScope','index':'transcriptIndex','indexIntro':'transcriptIndexIntro','about':'transcriptAbout','enlarge':'transcriptEnlarge','viewerNote':'transcriptViewerNote','hide':'transcriptHide','show':'transcriptShow','paperTab':'transcriptPaperTab','notes':'transcriptNotes','noPage':'transcriptNoPage'}.items():
            tr[target] = shell[key]
    src_count = str(len(doc.get('screenshots', {})))
    tr_count = str(sum(t.get('status') != 'unavailable' and bool(t.get('blocks')) for t in doc.get('screenshot_translations', {}).values()))
    for d in (src,tr):
        for k,v in d.items():
            d[k] = v.replace('{regions}',src_count).replace('{translated}',tr_count).replace('{version}',str(doc.get('paper',{}).get('version',''))).replace('{target}',translation)
    return {'ui':reader, 'argument_ui':arg, 'source_ui':src, 'translation_ui':tr, 'shell_ui':shell}

def safe_json(value: Any) -> str:
    s = json.dumps(value, ensure_ascii=False, allow_nan=False)
    for a,b in [('&','\\u0026'),('<','\\u003c'),('>','\\u003e'),('\u2028','\\u2028'),('\u2029','\\u2029')]: s=s.replace(a,b)
    return s

def render_multilingual(data: dict, render_single) -> str:
    check = validate_localization(data)
    if check['errors']: raise ValueError('; '.join(check['errors']))
    base = without_localization(data)
    # A single code/template copy and one shared set of source images, not N full pages.
    template = render_single(base)
    template,n = re.subn(r'(<script id="readerdata" type="application/json">).*?(</script>)',r'\1__LOCALIZED_DATA__\2',template,count=1,flags=re.S)
    if n != 1: raise ValueError('Cannot find data slot in reader template')
    template = template.replace("history.replaceState(null,'',", 'window.__pcmrNavigate(')
    bootstrap = '<script>window.__pcmrNavigate=function(h){if(window.parent===window){history.replaceState(null,"",h);}else{window.parent.postMessage({type:"pcmr-anchor",hash:h},"*");}};</script>'
    template = template.replace('</head>',bootstrap+'</head>')
    bridge = (ROOT/'assets/language-bridge.js').read_text()
    template = template.replace('</script></body></html>', '\n'+bridge+'\n</script></body></html>')
    translations = list(data['localization']['translations']) or ['']
    catalogs = {r:{t:catalog_for(data,r,t) for t in translations} for r in data['localization']['readings']}
    ident = hashlib.sha256(json.dumps({'repo':base.get('repository'),'paper':base.get('paper'),'ids':[l['id'] for l in base['lessons']]},sort_keys=True).encode()).hexdigest()[:20]
    bundle = {'base':base,'localization':data['localization'],'template':template,'catalogs':catalogs,'storage_key':'paper-code-reader-language-v1-'+ident}
    shell = (ROOT/'assets/language-shell.html').read_text()
    return shell.replace('__LANGUAGE_BUNDLE__',safe_json(bundle)).replace('__LANGUAGE_JS__',(ROOT/'assets/language-shell.js').read_text())
