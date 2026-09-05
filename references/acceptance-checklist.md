# Acceptance Scenarios

Use these scenarios for manual checks after changing this skill. They are not claims
that external repositories or published experiments were executed.

## 1. Beginner asks about a selected function
Input: repository and paper plus "Explain this function; I do not know Python."
Expected: open at the function; explain every displayed meaningful statement,
identifiers, branch, input state, and return/side effect; then attach paper evidence.
Reject: a call graph and "this implements the method" without code explanation.

## 2. User wants the whole project
Input: repository URL and manuscript.
Expected: inspect the actual entrypoint, dynamically selected classes, effective
configuration and core data flow; organize the reader by code files/functions.
Mark independent data preparation and evaluation scripts explicitly.
Reject: a paper-section table as the default main navigation.

## 3. No paper counterpart
Input: user selects imports, a constructor, cleanup, or CLI parsing.
Expected: explain that code anyway; label absent paper correspondence honestly.
Reject: assigning a convenient equation merely because a paper was supplied.

## 4. Conflicting default and launcher
Input: a parameter is 8 by default but 2 in the selected launch command.
Expected: follow the value to its consumer and explain how the branch uses it.
Reject: reporting the first occurrence as the experiment setting.

## 5. Token-level target range
Input: user asks which target positions contribute to the objective.
Expected: explain half-open slices, shifted logits, axes and reduction, gradient
recipient, and any difference between proposal/ranking/evaluation functions.
Reject: "first two words" without actual tokenization evidence.

## 6. Missing source or browser
Input: code source is inaccessible, or no browser is available to check HTML.
Expected: label the evidence gap; analyze what was actually read; report whether
rendering, syntax checks, source checks, or numerical tests ran separately.
Reject: simulated access, made-up line ranges, or claims of a successful experiment.

## 7. Reader editing
Input: an existing reader plus "there is still no code explanation".
Expected: edit the actual artifact and add adjacent meaning/why/result annotations.
Reject: promising a change, merely adding another summary paragraph, or linking
an unchanged/unverified file.

## Author argument acceptance
- Can the reader state the research problem and why the authors propose the design?
- Are observations, hypotheses, method steps, evidence and limitations distinguished?
- Does each experiment answer a specific claim rather than just supply a score?
- Do node-to-code links and reverse block-context links work?
- Is conceptual argument order distinct from actual call order?
- Are unsupported motives, missing justifications and analyst inferences marked?
- Does the code view retain all statement-level explanations?

## Source images and translations (new default)

- Is each visible source image rendered from the exact provided PDF version?
- Do screenshot IDs bind the crop, PDF page, coordinates, hash and translation?
- Does every cited region have visible source pixels plus corresponding translation,
  or an explicit partial/unavailable reason?
- Are author text, translated text, translator notes and analytical commentary distinct?
- Are chart axes, legends, captions, table cells and algorithm comments covered when present?
- Do continued sentences have links without silently adding unseen text?
- Are full-page context and selected-region translation labeled differently?
- Are counts derived from data, including missing or partial coverage?
- Do zoom, crop/full page, page selection, index and translation selection work offline?
- Were scripts actually run, and were desktop/mobile screenshots inspected?
- Did existing statement explanations and author-argument links survive the update?


## Language selection

- [ ] Reading and source/translation languages can be selected independently.
- [ ] Each listed reading language includes all explanations and the author argument.
- [ ] Original code, image bytes, formulas, numbers and evidence identity do not change.
- [ ] Original-language source text is labeled as a transcript.
- [ ] Missing target-language regions are explicit; another language is not substituted.
- [ ] Switching preserves the selected unit/block, argument, source crop and zoom.
- [ ] Offline generation and pre-authored locale limitations are stated.
- [ ] All generated locale choices were checked on desktop and mobile.
