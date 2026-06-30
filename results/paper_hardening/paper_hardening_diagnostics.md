# Paper Hardening Diagnostics

## Set A Paired Template Transitions

| model | paired_n | a1_correct_a2_correct | a1_wrong_a2_correct | a1_wrong_a2_wrong | a1_correct_a2_wrong | improved_families | persistent_wrong_families | regressed_families | a1_wrong_a2_correct_pct | a1_correct_a2_wrong_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | 66 | 42 | 12 | 9 | 3 | CRT (6); finite-unit-inverse-check (3); stable-value-arithmetic (3) | stable-value-map (3); prime-power-fiber-specialization (3); characteristic (3) | operation-bridge (3) | 18.2% | 4.5% |
| openai/gpt-oss-120b | 66 | 53 | 7 | 6 | 0 | CRT (7) | stable-value-map (3); prime-power-fiber-specialization (3) |  | 10.6% | 0.0% |

## Set B Paired Template Transitions

| model | paired_n | a1_correct_a2_correct | a1_wrong_a2_correct | a1_wrong_a2_wrong | a1_correct_a2_wrong | improved_families | persistent_wrong_families | regressed_families | a1_wrong_a2_correct_pct | a1_correct_a2_wrong_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | 18 | 9 | 5 | 4 | 0 | hidden-bit-overflow-decomposition (3); probabilistic-CRT-reconstruction (2) | CRT-budget-bound (3); probabilistic-CRT-reconstruction (1) |  | 27.8% | 0.0% |
| openai/gpt-oss-120b | 18 | 18 | 0 | 0 | 0 |  |  |  | 0.0% | 0.0% |

## Set A Strict Verdict Diagnostics

| model | condition | n | strict_verdict_correct | strict_verdict_accuracy | abstention_accepted_correct | abstention_accepted_accuracy | unknown_predictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A1 | 66 | 63 | 95.5% | 63 | 95.5% | 0 |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A2 | 66 | 63 | 95.5% | 63 | 95.5% | 0 |
| openai/gpt-oss-120b | A1 | 66 | 21 | 31.8% | 56 | 84.8% | 35 |
| openai/gpt-oss-120b | A2 | 66 | 63 | 95.5% | 63 | 95.5% | 0 |

## Set B Strict Verdict Diagnostics

| model | condition | n | strict_verdict_correct | strict_verdict_accuracy | abstention_accepted_correct | abstention_accepted_accuracy | unknown_predictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A1 | 18 | 12 | 66.7% | 18 | 100.0% | 6 |
| meta-llama/Llama-3.3-70B-Instruct-Turbo | A2 | 18 | 18 | 100.0% | 18 | 100.0% | 0 |
| openai/gpt-oss-120b | A1 | 18 | 0 | 0.0% | 15 | 83.3% | 15 |
| openai/gpt-oss-120b | A2 | 18 | 18 | 100.0% | 18 | 100.0% | 0 |

## Lean Source-Anchor Manifest Summary

| set | rows | theorem | theorem_family | source_family | source_gap | source_refs | source_snapshots |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 22 | 7 | 15 | 0 | 0 | 52 | automath@caa043a7733205c0152ec685d9e1870697077b70 |
| B | 6 | 4 | 2 | 0 | 0 | 10 | automath@caa043a7733205c0152ec685d9e1870697077b70 |
| Total | 28 | 11 | 17 | 0 | 0 | 62 | automath@caa043a7733205c0152ec685d9e1870697077b70 |
