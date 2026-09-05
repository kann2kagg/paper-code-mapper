# Code-First Output Template

## Whole-project reader

### Header
Project, observed revision, selected path, evidence level, and uninspected scope.

### Left: code navigation
Group by actual file and function. Offer an execution-order guide, but label
preparation and evaluation scripts as separate entrypoints. Allow search by file,
function, identifier, and explanation. Start at a user-selected function when given.

### Center: code and explanation
For each reading unit:

1. File/function and one-sentence role.
2. Inputs and initial state.
3. Switchable coherent source blocks, each with:
   - real source location / explicitly labeled pseudocode;
   - visible code;
   - adjacent syntax/variable/operation explanation;
   - computational role;
   - resulting value, shape, state, or control flow.
4. Before/after state and next consumer.
5. Previous/next reading-unit navigation.

### Right: supporting panels
Variables, small examples, and paper correspondence. Do not make the paper the
primary navigation or open a paper mapping table as the default main view.

For a paper correspondence, state the paper page and section/equation/algorithm,
which code behavior it supports, comparison status, and the source link/citation.
If the paper does not directly specify engineering logic, say so explicitly.

### Footer
Scope, static versus executed evidence, available source revision, unresolved
prerequisites. Do not claim a browser preview is an executed model experiment.

## Focused chat explanation

Begin with the function and what happens to its input. Show the selected coherent
code block and explain its meaningful statements in execution order. Use a compact
code/explanation table only when it is easier to read than prose.

Then show a harmless before/after example, the caller and result consumer, and the
paper correspondence. End with any uncertainty that changes the conclusion. Do not
start with a survey of unrelated paper sections.

## Final delivery

Link the completed HTML and briefly name the included core path and limitations.
Do not repeat the entire reader in chat. For a request to package this workflow as
a skill, provide the complete validated skill archive instead of only its prompt.

## Parallel author-argument track
Provide a compact research orientation plus an independently navigable argument.
For each node: question -> author claim -> preceding rationale -> next implication
-> source evidence -> bounded conclusion -> linked code blocks. Above each code
block, show its argument role and a return link. Do not replace the code route.
Use `references/argument-guide.md` for the evidence and transition rules.

## Original source and translation panel

For each mapped paper location, show the actual screenshot, PDF page/section and
faithful translated text. Provide crop/full-page and enlarged bilingual modes.
Keep translated content separate from the argument's interpretation and boundary.
Include a region translation index; retain code annotations and argument/code links.
Full-page viewing must explain that translation covers only the selected region.
In chat delivery, link the actual artifact and name meaningful omissions; do not
repeat the entire document or claim that creating this reader ran the experiment.
