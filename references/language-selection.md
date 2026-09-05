# Selectable reading and source-text languages

## Output behavior

Expose two persistent, labeled selectors above the reader:

- **Reading language** changes interface labels, statement explanations, variable
  descriptions, before/after explanations, examples, paper commentary, and the
  author-argument track together. Changing only buttons is not a translated reader.
- **Source / translation language** independently chooses an authored region
  translation or an original-language transcript. Show the language and content
  type next to the region. English source text shown in English is a transcript,
  not an English translation.

Keep original PDF pixels, quotations, code, identifiers, numerical data, equations,
page/crop coordinates, provenance, source ranges, lesson IDs and argument-link IDs
unchanged. Keep original-language screenshot titles as provenance; localized
region titles come from the selected text pack. Keep source/transcript/translation,
translator notes, research interpretation and code explanations visibly distinct.

For this ongoing workflow, prepare Simplified Chinese (`zh-CN`) and English (`en`)
reading versions by default, opening in the user's current language. Honor any
explicit list or a request for only one language. For a new target language, author
all corresponding content and reviewed UI catalogs before offering it. Ask only
when the desired language cannot be inferred and the ambiguity matters.

Only list languages that are included in the artifact. Do not expose decorative
language names or claim that an offline HTML file translates unseen content. No
translation API, browser auto-translation, or external CDN is used. Explain that
additional languages must be generated into the reader first. Keep language
preferences in namespaced localStorage when the browser permits it; handle blocked
storage without errors. Preserve the selected code block, argument node, example
step, source region, full-page/crop mode and zoom when a language changes.

## Authored-data contract

Retain schema `1.2` and its shared source data. Add an optional `localization`
object with `version: "1.0"`. Existing single-language files stay valid.

```json
{
  "language": "en",
  "localization": {
    "version": "1.0",
    "default_reading": "zh-CN",
    "default_translation": "zh-CN",
    "readings": {
      "en": {"label": "English", "patch": {}},
      "zh-CN": {"label": "Simplified Chinese", "patch": {
        "/title": "A human-authored translated title"
      }}
    },
    "translations": {
      "zh-CN": {"label": "Simplified Chinese", "mode": "translation", "regions": {}},
      "en": {"label": "English", "mode": "transcription", "regions": {}}
    }
  }
}
```

This is a structural illustration, not complete valid data: include **every**
required prose path and selected region. The full tested example is
`assets/examples/multilingual_fixture.json`.

The base `language` refers to the language in the root authored analysis. Its
reading entry uses an empty patch. Each additional language supplies all nonempty
paths returned by `scripts/language_support.py:prose_fields`. Patches can replace
only these human-language leaves, not code, IDs, graph topology, source URLs,
images, quotations, numeric values or metadata. Do not change code to make a
translation read more naturally. Keep literal teaching-state strings unchanged;
translate their adjacent explanation instead.

Each source-text pack has a `regions` dictionary keyed by the same screenshot IDs
as `screenshots`. Every record preserves the existing source binding: PDF hash,
page, crop rectangle and screenshot ID. Use the established translation block
schema. `mode` is `translation` or `transcription`; transcription must use the
recorded source language. Missing text is an explicit `status: "unavailable"`
record with a reason, not a silent fallback to another language.

Built-in UI catalogs exist for `zh-CN` and `en`. To add another reading language,
provide `readings[tag].ui` with complete `reader`, `source`, `argument`, and `shell`
catalogs matching `assets/ui.json`, `assets/source-ui.json`,
`assets/argument-ui.json`, and `assets/language-ui.json`. These must actually be
translated and reviewed, not copied English with a new language name. The schema
can check completeness but cannot establish linguistic quality. Additional
source-text languages do not require another reading-interface locale.

## Build and export

Inventory prose that needs translation:

```bash
python scripts/list_locale_fields.py --input analysis_bilingual.json --output prose_inventory.json
```

The inventory is source text, **not** an automatically translated pack. Author the
translations, source-text packs and localization object, then build normally:

```bash
python scripts/build_reader.py --input analysis_multilingual.json --output reader.html --source-pdf paper.pdf --report validation.json
python scripts/export_translations.py --input analysis_multilingual.json --language zh-CN --output selected_regions_zh.md
python scripts/export_translations.py --input analysis_multilingual.json --language en --output selected_regions_en.md
```

The builder uses one shared source document and one template inside an offline
language-selector shell. It rebuilds the selected reading view from validated
prose patches and restores the reading state. Source images are embedded once,
not copied for every language combination. Parent/child messages are limited to
reading anchors and checked against the expected frame. JSON is escaped before
embedding; strings render through existing escaping functions.

## Verification

Run the complete existing suite plus `tests/test_languages.py`. Verify that missing
prose, unknown locales, illegal code/image/ID patches, wrong PDF bindings, changed
equations and modified numerical table values are rejected. Check explicit missing
translations, correct transcript labels and language-specific Markdown export.

Run `tests/browser_languages.py --html reader.html --output-dir browser_checks` on
the bundled multilingual fixture. Inspect desktop/mobile screenshots. Verify code
and argument translations, independent source-text selection, preserved reading
state, synchronized source-region text, full-page context, zoom, no unexpected
network requests and graceful behavior when storage is unavailable. The fixture
uses independent teaching code and PDF content, not the research paper.

A structure check does not certify that every sentence is a faithful translation.
Review source-specific terminology, formatting literals, claims, numbers and
qualifications across languages before describing a language as ready.
