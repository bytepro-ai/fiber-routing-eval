# FiberRing Set A Routing Evaluation — Results Report
**Date:** 2026-05-27  
**Benchmark:** Israel Set A (22 items × 2 conditions = 44 prompts)  
**Total predictions:** 264 (2 models × 3 runs × 44 prompts)  
**Backend:** Together AI via OpenAI-compatible client  
**Labels:** 13 allowed templates  

---

## Headline Metrics

| Model | Condition | Template Acc | Verdict Acc | Caveat Hit Rate |
|---|---|---|---|---|
| openai/gpt-oss-120b | A1 | **80.3%** (53/66) | 84.8% (56/66) | 81.8% (54/66) |
| openai/gpt-oss-120b | A2 | **90.9%** (60/66) | 95.5% (63/66) | 89.4% (59/66) |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A1 | **68.2%** (45/66) | 95.5% (63/66) | 77.3% (51/66) |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A2 | **81.8%** (54/66) | 95.5% (63/66) | 77.3% (51/66) |

---

## A2 − A1 Gaps (headline estimate of verdict-cue benefit)

| Model | Δ Template Acc | Δ Verdict Acc | Δ Caveat Hit Rate |
|---|---|---|---|
| openai/gpt-oss-120b | **+10.6 pp** | +10.6 pp | +7.6 pp |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | **+13.6 pp** | 0.0 pp | 0.0 pp |

---

## Key Findings

### openai/gpt-oss-120b
- Strong blind routing (A1 template accuracy 80.3%), with a clear 10.6 pp lift in A2 when the Lean verdict cue is provided.
- Both template accuracy and verdict accuracy improve equally from A1 → A2, suggesting the model actively uses the verdict text to disambiguate neighboring buckets.
- Caveat hit rate also improves by 7.6 pp in A2, indicating better witness/keyword awareness with the verdict present.
- **Main failure mode (A1):** CRT items — 7/12 CRT predictions routed to `ring-equivalence` instead of `CRT` in A1. This resolves completely in A2 (12/12 correct).
- `stable-value-map` and `prime-power-fiber-specialization` were misrouted to `ring-structure` and `ring-equivalence` respectively in both conditions.

### meta-llama/Llama-3.3-70B-Instruct-Turbo
- Lower blind routing (A1 template accuracy 68.2%) but very high blind verdict accuracy (95.5%), suggesting the model makes confident correct verdict calls even when the template route is wrong.
- Largest template gap of the two models (+13.6 pp A2 vs A1), showing the verdict cue provides substantial routing disambiguation.
- Verdict accuracy and caveat hit rate are unchanged between A1 and A2 (already at ceiling or floor), so the A2 benefit is purely template routing.
- **Main failure modes:**
  - `stable-value-map`: routed to `ring-structure` in both A1 and A2 (0/6 correct).
  - `characteristic`: routed to `stable-value-map` in both conditions (0/6 correct).
  - `operation-bridge`: routed to `ring-structure` in A2 (0/3 correct in A2; was correct in A1).
  - `prime-power-fiber-specialization`: routed to `ring-equivalence` in both conditions.
  - CRT improved from 6/12 (A1) to 12/12 (A2).

---

## Confusion Summary (notable errors only)

| Expected | Predicted (A1) | Model | Count |
|---|---|---|---|
| CRT | ring-equivalence | gpt-oss-120b | 7 |
| CRT | ring-equivalence | Llama-3.3-70B | 6 |
| stable-value-map | ring-structure | gpt-oss-120b | 3 (A1+A2) |
| stable-value-map | ring-structure | Llama-3.3-70B | 3 (A1+A2) |
| prime-power-fiber-specialization | ring-equivalence | both | 3 each (A1+A2) |
| characteristic | stable-value-map | Llama-3.3-70B | 3 (A1+A2) |
| finite-unit-inverse-check | ring-structure | Llama-3.3-70B | 3 (A1 only) |
| operation-bridge | ring-structure | Llama-3.3-70B | 3 (A2 only) |

---

## Run Configuration

```
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
| `experiments/israel_setA_predictions.jsonl` | Raw model outputs (264 rows) |
| `experiments/israel_setA_summary.json` | Aggregate metrics and confusion matrices |
| `experiments/israel_setA_row_scores.csv` | Row-level scoring detail (1057 data rows) |
| `data/israel_setA_A1_A2_protocol.json` | Ground truth reference |
| `data/israel_setA_A1_A2_prompt_pack.jsonl` | 44 rendered prompts |
