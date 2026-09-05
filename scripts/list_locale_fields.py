#!/usr/bin/env python3
"""Export translatable prose paths. This is a source inventory, not a translation."""
import argparse
import json
from pathlib import Path
from language_support import prose_fields

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if args.input.resolve()==args.output.resolve(): ap.error('output must not overwrite input')
    data=json.loads(args.input.read_text(encoding='utf-8'))
    result={'status':'source-inventory-not-translated','base_language':data.get('language','zh-CN'),'fields':prose_fields(data)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(result["fields"])} prose fields; review and translate them before enabling another reading language.')
if __name__=='__main__': main()
