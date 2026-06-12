# FiberRing Israel Set A Measurement Memo

This benchmark measures whether a model can route FiberRing formalization claims to the right proof-template family. Each of the 22 items appears under two conditions, giving 44 prompts.

## A1: blind structural routing

A1 prompts include the item ID, the equation or object, and the 13 allowed labels. They do not include the Lean verdict. A1 is meant to estimate the ceiling for routing from surface mathematical structure alone: for example, whether a product of `ZMod` factors is recognized as `CRT`, or whether a stable-value identity is routed to `stable-value-arithmetic`.

Because A1 does not expose whether Lean actually proved the statement, the evaluator accepts `Unknown-from-statement` as a correct verdict in A1 when the template route is otherwise judged against the hidden reference.

## A2: cue-conditioned routing

A2 prompts add the Lean verdict / witness cue. This measures how well the model uses proof-status and witness cues such as declared instances, CRT packages, explicit finite calculations, and preservation lemmas. A2 is not a blind math-reading score; it is a cue-conditioned routing score.

For almost all rows the expected verdict is `True`. Row `fr-021` is scored as `Conditional` because the additive-order statement includes the explicit hypothesis `2 ≤ m`.

## A2 minus A1 gap

The A2-A1 gap is the headline estimate of how much routing improves when the model sees the Lean verdict / witness cue. A positive template-accuracy gap means the cue disambiguates neighboring buckets. A small gap can mean the statement was already structurally clear, or that the model did not use the cue effectively.

Interpret the gap per model, because different models may have different priors about Lean, algebraic structures, and finite-ring calculations.

## Confusion matrix interpretation

Rows are expected labels and columns are predicted labels. The evaluator includes all 13 allowed labels plus `__other__` for blank or invalid predictions. Common expected confusions include:

- `ring-equivalence` versus `stable-value-map` when equivalence transport is collapsed into homomorphism preservation.
- `operation-bridge` versus `stable-value-arithmetic` when stable operation alignment is mistaken for a numerical stable-value formula.
- `CRT` versus `finite-zero-divisor-check` when a zero-divisor example is explained by a product decomposition.
- `field-phase` versus `finite-unit-inverse-check` when a unit identity in a field fiber is scored as the concrete finite calculation.
- `characteristic` versus `ring-equivalence` when additive order is proved through the `ZMod` equivalence but should route to characteristic/additive-order reasoning.

Caveat hit rate is secondary. It checks whether the model mentions an expected caveat or witness keyword in the caveat, reason, or raw response. Rows without expected keywords are excluded from that denominator.
