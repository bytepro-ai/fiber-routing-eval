#!/usr/bin/env python3
"""Evaluate FiberRing routing predictions for Israel Set A."""

from __future__ import annotations

import argparse
import csv
import json
import re
import string
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_ALLOWED_LABELS = [
    "ring-structure",
    "operation-bridge",
    "stable-value-map",
    "ring-equivalence",
    "affine-transfer",
    "field-phase",
    "CRT",
    "prime-power-fiber-specialization",
    "finite-zero-divisor-check",
    "finite-unit-inverse-check",
    "characteristic",
    "rigidity",
    "stable-value-arithmetic",
]

OTHER_LABEL = "__other__"
BLANK_MODEL = "__blank__"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row: {exc}") from exc
    return rows


def label_key(value: str) -> str:
    """Canonical key for exact-ish label matching across punctuation and hyphens."""
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def build_label_map(allowed_labels: list[str]) -> dict[str, str]:
    return {label_key(label): label for label in allowed_labels}


def canonical_label(value: str, label_map: dict[str, str]) -> str:
    if value is None:
        return OTHER_LABEL
    cleaned = str(value).strip()
    if not cleaned:
        return OTHER_LABEL
    return label_map.get(label_key(cleaned), OTHER_LABEL)


def canonical_verdict(value: str) -> str:
    cleaned = str(value or "").strip().casefold()
    if not cleaned:
        return ""
    compact = re.sub(rf"[{re.escape(string.punctuation)}\s]+", "", cleaned)
    if compact in {"true", "proved", "yes", "leantrue"}:
        return "True"
    if compact in {"false", "disproved", "no", "leanfalse"}:
        return "False"
    if "conditional" in compact or "hypothesis" in compact or "assuming" in compact:
        return "Conditional"
    if "unknown" in compact or "undetermined" in compact or "cannotdetermine" in compact:
        return "Unknown-from-statement"
    return str(value).strip()


def normalize_keyword_text(value: str) -> str:
    return (
        str(value or "")
        .casefold()
        .replace("≤", "<=")
        .replace("≥", ">=")
        .replace("×", "x")
    )


def caveat_hit(row: dict[str, Any], keywords: list[str]) -> bool | None:
    if not keywords:
        return None
    haystack = normalize_keyword_text(
        " ".join(
            [
                str(row.get("caveat", "")),
                str(row.get("reason", "")),
                str(row.get("raw_response", "")),
            ]
        )
    )
    return any(normalize_keyword_text(keyword) in haystack for keyword in keywords)


def load_reference(path: Path) -> tuple[list[str], dict[str, dict[str, Any]]]:
    """Load reference rows from the protocol JSON or a prompt-pack JSONL file."""
    text = path.read_text(encoding="utf-8").lstrip()
    if text.startswith("{"):
        protocol = json.loads(text)
        allowed_labels = list(
            protocol.get("allowed_labels")
            or protocol.get("allowed_template_labels")
            or DEFAULT_ALLOWED_LABELS
        )
        rows = protocol.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"{path} does not contain a protocol rows list")
    else:
        rows = read_jsonl(path)
        allowed_labels = sorted(
            {str(row["expected_template"]) for row in rows if row.get("expected_template")}
        ) or DEFAULT_ALLOWED_LABELS

    reference: dict[str, dict[str, Any]] = {}
    for row in rows:
        item_id = str(row.get("item_id", "")).strip()
        if not item_id:
            continue
        existing = reference.get(item_id, {})
        merged = {**existing, **row}
        merged.setdefault("expected_verdict", "True")
        merged.setdefault("caveat_keywords", [])
        merged.setdefault("a1_unknown_acceptable", True)
        reference[item_id] = merged

    if not reference:
        raise ValueError(f"no reference rows found in {path}")
    return allowed_labels, reference


def expected_condition(row: dict[str, Any]) -> str:
    condition = str(row.get("condition", "")).strip()
    if condition:
        return condition
    prompt_id = str(row.get("prompt_id", ""))
    if prompt_id.endswith("-A1"):
        return "A1"
    if prompt_id.endswith("-A2"):
        return "A2"
    return ""


def verdict_correct(predicted: str, expected: str, condition: str, reference: dict[str, Any]) -> bool:
    predicted_canon = canonical_verdict(predicted)
    expected_canon = canonical_verdict(expected)
    if predicted_canon == expected_canon:
        return True
    if (
        condition == "A1"
        and reference.get("a1_unknown_acceptable", True)
        and predicted_canon == "Unknown-from-statement"
    ):
        return True
    return False


def empty_confusion_matrix(allowed_labels: list[str]) -> dict[str, dict[str, int]]:
    columns = allowed_labels + [OTHER_LABEL]
    return {label: {column: 0 for column in columns} for label in allowed_labels}


def summarize_group(rows: list[dict[str, Any]], allowed_labels: list[str]) -> dict[str, Any]:
    n = len(rows)
    template_correct = sum(1 for row in rows if row["template_correct"])
    verdict_correct_count = sum(1 for row in rows if row["verdict_correct"])
    caveat_applicable = sum(1 for row in rows if row["caveat_applicable"])
    caveat_hits = sum(1 for row in rows if row["caveat_hit"] is True)

    matrix = empty_confusion_matrix(allowed_labels)
    for row in rows:
        expected = row["expected_template"]
        predicted = row["canonical_predicted_template"]
        if expected not in matrix:
            matrix[expected] = {label: 0 for label in allowed_labels + [OTHER_LABEL]}
        if predicted not in matrix[expected]:
            predicted = OTHER_LABEL
        matrix[expected][predicted] += 1

    return {
        "n": n,
        "template_correct": template_correct,
        "template_accuracy": template_correct / n if n else None,
        "verdict_correct": verdict_correct_count,
        "verdict_accuracy": verdict_correct_count / n if n else None,
        "caveat_applicable": caveat_applicable,
        "caveat_hits": caveat_hits,
        "caveat_hit_rate": caveat_hits / caveat_applicable if caveat_applicable else None,
        "confusion_matrix": matrix,
    }


def compute_gaps(by_condition: dict[str, dict[str, Any]]) -> dict[str, float | None]:
    gaps: dict[str, float | None] = {}
    for metric in ["template_accuracy", "verdict_accuracy", "caveat_hit_rate"]:
        a1 = by_condition.get("A1", {}).get(metric)
        a2 = by_condition.get("A2", {}).get(metric)
        gaps[f"A2_minus_A1_{metric}"] = a2 - a1 if a1 is not None and a2 is not None else None
    return gaps


def evaluate(
    predictions: list[dict[str, Any]],
    reference: dict[str, dict[str, Any]],
    allowed_labels: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    label_map = build_label_map(allowed_labels)
    scored_rows: list[dict[str, Any]] = []
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))

    for prediction in predictions:
        item_id = str(prediction.get("item_id", "")).strip()
        if not item_id and prediction.get("prompt_id"):
            item_id = str(prediction["prompt_id"]).rsplit("-", 1)[0]
        if item_id not in reference:
            raise ValueError(f"prediction references unknown item_id {item_id!r}")

        ref = reference[item_id]
        condition = expected_condition(prediction)
        model = str(prediction.get("model") or BLANK_MODEL)
        expected_template = str(ref["expected_template"])
        predicted_template = str(prediction.get("predicted_template", ""))
        canonical_predicted_template = canonical_label(predicted_template, label_map)
        expected_verdict = str(ref.get("expected_verdict", "True"))
        predicted_verdict = str(prediction.get("predicted_verdict", ""))
        canonical_predicted_verdict = canonical_verdict(predicted_verdict)
        caveat = caveat_hit(prediction, list(ref.get("caveat_keywords") or []))

        scored = {
            "model": model,
            "condition": condition,
            "run": prediction.get("run", ""),
            "prompt_id": prediction.get("prompt_id", ""),
            "item_id": item_id,
            "expected_template": expected_template,
            "predicted_template": predicted_template,
            "canonical_predicted_template": canonical_predicted_template,
            "template_correct": canonical_predicted_template == canonical_label(expected_template, label_map),
            "expected_verdict": expected_verdict,
            "predicted_verdict": predicted_verdict,
            "canonical_predicted_verdict": canonical_predicted_verdict,
            "verdict_correct": verdict_correct(predicted_verdict, expected_verdict, condition, ref),
            "caveat_applicable": caveat is not None,
            "caveat_hit": caveat,
            "reason": prediction.get("reason", ""),
            "caveat": prediction.get("caveat", ""),
            "raw_response": prediction.get("raw_response", ""),
        }
        scored_rows.append(scored)
        grouped[model][condition].append(scored)

    by_model_condition: dict[str, dict[str, Any]] = {}
    headline_gaps: dict[str, dict[str, float | None]] = {}
    for model, condition_rows in grouped.items():
        by_model_condition[model] = {}
        for condition, rows in sorted(condition_rows.items()):
            by_model_condition[model][condition] = summarize_group(rows, allowed_labels)
        headline_gaps[model] = compute_gaps(by_model_condition[model])

    summary = {
        "prediction_count": len(predictions),
        "allowed_labels": allowed_labels,
        "by_model_condition": by_model_condition,
        "headline_gaps": headline_gaps,
    }
    return summary, scored_rows


def write_row_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "model",
        "condition",
        "run",
        "prompt_id",
        "item_id",
        "expected_template",
        "predicted_template",
        "canonical_predicted_template",
        "template_correct",
        "expected_verdict",
        "predicted_verdict",
        "canonical_predicted_verdict",
        "verdict_correct",
        "caveat_applicable",
        "caveat_hit",
        "reason",
        "caveat",
        "raw_response",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate FiberRing Israel Set A predictions.")
    parser.add_argument(
        "--predictions",
        type=Path,
        default=Path("experiments/israel_setA_predictions.jsonl"),
        help="Predictions JSONL path.",
    )
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("data/israel_setA_A1_A2_protocol.json"),
        help="Protocol JSON path, or prompt-pack JSONL with expected_template fields.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("experiments/israel_setA_summary.json"),
        help="Summary JSON output path.",
    )
    parser.add_argument(
        "--row-csv-output",
        type=Path,
        default=Path("experiments/israel_setA_row_scores.csv"),
        help="Row-level CSV output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    allowed_labels, reference = load_reference(args.protocol)
    predictions = read_jsonl(args.predictions)
    summary, row_scores = evaluate(predictions, reference, allowed_labels)

    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_row_csv(args.row_csv_output, row_scores)

    print(
        json.dumps(
            {
                "prediction_count": summary["prediction_count"],
                "summary_output": str(args.summary_output),
                "row_csv_output": str(args.row_csv_output),
                "headline_gaps": summary["headline_gaps"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
