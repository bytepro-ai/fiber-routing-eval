#!/usr/bin/env python3
"""Check the Lean source-anchor manifest against the Set A/B protocols."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SET_A_PROTOCOL = ROOT / "data" / "israel_setA_A1_A2_protocol.json"
SET_B_PROTOCOL = ROOT / "data" / "israel_setB_A1_A2_protocol_2026-05-28.json"
MANIFEST = ROOT / "docs" / "lean_source_anchor_manifest.jsonl"

ALLOWED_ANCHOR_LEVELS = {
    "theorem",
    "theorem-family",
    "source-family",
    "source-gap",
}


def load_protocol(path: Path, set_name: str) -> dict[str, dict]:
    with path.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    rows = {}
    for row in payload["rows"]:
        item_id = row["item_id"]
        rows[item_id] = {
            "set": set_name,
            "expected_template": row["expected_template"],
            "witness_family": row["witness_family"],
            "audit_pointer": row["audit_pointer"],
        }
    return rows


def load_manifest(path: Path) -> dict[str, dict]:
    rows = {}
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            item_id = row.get("item_id")
            if item_id in rows:
                raise AssertionError(f"duplicate manifest item_id {item_id!r} at line {lineno}")
            rows[item_id] = row
    return rows


def pointer_from_ref(ref: dict) -> str:
    return f"{ref['path']}:{ref['line']}"


def main() -> None:
    protocol = {}
    protocol.update(load_protocol(SET_A_PROTOCOL, "A"))
    protocol.update(load_protocol(SET_B_PROTOCOL, "B"))
    manifest = load_manifest(MANIFEST)

    protocol_ids = set(protocol)
    manifest_ids = set(manifest)
    missing = sorted(protocol_ids - manifest_ids)
    extra = sorted(manifest_ids - protocol_ids)
    if missing or extra:
        raise AssertionError(f"manifest/protocol item mismatch: missing={missing}, extra={extra}")

    for item_id in sorted(protocol):
        expected = protocol[item_id]
        row = manifest[item_id]

        for key in ("set", "expected_template", "witness_family"):
            if row.get(key) != expected[key]:
                raise AssertionError(
                    f"{item_id}: {key} mismatch: manifest={row.get(key)!r}, "
                    f"protocol={expected[key]!r}"
                )

        if row.get("protocol_audit_pointer") != expected["audit_pointer"]:
            raise AssertionError(
                f"{item_id}: protocol_audit_pointer mismatch: "
                f"manifest={row.get('protocol_audit_pointer')!r}, "
                f"protocol={expected['audit_pointer']!r}"
            )

        anchor_level = row.get("anchor_level")
        if anchor_level not in ALLOWED_ANCHOR_LEVELS:
            raise AssertionError(f"{item_id}: unsupported anchor_level {anchor_level!r}")

        refs = row.get("source_refs")
        if not isinstance(refs, list) or not refs:
            raise AssertionError(f"{item_id}: source_refs must be a nonempty list")

        for index, ref in enumerate(refs):
            for key in ("path", "line", "lean_name", "kind"):
                if key not in ref:
                    raise AssertionError(f"{item_id}: source_refs[{index}] missing {key}")
            if not isinstance(ref["path"], str) or not ref["path"].startswith("lean4/"):
                raise AssertionError(f"{item_id}: invalid source path {ref['path']!r}")
            if not isinstance(ref["line"], int) or ref["line"] <= 0:
                raise AssertionError(f"{item_id}: invalid source line {ref['line']!r}")
            if not isinstance(ref["lean_name"], str) or not ref["lean_name"]:
                raise AssertionError(f"{item_id}: missing Lean declaration name")

        if expected["set"] == "B":
            first_pointer = pointer_from_ref(refs[0])
            if first_pointer != expected["audit_pointer"]:
                raise AssertionError(
                    f"{item_id}: first Set B source ref must mirror protocol pointer: "
                    f"{first_pointer!r} != {expected['audit_pointer']!r}"
                )

        if anchor_level == "theorem":
            theorem_refs = [ref for ref in refs if ref.get("kind") == "theorem"]
            if not theorem_refs:
                raise AssertionError(f"{item_id}: theorem-level row has no theorem ref")

        if anchor_level == "source-gap":
            note = row.get("review_note", "").lower()
            if "not located" not in note and "gap" not in note:
                raise AssertionError(f"{item_id}: source-gap row must explain the gap")

    print(f"OK: checked {len(manifest)} Lean source-anchor manifest rows")


if __name__ == "__main__":
    main()
