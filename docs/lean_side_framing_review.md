# Lean-Side Framing Review

This document is a review checklist for the Automath/Omega formalization side
of the FiberRing routing evaluation. It is intended to make Lean-side review
concrete and auditable while the manuscript and protocol wording are being
revised.

The goal is not to re-run the benchmark. The goal is to verify that the paper
and repository describe the formalization-side material accurately:

- what is actually Lean-verified;
- what is a certificate-family or proof-mechanism annotation;
- what is only a routing label used by this evaluation;
- which Automath/Omega source anchors support each item family;
- where the manuscript may overstate or blur those distinctions.

This is meant to be a technical review surface for wording, source anchors,
protocol labels, and manuscript claims.

## Machine-Readable Anchor Manifest

The source-anchor audit surface is recorded in
`docs/lean_source_anchor_manifest.jsonl`. It gives one row for each Set A and
Set B protocol item, mapping the benchmark row to Automath/Omega Lean
declarations, source line references, and an explicit anchor level.

Run `python3 tools/check_lean_source_manifest.py` to verify that the manifest
and protocols stay synchronized. The checker confirms row coverage, expected
template and witness-family agreement, protocol audit-pointer agreement, and
exact Set B pointer mirroring.

## Review Roles

Suggested review responsibilities:

- Benchmark maintainer: experimental design, execution, analysis, and paper
  framing.
- Automath/Omega anchor reviewer: source-anchor coordination and repository
  review.
- Formalization-side reviewer: Lean-side wording, source obligations, and
  certificate-family framing.

This document gives a concrete path for Lean-side technical review.

## Review Inputs

The reviewer should compare this checklist against these repository files.

| File | Review use |
|---|---|
| `papers/main.tex` | Check wording in the abstract, dataset, methodology, analysis, limitations, and attribution-facing passages. |
| `data/israel_setA_A1_A2_protocol.json` | Check Set A labels, verdict fields, and source-family interpretation. |
| `data/israel_setB_A1_A2_protocol_2026-05-28.json` | Check Set B labels, audit pointers, and ambiguity notes. |
| `results/fiberring_setA_results_2026-05-27.md` | Check whether the Set A result narrative matches the protocol. |
| `results/fiberring_setB_results_2026-05-28.md` | Check whether the Set B result narrative stays separate from the Set A headline claim. |
| `README.md` and `REPO_MAP.md` | Check public repository descriptions and entry points. |

The review is complete when every requested wording change is either applied
in a PR or recorded as an explicit unresolved source obligation.

## Terms To Keep Distinct

Use these distinctions consistently in the manuscript and repository.

| Term | Intended meaning | Avoid saying |
|---|---|---|
| Lean-verified artifact | A theorem, definition, instance, or certificate actually present in the Lean corpus. | That every natural-language interpretation is itself Lean-verified. |
| Lean-anchored item | A benchmark row whose source points to a Lean artifact or source-family anchor. | That the benchmark row is a standalone formal theorem if it is only a routed statement. |
| Certificate-family annotation | A cue describing the named proof-mechanism family used as the intended label. | That the cue is merely a truth verdict. |
| Proof-mechanism label | The classification target in the routing task. | That the label is always the broad mathematical topic of the statement. |
| Verdict | The expected truth status used by the evaluator. | That verdict accuracy is the same as mechanism routing accuracy. |
| Source obligation | A source-level check needed to justify a label, claim, or wording choice. | That a label is source-secure without checking the relevant file/line anchor. |

## Set A Label Families

Set A uses 22 FiberRing rows and 13 labels. The review question is whether
each label name reflects the intended formal certificate family, not merely a
broad mathematical topic.

| Label | Review focus |
|---|---|
| `ring-structure` | Check that rows concern the `CommRing` / ring-instance layer on `X m`, not transport through `toZMod`. |
| `operation-bridge` | Check that rows concern alignment between inherited operations and stable operations. |
| `stable-value-map` | Check that rows concern preservation through `toZMod` / `stableValue`, not construction of a ring instance. |
| `ring-equivalence` | Check that rows use the broad `X m` to `ZMod (fib (m+2))` equivalence mechanism. |
| `affine-transfer` | Check that affine satisfaction transfer is not collapsed into generic ring equivalence. |
| `field-phase` | Check that prime-Fibonacci field fibers are described as field-instance reasoning. |
| `CRT` | Check that rows require coprime Fibonacci-modulus factorization plus Chinese remainder structure, not only product-ring shape. |
| `prime-power-fiber-specialization` | Check that the row is a direct prime-power specialization and not a nontrivial CRT split. |
| `finite-zero-divisor-check` | Check that the row is an explicit finite arithmetic witness. |
| `finite-unit-inverse-check` | Check that the row is an explicit finite unit/inverse calculation, not just field-phase reasoning. |
| `characteristic` | Check that the additive-order / characteristic statement keeps its hypotheses visible. |
| `rigidity` | Check that automorphism rigidity is not described as a generic equivalence statement. |
| `stable-value-arithmetic` | Check that rows are numerical stable-value formulas rather than structural map-preservation rows. |

## Set B Label Families

Set B extends the label space from 13 to 19 labels and adds cross-module
mechanisms from FiberRing/POM bridge, CRT-budget, and CollisionKernel
certificates.

| Label | Source anchor in protocol | Review focus |
|---|---|---|
| `hidden-bit-overflow-decomposition` | `lean4/Omega/POM/OneBit.lean:7` | Check that the statement is an overflow/hidden-bit decomposition, not merely a stable-value map. |
| `probabilistic-CRT-reconstruction` | `lean4/Omega/POM/RCRTEpsilon.lean:22` | Check that the label captures epsilon/bad-event reconstruction, not generic CRT. |
| `collision-kernel-existence` | `lean4/Omega/POM/CollisionKernelPublication.lean:9` | Check that the row concerns existence/realization of a collision-kernel package. |
| `collision-CK-classification` | `lean4/Omega/POM/CollisionCKClassificationQ234.lean:43` | Check that the row concerns low-rank CK classification data. |
| `bowen-franks-SNF-certificate` | `lean4/Omega/POM/CollisionBfSnfQ234.lean:71` | Check that the row concerns Smith / Bowen-Franks certificate data. |
| `CRT-budget-bound` | `lean4/Omega/POM/CRTSpatializationPrimeBudget.lean:30` | Check that the row is a product-size budget condition for exact reconstruction, not generic CRT decomposition. |

## Manuscript Touchpoints

These manuscript locations should be reviewed after any Set B integration or
protocol update.

| Location | Review question |
|---|---|
| Abstract | Does the abstract still describe the evaluated corpus accurately if Set B is included? |
| Introduction / Contributions | Does the paper distinguish Set A headline claims from Set B extension evidence? |
| Dataset section | Are item count, label count, and source families correct for Set A only or Set A plus Set B? |
| Methodology | Is A2 described as Lean-cue-conditioned routing without implying that the cue is only a truth value? |
| Results | Are Set B findings reported without overloading the original Set A narrative? |
| Analysis | Are coarse-label collapses described as routing to a broader structural family rather than as simple model errors? |
| Limitations | Does the paper state that both sets are small and source-family-specific? |
| Attribution wording | Does the Automath/Omega formalization source appear accurately and concretely? |

## Source-Obligation Checklist

Before freezing the manuscript, verify the following.

- Every row that is described as Lean-anchored has a source pointer in the
  protocol or an equivalent source-anchor note.
- Every `Lean-verified` phrase refers to an actual Lean artifact, not merely a
  natural-language row description.
- Every `certificate-family annotation` phrase refers to the intended
  proof-mechanism cue, not only the expected truth verdict.
- Set B uses the 19-label protocol in evaluator output and reports.
- CollisionKernel rows are not described as FiberRing core rows.
- POM / CRT-budget rows are not collapsed into generic CRT unless discussing a
  model misroute.
- Automath/Omega is cited as the formalization source, while the experimental
  design and execution remain attributed to this benchmark project.

## Reviewer Output

A Lean-side reviewer can complete this review in any of these forms:

- a GitHub review comment on a PR touching the manuscript or protocol;
- a short issue comment listing approved terms and requested wording changes;
- a commit or PR updating this checklist, protocol notes, or manuscript wording;
- a signed note confirming that the reviewed labels and source obligations are
  acceptable.

The review should record unresolved source or wording questions separately
from changes already applied in the repository.
