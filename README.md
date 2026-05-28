# FiberRing Routing Evaluation

This repository contains a complete, runnable evaluation pipeline for the FiberRing Set A routing benchmark. It tests whether models route formalized algebra statements to the intended proof-template family under two conditions:

- `A1`: blind structural routing from the equation/object only.
- `A2`: cue-conditioned routing with the known Lean verdict included.

The benchmark has 22 FiberRing rows, 13 allowed labels, and 44 prompts total.

## Repository Layout

```text
data/
  israel_setA_A1_A2_protocol.json        # benchmark metadata, rows, labels, scoring rules
  israel_setA_A1_A2_prompt_pack.jsonl    # 44 rendered A1/A2 prompts
  israel_setA_predictions_template.jsonl # blank evaluator-compatible prediction rows
  israel_setA_measurement_memo.md        # measurement rationale and interpretation notes
tools/
  israel_setA_evaluate.py                # scorer for prediction JSONL
outputs/                                # generated predictions and reports
eval_pipeline_together.py                # Together AI runner
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

The prompt pack is already generated at `data/israel_setA_A1_A2_prompt_pack.jsonl`. Each row contains:

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
python eval_pipeline_together.py \
  --prompt-pack data/israel_setA_A1_A2_prompt_pack.jsonl \
  --output outputs/israel_setA_predictions.jsonl
```

Useful options:

```bash
python eval_pipeline_together.py \
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
  --predictions outputs/israel_setA_predictions.jsonl \
  --protocol data/israel_setA_A1_A2_protocol.json \
  --summary-output outputs/israel_setA_summary.json \
  --row-csv-output outputs/israel_setA_row_scores.csv
```

The evaluator reports metrics separately by model and condition:

- template accuracy after canonicalizing punctuation, spacing, case, underscores, and hyphenation
- verdict accuracy, with A1 accepting `Unknown-from-statement` as a practical blind-condition verdict
- caveat hit rate from expected row keywords
- confusion matrices over the 13 labels, plus `__other__` for invalid or blank predictions
- headline A2-A1 gaps for template accuracy, verdict accuracy, and caveat hit rate

## Outputs

Typical generated files:

- `outputs/israel_setA_predictions.jsonl`: raw model outputs parsed into evaluator fields
- `outputs/israel_setA_summary.json`: aggregate metrics and confusion matrices
- `outputs/israel_setA_row_scores.csv`: row-level scoring details

## Notes On Collaboration And Cost

The protocol and prompt pack are deterministic data artifacts. If the item set changes, update `data/israel_setA_A1_A2_protocol.json` first, then regenerate or edit the prompt pack and prediction template consistently.

Cost scales as:

```text
22 items × 2 conditions × models × runs
```

With the default 2 models and 3 runs, the pipeline makes 264 model calls. For a smoke test, run one model with `--runs 1`.
