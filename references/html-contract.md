# Interactive Reader Contract

## Contents
1. Build and test
2. Root data
3. Reading units and statements
4. Examples and paper evidence
5. Renderer guarantees and limitations
6. Historical design exemplar
7. Author-argument schema 1.1

## 1. Build and test

Use Python 3.10 or newer. The builder uses only the standard library. Run commands
from the skill directory, or replace the relative script path with its absolute path.

```bash
python scripts/build_reader.py --input /mnt/data/analysis.json --output /mnt/data/code_reader.html
```

With a local source tree, verify the exact excerpts before rendering:

```bash
python scripts/build_reader.py --input /mnt/data/analysis.json --repo-root /mnt/data/repo --output /mnt/data/code_reader.html --report /mnt/data/reader_validation.json
```

Run the bundled example and renderer regression tests:

```bash
python scripts/build_reader.py --input assets/examples/minimal_reader.json --repo-root assets/examples --output /mnt/data/example_reader.html
python -m unittest discover -s tests -v
```

A validation error exits without creating a new HTML file. Inspect the errors,
correct the source data, and re-run. Do not fill a required explanation with vague
boilerplate just to satisfy the schema.

## 2. Root data

Start from `assets/examples/minimal_reader.json`, an original harmless fixture.
Replace its data with verified analysis; never copy it as repository evidence.

```json
{
  "schema_version": "1.1",
  "language": "zh-CN",
  "title": "Project / code-first walkthrough",
  "repository": {"url": "", "commit": ""},
  "paper": {"title": "", "version": "", "url": ""},
  "scope": "State the selected experiment and what remains uninspected.",
  "evidence_level": "Static source inspection; no model experiment run.",
  "default_lesson": "entry",
  "lessons": [],
  "paperPoints": [],
  "images": {},
  "sizes": {}
}
```

Supply at least one lesson. Empty source URLs and commits are honest when unknown;
do not invent them. `language` selects Chinese or English interface labels. Write
all explanations in the user's language; for other languages, add and review the
locale in `assets/ui.json` and update validation before generating that locale.

## 3. Reading units and statements

Each lesson needs:

- `id`: unique letters/numbers/dot/underscore/hyphen, used in navigation anchors.
- `title`, `file`, optional `symbol`: code-focused labels, actual repository path.
- `entry_kind`: `main-path`, `preparation`, `evaluation`, `utility`, or `teaching`.
- `role`, `before`, `after`: local purpose and actual state/return semantics.
- `chain`: nonempty array of readable upstream/downstream steps. Describe missing
  caller information instead of fabricating a call chain.
- `variables`: arrays of `[identifier, explanation]` with concrete contextual meaning.
- `blocks`: one or more coherent code blocks.
- `example`: explanatory text or authored step states (see below).
- `papers`: zero-based indexes into `paperPoints`; use `[]` when there is no evidence.
- `caution`: material boundary or source uncertainty, not generic filler.

Every code block has `title`, `path`, `summary`, `source_kind`, `url`, `rows`, and
optional `symbol` and `note`. `source_kind` is one of:

| Kind | Meaning |
|---|---|
| `verbatim` | Actual source; requires a real inclusive line range for every row |
| `pseudocode` | Clearly labeled paraphrase, not an exact repository excerpt |
| `teaching` | Independent illustrative code; never attributed as original source |

Do not relabel unverified source as "teaching" to conceal missing evidence. If it
is intended to be original source, retrieve and check it or state the gap.

Every row has nonempty `code`, `meaning`, `why`, `result`. A verbatim row also has
positive inclusive `start_line` and `end_line`. An annotation can represent several
physical lines of a single logical expression. The number of *annotations* must
not be advertised as the number of physical source lines.

```json
{
  "code": "    selected = values[:limit]",
  "start_line": 4,
  "end_line": 4,
  "meaning": "Take the list from index 0 up to, but excluding, limit.",
  "why": "Use the requested prefix without modifying the original list.",
  "result": "For values=[2,4,8] and limit=2, selected becomes [2,4]."
}
```

Verbatim comparison preserves indentation and physical line breaks, normalizing
only line endings and a trailing newline. Split non-contiguous source into separate
rows and explain the gap in the block note. Do not insert `...` and then claim an
exact source range. Local symlinks resolving outside the selected repository are
rejected by the range checker.

## 4. Examples and paper evidence

An example may be a string, or use authored steps:

```json
{
  "kind": "steps",
  "steps": [
    {"title": "Before", "state": "values = [2, 4, 8]", "explanation": "Input state."},
    {"title": "After", "state": "selected = [2, 4]", "explanation": "The original list is unchanged."}
  ]
}
```

The UI advances through these texts. It never evaluates repository code in the
browser. Such steps do not establish observed runtime behavior.

Each `paperPoints` object requires `section`, `page`, `paperSummary`, `relation`,
`status`, and an optional `paperUrl`. The page is a real 1-indexed PDF page. Use the
status vocabulary in `references/evidence-policy.md`. The `relation` must explain
what exact code behavior corresponds to the cited claim, not just repeat a title.

Optionally include a minimal `quote`, and provide paper imagery:

- `images["4"]`: a base64 data URI containing a PNG, JPEG, or WebP page image.
- `sizes["4"]`: `[page_width, page_height]` in the same coordinates as the boxes.
- point `clip`: `[x0, y0, x1, y1]` defining the displayed crop.
- point `rect`: an optional highlight rectangle in page coordinates.

Only add observed locations and verified excerpts. Do not invent a sample paper
page to fill an empty panel. When no paper has been supplied, leave the paper arrays
empty and say what remains unavailable. Avoid bundling full papers unnecessarily.

## 5. Renderer guarantees and limitations

The renderer supplies dynamic file/function navigation, visible statement
annotations, code-block tabs, search, hash anchors, previous/next navigation,
variables/examples/paper tabs, a reading-route dialog, and responsive layouts.
Its layout is derived from the user's code-first reader, not the earlier
paper-first locator.

The builder rejects missing annotations, broken paper indexes, unsafe source paths,
and non-http(s) links. It escapes data before embedding it into HTML and uses
text escaping when rendering code and explanations. It performs no network
requests, dependency installation, model loading, or repository execution.

These checks do not establish semantic correctness or paper-code equivalence.
`--repo-root` compares snippets but does not prove the directory's Git revision.
Resolve `git rev-parse HEAD` separately when that provenance is available.

## 6. Historical design exemplar
7. Author-argument schema 1.1

`assets/examples/transferattack_code_first_reader.html` preserves the existing
Chinese reader from this conversation: 10 units, 27 blocks, 93 annotated statements
or multiline expressions. Its commit and paper values belong only to that example.
It is supplied as a layout and teaching-pattern reference, not as a newly verified
repository analysis. Do not propagate its constants into a different task.


## 7. Author-argument schema 1.1

Use schema 1.1 for new readers. Version 1.0 remains accepted for legacy data, but
local paper links alone generate a warning. If 1.1 records a paper title, provide
`argument` or explicitly mark it unavailable with a nonempty `reason`.
`default_view` can be `code` or `argument`; respect a selected-function request.
For a project walkthrough, use the argument overview as a compact orientation,
not as a replacement for detailed code annotations.

An absent paper must not produce an invented argument:

```json
{"argument": {"status": "unavailable", "reason": "No manuscript was supplied."}}
```

For a supplied manuscript, use this shape (placeholders are not evidence):

```json
{
  "argument": {
    "status": "provided",
    "title": "The author's reasoning",
    "question": "The source's research question",
    "takeaway": "A bounded, source-supported explanation of the complete idea",
    "scope": "Manuscript identity, inspected sections, and unverified aspects",
    "default_node": "design",
    "nodes": [{
      "id": "design",
      "title": "A source-supported design choice",
      "stage": "Method",
      "basis": "author-stated",
      "question": "What does this step need to answer?",
      "claim": "What the authors assert, without adding missing reasoning",
      "because": "Its connection to the preceding diagnosis",
      "consequence": "The next design or test it motivates",
      "boundary": "What the evidence does not establish",
      "references": [{"page": 4, "section": "Section to verify",
        "locator": "Actual paragraph, equation, table or visible line range",
        "url": ""}],
      "code_links": [{"lesson": "entry", "block": 0,
        "role": "configures", "explanation": "Explain the actual relationship"}]
    }],
    "edges": []
  }
}
```

`basis` must be `author-stated`, `source-analysis`, or `teaching`. Source-based nodes
require references with a positive PDF page and a nonempty section/locator.
The validator checks presence and structure, not truth or source accessibility.

`code_links[].lesson` names an existing unit; optional `block` is a zero-based
block index. Roles are `implements`, `configures`, `measures`, `infrastructure`.
Provide `code_note` when there is no direct code correspondence. Derive reverse
links from these same entries, never maintain a second contradictory mapping.

Each edge requires `from`, `to` (node IDs), `relation`, `explanation`, and `basis`.
Attribute analyst-created connections as `source-analysis`. A diagrammed edge
must not imply a theorem, causal proof, or function call absent from the source.

The template embeds `assets/argument-view.css` and `assets/argument-view.js` into
one HTML output. View switching preserves the code block; argument links open the
specific block, and its context strip provides a return to the argument. Deep links
use `#logic=node-id`; ordinary code anchors remain `#lesson-id`. A local paper
thumbnail alone does not satisfy the complete-author-argument requirement.

`assets/examples/transferattack_argument.json` contains the manuscript-grounded
argument used in the historical design exemplar. It names that exemplar's lesson
IDs and must not be copied onto unrelated repositories. Its code statements are
carried from the earlier output, not freshly range-verified by this update.


Optional browser checks (requires Playwright and an available Chromium binary):

```bash
python tests/browser_check.py --output-dir /mnt/data/reader_browser_checks
```

Use `--executable /path/to/chromium` only when that browser exists. The browser
receives the generated HTML via `set_content` on a blank page; no remote source
site or inspected repository is executed. Inspect screenshots after layout changes.
The browser tests cover both the historical example and the current generic
renderer. Unit tests do not need a browser.

## Schema 1.2: source screenshots and bilingual evidence

Use `references/source-layer-schema.md` for the new fields, and
`references/screenshots-and-translation.md` for region selection and translation.
New outputs retain the code/argument schema and add explicit coverage, real source
pixels, synchronized region translations, page context and a translation index.
Use the provided render/merge/build/export pipeline; never mock the source panel.
Older 1.0/1.1 data remain supported without an unearned complete-source claim.


## Selectable languages (localization extension 1.0)

Add `localization` to a schema-1.2 document to enable the two language selectors.
See `references/language-selection.md` for the full contract. Keep code/source
content shared; provide complete prose patches per reading language and independent
region-text packs per translation language. Every code view and argument node must
change language, not only the interface labels. The existing single-language schema
and builder commands remain supported. The language shell saves preferences when
storage is available and restores code, argument and source-view state.
