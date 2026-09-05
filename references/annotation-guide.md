# Statement-Level Teaching Guide

## Read a unit in this order

1. Locate the file, enclosing function/class, and reachable caller.
2. State the inputs and current object/tensor state.
3. Show the smallest coherent code block.
4. Explain each displayed operation immediately next to that operation.
5. Show changed values or state with a harmless concrete example.
6. State what receives the result.
7. Only then connect it to paper evidence.

## Required annotation granularity

One annotation row represents one statement or a tightly coupled multiline
expression. Combine the argument lines of a single call; do not combine a loop,
loss calculation, backward pass, and candidate selection into "optimization".
Explain each control-flow change and each meaningful transformation separately.

Every row has `code`, `meaning`, `why`, and `result`. Empty `result` is not a shortcut:
for an import say a name is bound; for a definition say the body has not run yet;
for a condition say which branch is selected under the observed value.

A call graph is useful context but does not replace these annotations.

## Example: explain code, not the paper slogan

Teaching-only pseudocode (do not present as a repository excerpt):

```python
if self.use_prefix:
    text = f"{self.context} {self.question}"
else:
    text = f"{self.question} {self.context}"
```

Poor: "This implements prefix prompting."

Better:
- `self` refers to the current object. `self.use_prefix` reads its Boolean attribute;
  it does not create a new parameter. Under `True`, only the first branch runs.
- The `f` string evaluates the two expressions inside braces and interpolates their
  string representations in the displayed order. The space is literal text.
- `text = ...` binds the resulting string to the local name `text`; it does not call
  a model, update weights, or by itself mutate a conversation template.
- With `context="Be brief."` and `question="What is basil?"`, the first branch
  produces `Be brief. What is basil?`; the other produces the reversed order.
- The next consumer is unknown until the following call is inspected.

Contrast with `template.update_last_message(text)`: inspect the method before
claiming it mutates the template or returns a value. The name alone is not evidence.

## Language and object constructs

Explain only what is needed at the line:

| Construct | Explain |
|---|---|
| `self.x`, `obj.x` | Which instance and attribute; where the value was set |
| `def`, `class` | Definition versus execution; constructor and instance state |
| `a = b`, `a[:] = b` | Rebinding versus mutation; aliases where relevant |
| `*args`, `**kwargs` | Arguments reaching the selected caller/callee |
| `if` / `else` | Effective predicate, selected branch, skipped branch |
| `return` | Exact result and consumer, not just "returns data" |
| decorator/property | Hidden dispatch or setter effects |
| process/queue | Which process does work, how results are collected |
| Shell `$1`, `${x}`, `\` | Position argument, interpolation, continuation |
| relative path | Working directory, not assumed script directory |

## Tensors and losses

For `logits[:, loss_slice, :].transpose(1, 2)`, explain all axes and the shape
transition; do not just translate it as "transpose logits".

For `slice(10, 12)`, show the included positions 10 and 11 and excluded position 12.
For a causal shift, pair labels with predicting logit positions explicitly. A
synthetic index diagram is not proof of real tokenizer segmentation.

For `mean(dim=-1)`, say which dimension is averaged, what survives, and whether
examples with different lengths receive different weights. Do not assume a sum and
mean are equivalent when lengths or downstream coefficients differ.

For `.backward()`, identify differentiable leaves and which parameters are frozen,
not merely the model used for forward computation. Separate code observations from
claims about a whole unexecuted experiment.

## Keeping a reader usable

Use a small code block followed by adjacent explanations, not a wall of inline
comments inserted into the original source. Preserve the source verbatim; place
teaching text outside it. Distinguish study-row numbers from real file line numbers.
Keep before/after states visible. Place uncommon syntax, long tensor derivations,
and paper paragraphs in secondary panels without hiding the core explanation.

## Two different meanings of "why"
Keep a statement's local `why` explanation (why this computation is here) separate
from the authors' research rationale (which hypothesis or design motivates it).
The latter belongs in an evidence-backed argument node. Never infer author intent
solely from the implementation. Both explanations should be easy to reach.
