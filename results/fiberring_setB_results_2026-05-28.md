# FiberRing Set B Routing Evaluation — Results Report
**Date:** 2026-05-28  
**Benchmark:** Israel Set B (6 items x 2 conditions = 12 prompts)  
**Total predictions:** 72 (2 models x 3 runs x 12 prompts)  
**Backend:** Together AI via OpenAI-compatible client  
**Labels:** 19 allowed templates  

---

## Scope

Set B is a small extension set designed to test whether the Set A
mechanism-routing pattern persists when the objects move beyond the clean
FiberRing algebra core into FiberRing/POM bridge, CRT-budget, and
CollisionKernel certificates.

The six Set B mechanism labels are:

| Item | Expected template | Bucket |
|---|---|---|
| `fr-023` | `hidden-bit-overflow-decomposition` | FiberRing-POM bridge |
| `fr-024` | `probabilistic-CRT-reconstruction` | POM CRT budget |
| `fr-025` | `collision-kernel-existence` | CollisionKernel |
| `fr-026` | `collision-CK-classification` | CollisionKernel |
| `fr-027` | `bowen-franks-SNF-certificate` | CollisionKernel |
| `fr-028` | `CRT-budget-bound` | POM CRT budget |

Set B uses the same A1/A2 design as Set A:

- `A1`: blind structural routing from the equation/object only.
- `A2`: cue-conditioned routing with the Lean verdict / witness cue included.

---

## Headline Metrics

| Model | Condition | Template Acc | Verdict Acc | Caveat Hit Rate |
|---|---|---:|---:|---:|
| openai/gpt-oss-120b | A1 | **100.0%** (18/18) | 83.3% (15/18) | n/a |
| openai/gpt-oss-120b | A2 | **100.0%** (18/18) | 100.0% (18/18) | n/a |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A1 | **50.0%** (9/18) | 100.0% (18/18) | n/a |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A2 | **77.8%** (14/18) | 100.0% (18/18) | n/a |

---

## A2 - A1 Gaps

| Model | Delta Template Acc | Delta Verdict Acc | Delta Caveat Hit Rate |
|---|---:|---:|---:|
| openai/gpt-oss-120b | **0.0 pp** | +16.7 pp | n/a |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | **+27.8 pp** | 0.0 pp | n/a |

---

## Key Findings

### openai/gpt-oss-120b

- Template routing is perfect on this small Set B extension in both
  conditions: 18/18 in A1 and 18/18 in A2.
- Verdict accuracy improves from 15/18 in A1 to 18/18 in A2.
- The corrected evaluator now recognizes the six Set B-specific labels
  directly, rather than folding them into `__other__` in the confusion matrix.

### meta-llama/Llama-3.3-70B-Instruct-Turbo

- Template routing improves from 9/18 in A1 to 14/18 in A2, a +27.8 pp lift.
- Verdict accuracy is already at 18/18 in both conditions, preserving the Set A
  verdict/template dissociation pattern.
- The remaining A2 failures are concentrated in CRT-granularity compression:
  `probabilistic-CRT-reconstruction -> CRT` for 1/3 runs and
  `CRT-budget-bound -> CRT` for 3/3 runs.

---

## Misroute Summary

| Model | Condition | Expected | Predicted | Count |
|---|---|---|---|---:|
| Llama-3.3-70B | A1 | `hidden-bit-overflow-decomposition` | `stable-value-map` | 3 |
| Llama-3.3-70B | A1 | `probabilistic-CRT-reconstruction` | `CRT` | 3 |
| Llama-3.3-70B | A1 | `CRT-budget-bound` | `CRT` | 3 |
| Llama-3.3-70B | A2 | `probabilistic-CRT-reconstruction` | `CRT` | 1 |
| Llama-3.3-70B | A2 | `CRT-budget-bound` | `CRT` | 3 |

No template misroutes were observed for gpt-oss-120b on Set B.

---

## Run Configuration

```text
Models:      openai/gpt-oss-120b, meta-llama/Llama-3.3-70B-Instruct-Turbo
Runs:        3 per prompt per model
Temperature: 0.0
Seed:        0
Max tokens:  512
Reasoning:   {"effort": "low"}  (gpt-oss-120b only, via extra_body)
Resume:      enabled
```

## Artifacts

| File | Description |
|---|---|
| `experiments/israel_setB_predictions.jsonl` | Raw model outputs (72 rows) |
| `experiments/israel_setB_summary.json` | Aggregate metrics and confusion matrices |
| `experiments/israel_setB_row_scores.csv` | Row-level scoring detail |
| `data/israel_setB_A1_A2_protocol_2026-05-28.json` | Ground truth reference |
| `data/israel_setB_A1_A2_prompt_pack_2026-05-28.jsonl` | 12 rendered prompts |
