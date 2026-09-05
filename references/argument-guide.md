# Preserve the Author Argument

## Two orders, not one
Keep executable order (launcher -> functions -> state changes) separate from
research reasoning (observation -> proposed explanation -> intervention -> tests
-> bounded conclusion). Allow either view to navigate to the other. Do not turn
one into the other by sorting files in paper-section order.

## Build a supported argument
Read the relevant continuous manuscript sections, not only isolated search hits.
Preserve the source's terminology, scope, assumptions and level of certainty.
For every node record:
- Question: what does this part need to explain?
- Claim: what do the authors actually assert?
- Because: how does it follow from the preceding part?
- Consequence: why is the next design or experiment introduced?
- Basis: author-stated / source-analysis / teaching.
- References: manuscript version, PDF page, section or figure/table and locator.
- Boundary: what remains assumed, untested, or unsupported?

Label transitions too. A motivating observation is not a proof; two successive
sections do not necessarily have a causal dependency. Mark an analyst's proposed
connection as source-analysis. If the manuscript skips a justification, write
"The supplied text does not establish this step" instead of filling it silently.

## Preserve the purpose of experiments
For each major comparison or ablation explain the tested claim, varied factor,
reported observation, inference allowed by the authors' evidence, and limits.
Do not claim a model implementation reproduces a result just because it computes
the right metric. Distinguish source performance, transfer performance, surrogate
loss, generation examples, and classifier-based success.

## Map both directions
Use explicit link roles:
- implements: this code performs a proposed computation;
- configures: this code selects a tested condition or hyperparameter;
- measures: this code produces a metric used in evaluation;
- infrastructure: this code enables execution but is not itself a novel method.

Link to a block, not only a filename, where the evidence supports it. One design can
need multiple code blocks; one block can realize multiple design choices. Derive
reverse links from the same data to prevent contradictory hand-maintained maps.
If a node has no code, explain why. If code has no research counterpart, say so.

## Teaching presentation
Keep code-plus-explanation visible. Above a code block show its research purpose
and a one-click return to the relevant argument node. In the argument view show
problem, reasoning, evidence and boundaries, with specific code links. Do not hide
the author's logic in an optional footnote or replace it with a list of headings.

For whole-project teaching start with a compact orientation, then let the reader
choose the executable route or argument route. For a requested function open the
code directly, retaining the global argument as an accessible parallel view.

## Anti-patterns
"This loss maps to Equation 3" is insufficient without explaining what problem
motivated that loss and which experiment bears on its benefit.
"It works, therefore the proposed mechanism is true" overstates evidence.
"First run preparation, then main calls evaluation" invents runtime relations
when these are independent entrypoints.
"Every line must implement a paper sentence" mislabels engineering code.

## Source-based example
In the supplied TransferAttack v1, preserve the distinction between its shared
feasible-region conceptual framework, two proposed superfluous constraints,
target guidance plus relaxed loss, and empirical transfer/ablation evidence.
The shared-region picture is not a proved theorem. Shorter loss alone is not the
same intervention as guidance plus shorter loss. Report model-dependent effects
and the stronger-target limitations rather than promising universal transfer.
Use the paper itself as the evidence; this example is not a substitute for it.
