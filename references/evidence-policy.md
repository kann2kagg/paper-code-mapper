# Source and Verification Policy

## Provenance

Use the requested paper version and repository revision. Keep manuscript claims,
released-code behavior, and actual execution results separate. Read the sources,
not only generated summaries. A provided code reader is a useful design example,
not proof that a new checkout has the same behavior.

For source excerpts, retain path and real line range when known. Re-read ranges from
the pinned local file or source view. Never label study numbering as file numbering.
Do not add invented `...` inside a "verbatim" range. Split non-contiguous excerpts
into separate rows/ranges and state what was omitted.

For a local source archive with no revision metadata, record an unpinned archive;
do not infer a Git commit from its name. Keep generated source URLs optional rather
than filling in a plausible but unverified location.

## Comparison status

- Exact match: the traced operation and paper statement agree in the selected path.
- Equivalent implementation: establish mathematical equivalence under stated
  assumptions, such as fixed sequence length; do not generalize without proof.
- Partial match: only part of the paper mechanism appears in the inspected path.
- Runtime override: a later value changes a default before it is consumed.
- Implementation extension: released code adds behavior not described there.
- Potential mismatch: evidence conflicts; explain possible reproduction impact.
- No direct paper counterpart: infrastructure or unmentioned implementation detail.
- Unresolved: evidence is unavailable or ambiguous.

## Running and reproducing

Describe a repository command as documented unless it was actually run. Before
execution, inspect it for downloads, destructive changes, secrets, or external side
effects. Respect permissions and the user's source/access boundaries.

A useful running guide separates: working directory, interpreter/environment,
configuration and checkpoints, preparation data, selected entrypoint, expected
artifacts, and a safe sanity check. Mark missing values instead of inventing paths,
credentials, hardware requirements, or dependency pins.

Running a synthetic calculation only verifies that calculation. A renderer smoke
test only verifies its UI. Neither reproduces a paper table or audits external
libraries. Report failed tests and unsupported environments honestly.

## Figures, citations, and distribution

Use real PDF page indexes and printed page labels distinctly. Inspect graphics when
the claim depends on them. Include only necessary excerpts or crops; do not attach
unneeded full papers, model weights, credentials, private data, or font files.

Chat citations must use genuine tool citation markers. HTML can use verified source
links plus visible page/section/range labels. Do not copy a synthetic tool marker
into a generated page and pretend it is a resolvable source.

## Claims about author reasoning
An exact code-paper correspondence establishes an implementation relationship,
not the truth of the paper's causal explanation. Label analyst-created argument
edges. Never silently add background reasoning to fill a manuscript gap. Preserve
parallel constraints, conditional design choices, negative ablations and limits.
