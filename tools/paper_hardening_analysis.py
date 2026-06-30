#!/usr/bin/env python3
"""Generate paper-hardening diagnostics from existing FiberRing outputs.

This script does not rerun model calls. It computes secondary diagnostics used
by the manuscript:

- paired A1/A2 template transitions by model;
- strict verdict accuracy versus the existing abstention-accepted score;
- Lean source-anchor manifest counts.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from israel_setA_evaluate import canonical_verdict, evaluate, load_reference, read_jsonl


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a"
    return f"{100.0 * numerator / denominator:.1f}%"


def bool_cell(value: bool) -> str:
    return "yes" if value else "no"


def paired_template_transitions(scored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in scored_rows:
        key = (str(row["model"]), str(row["run"]), str(row["item_id"]))
        by_key[key][str(row["condition"])] = row

    groups: dict[str, Counter[tuple[bool, bool]]] = defaultdict(Counter)
    improved_families: dict[str, Counter[str]] = defaultdict(Counter)
    persistent_families: dict[str, Counter[str]] = defaultdict(Counter)
    regressed_families: dict[str, Counter[str]] = defaultdict(Counter)

    for (model, _run, _item_id), conditions in by_key.items():
        if "A1" not in conditions or "A2" not in conditions:
            continue
        a1 = bool(conditions["A1"]["template_correct"])
        a2 = bool(conditions["A2"]["template_correct"])
        expected = str(conditions["A1"]["expected_template"])
        groups[model][(a1, a2)] += 1
        if not a1 and a2:
            improved_families[model][expected] += 1
        elif not a1 and not a2:
            persistent_families[model][expected] += 1
        elif a1 and not a2:
            regressed_families[model][expected] += 1

    rows: list[dict[str, Any]] = []
    for model in sorted(groups):
        counter = groups[model]
        total = sum(counter.values())
        rows.append(
            {
                "model": model,
                "paired_n": total,
                "a1_correct_a2_correct": counter[(True, True)],
                "a1_wrong_a2_correct": counter[(False, True)],
                "a1_wrong_a2_wrong": counter[(False, False)],
                "a1_correct_a2_wrong": counter[(True, False)],
                "improved_families": "; ".join(
                    f"{name} ({count})" for name, count in improved_families[model].most_common()
                ),
                "persistent_wrong_families": "; ".join(
                    f"{name} ({count})" for name, count in persistent_families[model].most_common()
                ),
                "regressed_families": "; ".join(
                    f"{name} ({count})" for name, count in regressed_families[model].most_common()
                ),
                "a1_wrong_a2_correct_pct": pct(counter[(False, True)], total),
                "a1_correct_a2_wrong_pct": pct(counter[(True, False)], total),
            }
        )
    return rows


def strict_verdict_summary(scored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        groups[(str(row["model"]), str(row["condition"]))].append(row)

    rows: list[dict[str, Any]] = []
    for (model, condition), group_rows in sorted(groups.items()):
        n = len(group_rows)
        strict_correct = sum(
            1
            for row in group_rows
            if canonical_verdict(str(row["predicted_verdict"]))
            == canonical_verdict(str(row["expected_verdict"]))
        )
        abstention_accepted_correct = sum(1 for row in group_rows if row["verdict_correct"])
        unknown_predictions = sum(
            1
            for row in group_rows
            if canonical_verdict(str(row["predicted_verdict"])) == "Unknown-from-statement"
        )
        rows.append(
            {
                "model": model,
                "condition": condition,
                "n": n,
                "strict_verdict_correct": strict_correct,
                "strict_verdict_accuracy": pct(strict_correct, n),
                "abstention_accepted_correct": abstention_accepted_correct,
                "abstention_accepted_accuracy": pct(abstention_accepted_correct, n),
                "unknown_predictions": unknown_predictions,
            }
        )
    return rows


def manifest_summary(manifest_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_set: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in manifest_rows:
        by_set[str(row["set"])].append(row)

    rows: list[dict[str, Any]] = []
    for set_name in sorted(by_set):
        group = by_set[set_name]
        anchor_counts = Counter(str(row["anchor_level"]) for row in group)
        source_ref_count = sum(len(row.get("source_refs") or []) for row in group)
        source_gap_count = anchor_counts.get("source-gap", 0)
        rows.append(
            {
                "set": set_name,
                "rows": len(group),
                "theorem": anchor_counts.get("theorem", 0),
                "theorem_family": anchor_counts.get("theorem-family", 0),
                "source_family": anchor_counts.get("source-family", 0),
                "source_gap": source_gap_count,
                "source_refs": source_ref_count,
                "source_snapshots": "; ".join(sorted({str(row["source_snapshot"]) for row in group})),
            }
        )
    if len(rows) > 1:
        anchor_counts = Counter(str(row["anchor_level"]) for row in manifest_rows)
        rows.append(
            {
                "set": "Total",
                "rows": len(manifest_rows),
                "theorem": anchor_counts.get("theorem", 0),
                "theorem_family": anchor_counts.get("theorem-family", 0),
                "source_family": anchor_counts.get("source-family", 0),
                "source_gap": anchor_counts.get("source-gap", 0),
                "source_refs": sum(len(row.get("source_refs") or []) for row in manifest_rows),
                "source_snapshots": "; ".join(sorted({str(row["source_snapshot"]) for row in manifest_rows})),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, sections: dict[str, list[dict[str, Any]]]) -> None:
    lines = ["# Paper Hardening Diagnostics", ""]
    for title, rows in sections.items():
        lines.extend([f"## {title}", ""])
        if not rows:
            lines.extend(["No rows.", ""])
            continue
        headers = list(rows[0].keys())
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def load_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-protocol", type=Path, default=Path("data/israel_setA_A1_A2_protocol.json"))
    parser.add_argument("--set-a-predictions", type=Path, default=Path("experiments/israel_setA_predictions.jsonl"))
    parser.add_argument("--set-b-protocol", type=Path, default=Path("data/israel_setB_A1_A2_protocol_2026-05-28.json"))
    parser.add_argument("--set-b-predictions", type=Path, default=Path("experiments/israel_setB_predictions.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("docs/lean_source_anchor_manifest.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/paper_hardening"))
    return parser.parse_args()


def score_dataset(protocol_path: Path, predictions_path: Path) -> list[dict[str, Any]]:
    allowed_labels, reference = load_reference(protocol_path)
    predictions = read_jsonl(predictions_path)
    _summary, scored_rows = evaluate(predictions, reference, allowed_labels)
    return scored_rows


def main() -> int:
    args = parse_args()
    set_a_rows = score_dataset(args.set_a_protocol, args.set_a_predictions)
    set_b_rows = score_dataset(args.set_b_protocol, args.set_b_predictions)
    manifest_rows = load_manifest(args.manifest)

    sections = {
        "Set A Paired Template Transitions": paired_template_transitions(set_a_rows),
        "Set B Paired Template Transitions": paired_template_transitions(set_b_rows),
        "Set A Strict Verdict Diagnostics": strict_verdict_summary(set_a_rows),
        "Set B Strict Verdict Diagnostics": strict_verdict_summary(set_b_rows),
        "Lean Source-Anchor Manifest Summary": manifest_summary(manifest_rows),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in sections.items():
        slug = name.casefold().replace(" ", "_").replace("-", "_")
        write_csv(args.output_dir / f"{slug}.csv", rows)
    write_markdown(args.output_dir / "paper_hardening_diagnostics.md", sections)
    print(json.dumps({"output_dir": str(args.output_dir), "sections": list(sections)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
