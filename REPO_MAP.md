# FiberRing Routing Eval — Repo Map

## Purpose

This repository contains the evaluation pipeline for the **FiberRing Israel routing benchmarks**. The benchmarks test whether language models can correctly route formalized algebraic claims (from Lean 4 FiberRing/POM/CollisionKernel artifacts) to the right proof-template family under two experimental conditions:

- **A1** — blind structural routing: model sees only the equation/object and the label list.
- **A2** — cue-conditioned routing: model also sees the Lean verdict / witness cue.

Set A uses 22 FiberRing rows and 13 labels. Set B is a 6-row extension with 19 labels covering FiberRing/POM bridge, CRT-budget, and CollisionKernel certificates. The A2 - A1 gap measures how much routing improves when the Lean verdict / witness cue is revealed.

---

## Directory Structure

```
fiber-routing-eval/
│
├── data/                          # Benchmark data artifacts (do not modify without updating protocol)
│   ├── israel_setA_A1_A2_protocol.json       # Ground truth: 22 items, expected labels, verdicts, keywords
│   ├── israel_setA_A1_A2_prompt_pack.jsonl   # 44 rendered prompts (A1 + A2 for each item)
│   ├── israel_setA_predictions_template.jsonl # Blank evaluator-compatible prediction schema
│   ├── israel_setA_measurement_memo.md        # Methodological rationale and confusion guidance
│   ├── israel_setB_A1_A2_protocol_2026-05-28.json       # Set B ground truth: 6 extension items
│   ├── israel_setB_A1_A2_prompt_pack_2026-05-28.jsonl   # 12 rendered prompts
│   └── israel_setB_predictions_template_2026-05-28.jsonl # Blank Set B prediction schema
│
├── scripts/                       # Runnable pipeline scripts
│   └── eval_pipeline_together.py  # Together AI runner (OpenAI-compatible client)
│
├── tools/                         # Evaluation and scoring utilities
│   ├── israel_setA_evaluate.py    # Scorer: reads predictions + protocol, writes summary + CSV
│   └── check_lean_source_manifest.py # Checks Lean source-anchor manifest against protocols
│
├── experiments/                   # Generated outputs from pipeline runs
│   ├── israel_setA_predictions.jsonl  # Raw model outputs (264 rows for Set A)
│   ├── israel_setA_summary.json       # Aggregate metrics and confusion matrices
│   ├── israel_setA_row_scores.csv     # Row-level Set A scoring detail
│   ├── israel_setB_predictions.jsonl  # Raw model outputs (72 rows for Set B)
│   ├── israel_setB_summary.json       # Aggregate Set B metrics and confusion matrices
│   ├── israel_setB_row_scores.csv     # Row-level Set B scoring detail
│   ├── blank_summary.json             # Schema reference (all-blank baseline)
│   └── blank_row_scores.csv           # Schema reference (all-blank baseline)
│
├── results/                       # Human-readable results reports
│   ├── fiberring_setA_results_2026-05-27.md  # Set A results report
│   └── fiberring_setB_results_2026-05-28.md  # Set B results report
│
├── docs/                          # Review and coordination notes
│   ├── lean_side_framing_review.md # Automath/Omega Lean-side review checklist
│   ├── lean_source_anchor_manifest.jsonl # Lean anchors for all Set A/B protocol rows
│   └── lean_source_anchor_manifest_spec.md # Manifest schema, anchor levels, and review invariants
│
├── papers/                        # Manuscript and bibliography (in progress)
│   ├── main.tex
│   └── references.bib
│
├── FiberRing/                     # Python virtual environment (not tracked)
├── .env                           # API key (not tracked)
├── .env.example                   # Key template: TOGETHER_API_KEY=...
├── requirements.txt               # Pinned pip dependencies
└── README.md                      # Setup and usage documentation
```

---

## Workflow

### 1. Run the pipeline

```bash
source FiberRing/bin/activate
python scripts/eval_pipeline_together.py \
  --prompt-pack data/israel_setA_A1_A2_prompt_pack.jsonl \
  --output experiments/israel_setA_predictions.jsonl \
  --models openai/gpt-oss-120b meta-llama/Llama-3.3-70B-Instruct-Turbo \
  --runs 3 --temperature 0 --max-tokens 512
```

`--resume` is on by default; re-running skips already-completed `(prompt_id, model, run)` rows.

### 2. Evaluate predictions

```bash
python tools/israel_setA_evaluate.py \
  --predictions experiments/israel_setA_predictions.jsonl \
  --protocol data/israel_setA_A1_A2_protocol.json \
  --summary-output experiments/israel_setA_summary.json \
  --row-csv-output experiments/israel_setA_row_scores.csv
```

### 3. Review results

See `results/` for human-readable reports. See `experiments/israel_setA_summary.json` for full metrics and confusion matrices.
For Set B, see `results/fiberring_setB_results_2026-05-28.md` and
`experiments/israel_setB_summary.json`.

For formalization-side wording and source-obligation review, see
`docs/lean_side_framing_review.md`.

For machine-readable Lean source anchors, see
`docs/lean_source_anchor_manifest.jsonl`. For the manifest row schema, anchor
levels, and review invariants, see
`docs/lean_source_anchor_manifest_spec.md`. Check the manifest with
`python3 tools/check_lean_source_manifest.py`.

---

## Cost Scaling

```
22 items × 2 conditions × models × runs
```

Default (2 models, 3 runs) = **264 API calls**. For a smoke test: `--models openai/gpt-oss-120b --runs 1` = 44 calls.

---

## Key Numbers (Set A, 2026-05-27)

| Model | A1 Template Acc | A2 Template Acc | Δ (A2−A1) |
|---|---|---|---|
| openai/gpt-oss-120b | 80.3% | 90.9% | +10.6 pp |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | 68.2% | 81.8% | +13.6 pp |

## Key Numbers (Set B, 2026-05-28)

| Model | A1 Template Acc | A2 Template Acc | Delta (A2-A1) |
|---|---:|---:|---:|
| openai/gpt-oss-120b | 100.0% | 100.0% | +0.0 pp |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | 50.0% | 77.8% | +27.8 pp |
