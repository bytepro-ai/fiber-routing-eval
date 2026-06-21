# FiberRing Routing Evaluation

This repository contains a complete, runnable evaluation pipeline for the FiberRing routing benchmarks. It tests whether models route formalized algebra statements to the intended proof-template family under two conditions:

- `A1`: blind structural routing from the equation/object only.
- `A2`: cue-conditioned routing with the Lean verdict / witness cue included.

Set A has 22 FiberRing rows, 13 allowed labels, and 44 prompts total. Set B is a 6-row extension with 19 allowed labels and 12 prompts, covering FiberRing/POM bridge, CRT-budget, and CollisionKernel certificates.

## Repository Layout

```text
data/
  israel_setA_A1_A2_protocol.json        # benchmark metadata, rows, labels, scoring rules
  israel_setA_A1_A2_prompt_pack.jsonl    # 44 rendered A1/A2 prompts
  israel_setA_predictions_template.jsonl # blank evaluator-compatible prediction rows
  israel_setA_measurement_memo.md        # measurement rationale and interpretation notes
  israel_setB_A1_A2_protocol_2026-05-28.json
  israel_setB_A1_A2_prompt_pack_2026-05-28.jsonl
  israel_setB_predictions_template_2026-05-28.jsonl
tools/
  israel_setA_evaluate.py                # scorer for prediction JSONL
  check_lean_source_manifest.py          # checks Lean source-anchor manifest against protocols
scripts/
  eval_pipeline_together.py              # Together AI runner
experiments/                             # generated predictions and machine-readable reports
results/                                 # human-readable results reports
docs/
  lean_source_anchor_manifest.jsonl      # Lean source anchors for all Set A/B rows
  lean_side_framing_review.md            # formalization-side review checklist
.env.example                             # TOGETHER_API_KEY placeholder
README.md
```

## Setup

Use Python 3.10+ and install the OpenAI SDK for the Together-compatible client:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install openai
cp .env.example .env
```

Then set `TOGETHER_API_KEY` in your environment:

```bash
export TOGETHER_API_KEY="..."
```

## Data And Prompt Generation

The prompt packs are already generated:

- `data/israel_setA_A1_A2_prompt_pack.jsonl`
- `data/israel_setB_A1_A2_prompt_pack_2026-05-28.jsonl`

Each row contains:

- `prompt_id`, such as `fr-001-A1`
- `item_id`
- `condition`
- hidden scoring metadata: `expected_template`, `expected_verdict`
- `prompt_text`, the exact text sent to the model

The blank template at `data/israel_setA_predictions_template.jsonl` can be copied or used as a schema reference for manual predictions.

## Running The Together Pipeline

By default, the runner uses:

- `openai/gpt-oss-120b`
- `meta-llama/Llama-3.3-70B-Instruct-Turbo`

and runs each prompt 3 times per model.

```bash
python scripts/eval_pipeline_together.py \
  --prompt-pack data/israel_setA_A1_A2_prompt_pack.jsonl \
  --output experiments/israel_setA_predictions.jsonl
```

Useful options:

```bash
python scripts/eval_pipeline_together.py \
  --models openai/gpt-oss-120b \
  --runs 1 \
  --temperature 0 \
  --max-tokens 512 \
  --resume
```

`--resume` is enabled by default and skips existing `(prompt_id, model, run)` rows in the output. Use `--no-resume` to overwrite from scratch. The runner retries 429 and transient server/connection errors with exponential backoff.

## Evaluation

Evaluate a prediction file against the protocol:

```bash
python tools/israel_setA_evaluate.py \
  --predictions experiments/israel_setA_predictions.jsonl \
  --protocol data/israel_setA_A1_A2_protocol.json \
  --summary-output experiments/israel_setA_summary.json \
  --row-csv-output experiments/israel_setA_row_scores.csv
```

For Set B:

```bash
python tools/israel_setA_evaluate.py \
  --predictions experiments/israel_setB_predictions.jsonl \
  --protocol data/israel_setB_A1_A2_protocol_2026-05-28.json \
  --summary-output experiments/israel_setB_summary.json \
  --row-csv-output experiments/israel_setB_row_scores.csv
```

The evaluator reports metrics separately by model and condition:

- template accuracy after canonicalizing punctuation, spacing, case, underscores, and hyphenation
- verdict accuracy, with A1 accepting `Unknown-from-statement` as a practical blind-condition verdict
- caveat hit rate from expected row keywords
- confusion matrices over the protocol labels, plus `__other__` for invalid or blank predictions
- headline A2-A1 gaps for template accuracy, verdict accuracy, and caveat hit rate

## Outputs

Typical generated files:

- `experiments/israel_setA_predictions.jsonl`: raw Set A model outputs parsed into evaluator fields
- `experiments/israel_setA_summary.json`: Set A aggregate metrics and confusion matrices
- `experiments/israel_setA_row_scores.csv`: Set A row-level scoring details
- `experiments/israel_setB_predictions.jsonl`: raw Set B model outputs parsed into evaluator fields
- `experiments/israel_setB_summary.json`: Set B aggregate metrics and confusion matrices
- `experiments/israel_setB_row_scores.csv`: Set B row-level scoring details
- `results/fiberring_setA_results_2026-05-27.md`: human-readable Set A report
- `results/fiberring_setB_results_2026-05-28.md`: human-readable Set B report

## Lean-Side Review

Use `docs/lean_side_framing_review.md` to review the Automath/Omega
formalization side: Lean-verified artifacts, Lean-side witness cues,
certificate-family annotations, proof-mechanism labels, source obligations,
and manuscript wording.

The machine-readable source-anchor manifest is
`docs/lean_source_anchor_manifest.jsonl`. It maps every Set A and Set B row to
Automath/Omega Lean declarations and line anchors. Its row schema, anchor
levels, and validation invariants are documented in
`docs/lean_source_anchor_manifest_spec.md`. Check the manifest with:

```bash
python3 tools/check_lean_source_manifest.py
```

## Notes On Collaboration And Cost

The protocol and prompt pack are deterministic data artifacts. If an item set changes, update the corresponding protocol first, then regenerate or edit the prompt pack and prediction template consistently.

Cost scales as:

```text
22 items × 2 conditions × models × runs
```

With the default 2 models and 3 runs, the pipeline makes 264 model calls. For a smoke test, run one model with `--runs 1`.

For Set B:

```text
6 items × 2 conditions × models × runs
```
