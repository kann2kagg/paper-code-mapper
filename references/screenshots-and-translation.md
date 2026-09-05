# Real source images and faithful translations

## Contents
1. Evidence is not a decoration
2. Choose and render regions
3. Bind translations to exact images
4. Handle figures, tables, algorithms and continuations
5. User-interface behavior
6. Commands and deliverables
7. Manual verification

## 1. Evidence is not a decoration

Keep four layers visibly distinct: original PDF pixels; faithful translation;
author-argument interpretation; code explanation. None substitutes for another.
A page citation without visible pixels does not satisfy a screenshot request.
An explanatory summary under an image does not satisfy a translation request.

Use the exact manuscript version the user selected. Preserve the framing and
uncertainty of the source. Do not fix an author's equation, claim, awkward wording,
or table silently. Explain suspected errors in translator notes or analytical
commentary, with a source reference; leave the translation faithful.

Record source filename, PDF SHA256, page count, page dimensions, rendered pages,
region IDs, and rectangle coordinates. Use 1-indexed PDF file pages, distinct from
printed page labels. A crop is evidence for its visible content, not adjacent text.

## 2. Choose and render regions

First locate the passage using the environment's file tools. Inspect page images
for equations, diagrams, charts and tables. Use text extraction to assist reading,
not to reconstruct an image. Read the environment's PDF skill before PDF operations.

Select complete logical regions: paragraph with any continued sentence, equation
with its definition, chart with caption/axes/legend, or table with headers and notes.
For two-column or cross-page text, use separate ordered region IDs and link them.
Do not crop a figure so tightly that its denominator, legend or qualifying footnote
is missing. A sentence outside the crop is not part of that crop's translation.

Render genuine PDF pixels with `scripts/render_sources.py`. Do not use image
generation to recreate a source screenshot, apply retouching, or paint translated
text over the original. No OCR by default. For scans, inspect the pixels; use OCR
only as a necessary last resort and mark uncertain characters.

The script takes displayed-page point coordinates `[x0,y0,x1,y1]` with top-left
origin, not image pixels. Its page dimensions include page rotation. Default DPI is
200, with an allowed range of 96-400. Increase resolution when formulas are small.
A rotated source requires visual coordinate verification before selecting crops.

For documents of 20 pages or fewer, default to all original pages as context; for
long documents, default to referenced pages, listing coverage explicitly. A user
request for all pages takes precedence. Full-page viewing does not imply full-page
translation. Image payloads are deduplicated per page in the HTML.

## 3. Bind translations to exact images

Author the translations after reading the actual region and its source text. The
rendering, merging and exporting scripts do not translate or infer content.

Use one `screenshot_translations[id]` per region, with a translated title and typed
blocks. Include a source binding: screenshot ID, PDF page, exact crop rectangle,
and source PDF hash. Never attach a translation merely because the titles match.
Preserve paragraph order, headings, mathematical symbols, citation names and numbers.
Keep code identifiers, token strings and literal formatting samples unchanged when
translating them would change the described computation. Explain their meaning
separately rather than replacing the literal value.

Use `notes` for translator notes, explicitly labeled as not author text. Use
`related_ids` for cross-column/page continuations. For partially visible sentences,
retain the truncation and point to the continuation; do not silently insert unseen
text into the translation. Do not translate only a summary of a long screenshot.

A genuine unreadable region must use `status: unavailable` and a concrete reason.
Use a partial source layer with a reason, not filler content or a false full-coverage
claim. Never remove a difficult source region to make the coverage count look good.

## 4. Figures, tables, algorithms and continuations

- Paragraph: translate all visible sentences in order.
- Equation: preserve signs, subscripts, indices, sums, bounds and equation numbers;
  translate explanatory text separately. A generic regex formatter is not LaTeX.
  For complex mathematics, show the original plus a faithful text representation
  or use a verified offline renderer; never simplify the math silently.
- Figure: translate caption, axes, legends, labels and callouts using `pairs` blocks.
  Clearly distinguish visible labels from an explanatory reading of the figure.
- Table: translate headings/notes; retain every covered cell's value, decimal,
  uncertainty, model name, dash and unit. Distinguish percent from percentage points.
  Keep row/column associations. Wide tables should scroll horizontally.
- Algorithm: preserve symbols and control flow; translate comments and instructions.
  Do not turn an algorithm translation into a changed implementation.
- Literal example: preserve the literal sample when it demonstrates tokenization,
  whitespace or formatting; provide its translation alongside, not in its place.

Never infer missing numerical cells from surrounding prose. Formula and table
correctness requires visual comparison even when extraction appears clean.

## 5. User-interface behavior

Keep the code and author-argument tracks and all prior statement annotations.
Show source crops within author evidence and within the code view's paper tab.
Translations are visible by default immediately below the corresponding image;
collapsing is optional. The main code explanations must not become hidden.

The image viewer supports crop/full-page modes, zoom/fit, optional locator overlay,
page navigation, and synchronized translation selection. Use side-by-side columns
on desktop and stacked regions on mobile. The overlay must not alter stored pixels.
Provide a source-translation index grouped by PDF page. Retain stable region IDs.
When the full page is visible, state that the translation belongs only to the
selected region. When no region is selected, list available translated regions on
that page or explicitly state that no translation is provided there.

No placeholder page counts, paper-specific filenames, or fixed region counts in
generic templates. Derive coverage from authored data. Embed pixels and text for
offline reading; external source links may still need the network.

## 6. Commands and deliverables

Prepare `regions.json` and `translations.json` using the schema in
`references/source-layer-schema.md`. Add `shot_ids` to the analysis's paper points
and author-argument references. Then:

```bash
python scripts/render_sources.py --pdf paper.pdf --regions regions.json --output-dir source_images --dpi 200
python scripts/merge_sources.py --analysis analysis.json --sources source_images/source_layer.json --translations translations.json --output analysis_bilingual.json
python scripts/build_reader.py --input analysis_bilingual.json --output reader.html --source-pdf paper.pdf --report validation.json
python scripts/export_translations.py --input analysis_bilingual.json --output translations_zh.md
```

Add `--repo-root` to the builder only with a checked source tree. If coverage is
incomplete, `merge_sources.py --partial-reason "..."` requires an honest reason;
it does not repair broken source bindings or permit fabricated image references.

Deliver the HTML and a brief scope note. A requested full report bundle can contain
analysis JSON, copyable translation Markdown/JSON, source manifest, screenshots,
and the provided original PDF. Keep generated report bundles separate from the
installable Skill archive. Do not package model checkpoints, dependencies, secrets,
font files, browser caches or unrelated user files.

## 7. Manual verification

Open at least one paragraph, figure, table, equation and algorithm region when
present; verify text, crop boundaries and numeric fidelity. Check cross-page links,
missing-source fallbacks, image/translation synchronization, desktop/mobile layouts,
keyboard focus, offline loading and the distinction between full-page context and
regional translation. Test all referenced IDs, not only the first sample.

The validator checks source bindings, referenced IDs, dimensions, rectangular tables,
missing content and optional local PDF hash. It cannot certify faithful translation,
correct research conclusions, source-image fidelity or model reproduction. Label
those unverified boundaries explicitly in validation reports and in final delivery.


## Target-language selection

Do not hard-code Chinese into screenshot translation labels. For a multilingual
reader, use the independent source-text selector and region packs in
`references/language-selection.md`. Preserve exact source bindings in every pack.
Showing an English screenshot as English copyable text is original-language
transcription, not translation. Provide missing-language notices rather than
automatic fallback. Do not generate an unseen language in browser JavaScript.
