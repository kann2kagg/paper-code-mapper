# Repository Inspection Checklist

Use this checklist when a repository contains enough indirection that a superficial grep could be misleading.

## Entrypoints
- README experiment command
- shell launchers
- Python `main`
- argparse/absl/Hydra/gin/config loaders
- notebook-only paths vs production paths

## Configuration
- base/default config
- experiment-specific config
- model-specific config
- environment variables
- CLI overrides
- checkpoint config
- conditional overrides inside functions

## Call graph
- direct callers
- factory/registry selection
- subclass overrides
- imported aliases
- dynamically loaded modules
- callbacks/hooks

## Objective and gradients
- exact objective expression
- slice/mask
- logits shift
- reduction
- weights
- detached tensors
- `no_grad` regions
- `backward`, `autograd.grad`, or custom gradient
- proposal loss vs ranking loss

## Tokenization and templates
- tokenizer class/checkpoint
- BOS/EOS
- chat template
- role separators
- target prefix
- token slice boundaries
- padding side and attention mask

## Data
- dataset path
- columns/schema
- preprocessing
- sample selection
- train/test split
- target construction

## Runtime verification
- parameter is actually consumed
- branch is reachable
- official script selects this implementation
- value is not overwritten later
- code is not legacy/dead

## Paper-code consistency
- main-text method
- appendix implementation details
- released code behavior
- paper table hyperparameters
- README reproduction command

## Code-first teaching requirements
- File/function navigation takes priority over paper chapters.
- Every meaningful displayed statement has its own actual explanation.
- Explain language syntax, operands, state transitions, and result consumers.
- Explain code even when it has no direct paper counterpart.
- Keep source excerpts distinct from pseudocode and synthetic examples.
- Mark separate entrypoints instead of inventing one continuous call chain.
- Distinguish study-row numbering from verified repository line numbers.
- Use the observed revision; never copy example-specific constants into a new run.
- Validate the generated reader, then manually check paper/code claims.
- State which tests were executed and which dependencies remain unverified.
