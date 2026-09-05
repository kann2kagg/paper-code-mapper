# Source-layer schema 1.2

Extend the existing reader schema; do not replace `lessons`, `paperPoints` or
`argument`. Version 1.0/1.1 remain accepted for old readers, but new bilingual
readers use 1.2. Content strings are escaped as text, never executed as HTML/JS.

## Required coverage record

```json
{
  "schema_version": "1.2",
  "source_layer": {
    "status": "provided",
    "source_language": "en",
    "translation_language": "zh-CN"
  }
}
```

Use `partial`, `unavailable` or `not-requested` only with a nonempty `reason`.
`provided` requires source regions and translated content for every cited paper
location. For a code-only task with no paper, use `not-requested` and say why.
Do not claim complete manuscript coverage from complete selected-region coverage.

## Authored region input for render_sources.py

```json
{"regions": [{
  "id": "method-intro", "page": 4,
  "title": "Section 4.1, introductory paragraph",
  "clip": [301, 358, 533, 584],
  "note": "Example coordinates only; replace with inspected PDF coordinates."
}]}
```

`page` is the 1-indexed PDF file page. `clip` is the displayed page's point-space
rectangle, not normalized coordinates, image pixels or a guessed bounding box.
IDs must be unique and use letters, numbers, underscore, hyphen or dot.

The renderer outputs `images` (page ID -> embedded lossless WebP), `sizes`
(page ID -> `[width,height]` in PDF points), `screenshots` (region ID -> region),
and `screenshot_provenance` (real source hash and rendering metadata).

## Authored translation input for merge_sources.py

```json
{
  "method-intro": {
    "status": "translated",
    "title_target": "Translated section title",
    "blocks": [
      {"type": "paragraph", "text": "Faithful translation of the visible paragraph."},
      {"type": "equation", "text": "L = a + b  (1)"},
      {"type": "pairs", "title": "Figure labels", "rows": [["Input", "Translated Input"]]},
      {"type": "table", "headers": ["Method", "Value"], "rows": [["A", "10.2"]]}
    ],
    "notes": ["Clearly labeled translator note, not an author statement."],
    "related_ids": [],
    "source": {
      "screenshot_id": "method-intro",
      "pdf_page": 4,
      "clip_pdf_points": [301, 358, 533, 584],
      "pdf_sha256": "REPLACE_WITH_ACTUAL_SOURCE_SHA256"
    }
  }
}
```

The example's prose, formula, number and coordinates are schema illustrations,
not evidence for any manuscript. Populate all fields from the actual source.
Allowed block types: `paragraph`, `heading`, `equation`, `code` (nonempty text);
`pairs` (title and two-column string rows); `table` (nonempty string headers and
same-width string rows). Use `variant: prose` for long textual table cells.
`title_zh` is accepted as a legacy alias for `title_target`.

An unreadable region uses `{"status":"unavailable","reason":"Specific reason"}`
and the overall source layer must be `partial`. Do not fill `blocks` with a summary
to pass validation. Missing source files should be disclosed, not recreated.

## Bind both tracks

Add `"shot_ids": ["method-intro"]` to a `paperPoints` item and to the relevant
`argument.nodes[].references[]`. The reference's primary `page` must occur among
the linked screenshots. Other region IDs may supply continuations on later pages.
Several code blocks may share one region; several regions may support one argument.

## Integrity and validation boundaries

`source_pdf_hash_checked` means only that the supplied local PDF bytes match the
recorded SHA256. Image headers and optional page image hashes are checked. Image
semantics and translated numerical/textual fidelity remain a separate visual task.
The generated reports explicitly retain `translation_semantics_checked: false`
and `source_pixels_reverified: false`; do not reinterpret a schema pass as either.

`build_reader.py` injects generic locale strings from `assets/source-ui.json` and
derives page/region/translation counts from data. It does not reuse a demonstration's
38-region/12-page counts or overwrite source text with an interpretation.
