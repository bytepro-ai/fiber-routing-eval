# Lean Source-Anchor Manifest Specification

## Purpose

The Lean source-anchor manifest records how each benchmark evaluation row is
linked to formal source material in the Automath/Omega Lean corpus.

The manifest is not an experimental result file and is not a replacement for
the Set A or Set B protocols. Its purpose is to make the source obligations of
the benchmark auditable:

- each evaluation row has a stable identifier and benchmark subset;
- each row has a proof-mechanism label used as the routing target;
- each row has witness-family language corresponding to the Lean-side cue used
  in cue-conditioned routing;
- each row points to one or more Lean declarations, line anchors, or source
  families that support the label assignment;
- each row records the source snapshot against which those anchors were
  reviewed.

This distinction is important for manuscript wording. A benchmark row may be
Lean-anchored without being a one-to-one natural-language translation of a
single Lean theorem. Some rows are direct theorem rows; others are anchored to a
theorem family, a broader source family, or an explicitly recorded source gap.
Individual source references may still point to declarations whose `kind` is
`def`, `instance`, or another declaration category; those are source-reference
kinds, not row-level `anchor_level` values.

## Manifest Row Schema

The manifest is stored as JSON Lines in
`docs/lean_source_anchor_manifest.jsonl`. Each line is one manifest row. The
current repository instance has one row for each Set A and Set B protocol item.

Canonical row shape:

```json
{
  "item_id": "fr-001",
  "set": "A",
  "expected_template": "ring-equivalence",
  "witness_family": "stableValueRingEquiv equivalence package",
  "protocol_audit_pointer": "Check the global X_m-to-ZMod ring equivalence declarations.",
  "anchor_level": "theorem-family",
  "source_snapshot": "automath@caa043a7733205c0152ec685d9e1870697077b70",
  "source_refs": [
    {
      "path": "lean4/Omega/Folding/FiberRing.lean",
      "line": 157,
      "lean_name": "stableValueRingEquiv",
      "kind": "def"
    }
  ],
  "review_note": "Global ring-equivalence package; row wording is a family-level benchmark statement rather than a single isolated formula."
}
```

Field meanings:

| Field | Meaning |
|---|---|
| `item_id` | Evaluation row identifier. This must match the protocol row identifier, such as `fr-001`. |
| `set` | Benchmark subset. Current values are `A` for FiberRing Set A and `B` for the cross-corpus Set B extension. |
| `expected_template` | Routing target, also called the proof-mechanism label. This is the template the evaluator expects the model to select. |
| `witness_family` | Human-readable formal witness or certificate-family language. This should align with the cue or Lean-side mechanism language used by the protocol. |
| `protocol_audit_pointer` | Protocol-side source pointer or review instruction used to align the benchmark row with formal source material. For Set B exact file-line pointers, this is mirrored by the first `source_refs` entry. |
| `anchor_level` | The granularity at which the row is anchored to Lean source. See the anchor-level definitions below. |
| `source_snapshot` | Exact source commit or snapshot where the references were reviewed. Current rows use `automath@caa043a7733205c0152ec685d9e1870697077b70`. |
| `source_refs` | Nonempty list of Lean source references. Each reference gives a file path, line number, declaration name, and declaration kind. |
| `review_note` | Human-readable explanation of why the listed anchors support the mechanism label and how narrowly the row should be described. |

Each `source_refs` entry has this shape:

```json
{
  "path": "lean4/Omega/Folding/FiberRing.lean",
  "line": 157,
  "lean_name": "stableValueRingEquiv",
  "kind": "def"
}
```

`path` is relative to the declared source snapshot. `line` is a 1-indexed line
anchor in that snapshot. `lean_name` is the declaration or source object being
anchored. `kind` records the source category, such as `theorem`, `def`, or
`instance`.

## Anchor Levels

`anchor_level` records how directly the evaluation row is represented in Lean.
It prevents overclaiming by separating direct theorem anchors from broader
source-family anchors. The checker accepts exactly these row-level values:
`theorem`, `theorem-family`, `source-family`, and `source-gap`.

| Anchor level | Meaning | Manuscript implication |
|---|---|---|
| `theorem` | The row is supported by a specific Lean theorem whose statement directly captures the row or publication-facing claim. | It is usually safe to call the referenced artifact Lean-verified, while still avoiding claims beyond the theorem statement. |
| `theorem-family` | The row is supported by a related family of theorems, definitions, or packaging lemmas. The benchmark row may summarize the mechanism family rather than translate one theorem verbatim. | Describe the row as Lean-anchored or anchored to a theorem family. Do not imply a one-to-one theorem translation unless a direct theorem is listed and reviewed. |
| `source-family` | The row is anchored to a source region or module family rather than one declaration. | Use conservative wording: the item is source-anchored, but stronger claims need a more precise declaration-level anchor. |
| `source-gap` | The intended source anchor has not been located or is known to be incomplete, and the gap is recorded in `review_note`. | Do not describe the item as Lean-verified or source-secure. Treat it as an unresolved source obligation until the gap is closed. |

Current rows primarily use `theorem` and `theorem-family`, with `source_refs`
that may include `def` and `instance` declarations. The distinction is between
the row-level anchor granularity and the kind of each individual source
reference. Certificate-family language belongs in `witness_family` and
`review_note`; it is not a separate row-level `anchor_level` value unless a
future checker revision adds one.

## Source References

A source reference is an auditable pointer into the formal corpus. It should be
stable enough that an independent reviewer can recover the cited declaration
from the declared snapshot.

Required properties:

- `path` must exist in `source_snapshot`.
- `line` should point to the declaration line or a nearby line that uniquely
  identifies the declaration.
- `lean_name` should occur at the listed line for exact anchors. If a future
  row intentionally uses a nearby context anchor instead, the `review_note`
  should say so explicitly.
- `kind` should match the Lean declaration category when the declaration is a
  theorem, definition, or instance.

For exact protocol file-line pointers, the first source reference should mirror
the protocol pointer. This convention is used by Set B so that protocol rows and
manifest rows can be mechanically compared.

## Protocol Alignment Invariants

The manifest and protocol files should satisfy these invariants.

1. Every protocol row must have exactly one manifest row.
2. Every manifest row must correspond to exactly one protocol row.
3. `item_id` must match between the protocol row and manifest row.
4. `expected_template` must match the protocol label.
5. `witness_family` must match the cue or certificate-family language used by
   the protocol.
6. `protocol_audit_pointer` must match the protocol audit pointer or equivalent
   source-review instruction.
7. `source_refs` must be nonempty.
8. Every `source_refs[].path` must exist in the declared `source_snapshot`.
9. Every `source_refs[].lean_name` should occur at the listed line anchor in
   the declared `source_snapshot`.
10. For exact Set B protocol pointers of the form `path:line`, the first
    manifest `source_refs` entry should mirror that path and line exactly.
11. Manuscript claims using `Lean-verified` should refer only to source
    artifacts whose anchor level supports that wording.
12. Rows with `theorem-family` or `source-family` anchors should not be
    described as one-to-one natural-language theorem translations unless a
    direct theorem row is listed and reviewed.
13. Rows with `source-gap` anchors should explicitly explain the gap in
    `review_note` and should not be used to support Lean-verified wording.

These invariants are designed to keep three layers synchronized:

- protocol rows used by the evaluator;
- Lean-side source anchors used by reviewers;
- manuscript wording about Lean verification and proof-mechanism labels.

## Review and Validation Workflow

The standard review workflow is:

1. Run the manifest checker:

   ```bash
   python3 tools/check_lean_source_manifest.py
   ```

   This checks row coverage, expected-template agreement, witness-family
   agreement, protocol audit-pointer agreement, and exact Set B pointer
   mirroring.

2. Compare the manifest against the protocol files:

   - `data/israel_setA_A1_A2_protocol.json`
   - `data/israel_setB_A1_A2_protocol_2026-05-28.json`

   Confirm that each row's `expected_template`, `witness_family`, and
   `protocol_audit_pointer` have the intended meaning in the protocol.

3. Check the declared source snapshot. For the current repository instance,
   the source snapshot is:

   ```text
   automath@caa043a7733205c0152ec685d9e1870697077b70
   ```

   A reviewer should verify that each `source_refs[].path` exists at that
   snapshot and that each `lean_name` occurs at the listed line anchor.

4. Inspect the source context around representative anchors. The goal is not
   only to match names, but to confirm that the declaration supports the stated
   proof-mechanism label.

5. If local Lean source and dependencies are available, run targeted Lean
   builds for the anchored modules. This is a source replay, not a benchmark
   rerun. For the current source snapshot, a targeted build can use module
   names such as:

   ```bash
   lake build \
     Omega.Folding.FiberRing \
     Omega.Folding.FiberArithmetic \
     Omega.POM.OneBit \
     Omega.POM.RCRTEpsilon \
     Omega.POM.CollisionKernelPublication \
     Omega.POM.CollisionCKClassificationQ234 \
     Omega.POM.CollisionBfSnfQ234 \
     Omega.POM.CRTSpatializationPrimeBudget
   ```

6. Review manuscript wording only after the source and protocol checks are
   complete. In particular, confirm that `Lean-verified`, `Lean-anchored`,
   `certificate-family`, `proof-mechanism label`, and `witness cue` are not
   used interchangeably.

The benchmark itself does not need to be rerun for this source-anchor review.

## Example Row

Example: `fr-001`.

```json
{
  "item_id": "fr-001",
  "set": "A",
  "expected_template": "ring-equivalence",
  "witness_family": "stableValueRingEquiv equivalence package",
  "protocol_audit_pointer": "Check the global X_m-to-ZMod ring equivalence declarations.",
  "anchor_level": "theorem-family",
  "source_snapshot": "automath@caa043a7733205c0152ec685d9e1870697077b70",
  "source_refs": [
    {
      "path": "lean4/Omega/Folding/FiberRing.lean",
      "line": 157,
      "lean_name": "stableValueRingEquiv",
      "kind": "def"
    },
    {
      "path": "lean4/Omega/Folding/FiberRing.lean",
      "line": 343,
      "lean_name": "paper_finite_resolution_mod",
      "kind": "theorem"
    }
  ],
  "review_note": "Global ring-equivalence package; row wording is a family-level benchmark statement rather than a single isolated formula."
}
```

This row says that the routing target is `ring-equivalence`, not merely a broad
topic label. The source anchor points first to the equivalence construction
`stableValueRingEquiv`, then to a paper-facing theorem packaging the finite
resolution ring equivalence. The row-level `anchor_level` is
`theorem-family`, because the benchmark item summarizes the global equivalence
package rather than serving as a verbatim natural-language rendering of only
one theorem.

The correct manuscript wording is therefore conservative: the item is anchored
to a Lean-verified equivalence package, with a named construction and theorem
in the Lean corpus. It should not be described as an independent theorem beyond
the listed source artifacts.

## Current Repository Instance

The current manifest instance contains 28 rows:

- 22 Set A FiberRing rows;
- 6 Set B cross-corpus extension rows;
- 13 Set A proof-mechanism labels;
- 19 Set B proof-mechanism labels;
- source anchors against
  `automath@caa043a7733205c0152ec685d9e1870697077b70`.

Set B rows use exact protocol pointer mirroring for the first source reference:

| Item | Label | First source reference |
|---|---|---|
| `fr-023` | `hidden-bit-overflow-decomposition` | `lean4/Omega/POM/OneBit.lean:7` |
| `fr-024` | `probabilistic-CRT-reconstruction` | `lean4/Omega/POM/RCRTEpsilon.lean:22` |
| `fr-025` | `collision-kernel-existence` | `lean4/Omega/POM/CollisionKernelPublication.lean:9` |
| `fr-026` | `collision-CK-classification` | `lean4/Omega/POM/CollisionCKClassificationQ234.lean:43` |
| `fr-027` | `bowen-franks-SNF-certificate` | `lean4/Omega/POM/CollisionBfSnfQ234.lean:71` |
| `fr-028` | `CRT-budget-bound` | `lean4/Omega/POM/CRTSpatializationPrimeBudget.lean:30` |

These rows are cross-corpus extension items covering FiberRing/POM bridge,
POM CRT-budget, and CollisionKernel mechanisms. They should not be collapsed
into the FiberRing Set A core rows, even when a model misroutes them to a
broader label such as `CRT` or `stable-value-map`.
