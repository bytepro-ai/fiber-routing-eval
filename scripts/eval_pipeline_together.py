#!/usr/bin/env python3
"""Run the FiberRing routing prompts through Together AI.

The script writes JSONL rows compatible with tools/israel_setA_evaluate.py.
It uses the OpenAI-compatible Together endpoint and only depends on the
`openai` package in addition to the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


DEFAULT_MODELS = [
    "openai/gpt-oss-120b",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
]

SYSTEM_PROMPT = (
    "You are a careful evaluator for a Lean/FiberRing routing benchmark. "
    "Follow the requested output format exactly and choose one allowed template."
)

FIELD_NAMES = {
    "template": "predicted_template",
    "verdict": "predicted_verdict",
    "reason": "reason",
    "caveat": "caveat",
}


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


def load_existing_keys(path: Path) -> set[tuple[str, str, int]]:
    if not path.exists():
        return set()
    keys: set[tuple[str, str, int]] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError:
                print(f"warning: skipping invalid existing row {path}:{line_number}", file=sys.stderr)
                continue
            try:
                keys.add((str(row["prompt_id"]), str(row["model"]), int(row["run"])))
            except (KeyError, TypeError, ValueError):
                print(f"warning: skipping incomplete existing row {path}:{line_number}", file=sys.stderr)
    return keys


def clean_field(value: str) -> str:
    return value.strip().strip("`").strip()


def parse_response(raw_response: str) -> dict[str, str]:
    parsed = {
        "predicted_template": "",
        "predicted_verdict": "",
        "reason": "",
        "caveat": "",
    }

    text = raw_response.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {}
        for response_key, output_key in FIELD_NAMES.items():
            if response_key in data:
                parsed[output_key] = clean_field(str(data[response_key]))
            elif output_key in data:
                parsed[output_key] = clean_field(str(data[output_key]))
        if any(parsed.values()):
            return parsed

    for line in raw_response.splitlines():
        match = re.match(r"^\s*[-*]?\s*(Template|Verdict|Reason|Caveat)\s*:\s*(.*?)\s*$", line, re.I)
        if not match:
            continue
        label = match.group(1).lower()
        parsed[FIELD_NAMES[label]] = clean_field(match.group(2))

    return parsed


def is_retryable_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True
    if isinstance(status_code, int) and 500 <= status_code < 600:
        return True

    message = str(exc).lower()
    retry_markers = [
        "rate limit",
        "too many requests",
        "timeout",
        "temporarily unavailable",
        "connection",
        "server error",
        "service unavailable",
    ]
    return any(marker in message for marker in retry_markers)


def complete_with_retry(
    client: OpenAI,
    *,
    model: str,
    prompt_text: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    backoff_base: float,
) -> str:
    extra_kwargs: dict[str, Any] = {}
    if model == "openai/gpt-oss-120b":
        extra_kwargs["extra_body"] = {"reasoning": {"effort": "low"}}

    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_text},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                seed=0,
                **extra_kwargs,
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as exc:  # OpenAI SDK raises several transport/status subclasses.
            if attempt >= retries or not is_retryable_error(exc):
                raise
            retry_after = getattr(exc, "response", None)
            retry_after_value = None
            if retry_after is not None:
                headers = getattr(retry_after, "headers", {}) or {}
                retry_after_value = headers.get("retry-after") or headers.get("Retry-After")
            if retry_after_value:
                try:
                    delay = float(retry_after_value)
                except ValueError:
                    delay = backoff_base * (2**attempt)
            else:
                delay = backoff_base * (2**attempt)
            delay = min(delay, 90.0) + random.uniform(0.0, 0.5)
            print(
                f"retrying {model} after {type(exc).__name__} "
                f"(attempt {attempt + 1}/{retries}, sleep {delay:.1f}s)",
                file=sys.stderr,
            )
            time.sleep(delay)

    raise RuntimeError("unreachable retry loop exit")


def iter_jobs(
    prompts: Iterable[dict[str, Any]],
    models: list[str],
    runs: int,
) -> Iterable[tuple[dict[str, Any], str, int]]:
    for prompt in prompts:
        for model in models:
            for run in range(1, runs + 1):
                yield prompt, model, run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FiberRing routing prompts through Together AI.")
    parser.add_argument(
        "--prompt-pack",
        type=Path,
        default=Path("data/israel_setA_A1_A2_prompt_pack.jsonl"),
        help="Prompt-pack JSONL path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/israel_setA_predictions.jsonl"),
        help="Predictions JSONL output path.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help="Together model IDs to run.",
    )
    parser.add_argument("--runs", type=int, default=3, help="Runs per prompt per model.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--max-tokens", type=int, default=512, help="Maximum response tokens.")
    parser.add_argument("--retries", type=int, default=6, help="Retries for 429 and transient errors.")
    parser.add_argument("--backoff-base", type=float, default=2.0, help="Base seconds for exponential backoff.")
    parser.add_argument(
        "--resume",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip prompt/model/run rows already present in the output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs < 1:
        raise SystemExit("--runs must be >= 1")
    if args.retries < 0:
        raise SystemExit("--retries must be >= 0")

    prompts = read_jsonl(args.prompt_pack)
    if not prompts:
        raise SystemExit(f"no prompts found in {args.prompt_pack}")

    missing_prompt_text = [row.get("prompt_id", "<missing>") for row in prompts if not row.get("prompt_text")]
    if missing_prompt_text:
        raise SystemExit(f"prompt rows missing prompt_text: {missing_prompt_text[:5]}")

    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        raise SystemExit("TOGETHER_API_KEY is required; see .env.example")

    client = OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    existing_keys = load_existing_keys(args.output) if args.resume else set()
    mode = "a" if args.resume and args.output.exists() else "w"

    total_jobs = len(prompts) * len(args.models) * args.runs
    skipped = 0
    completed = 0

    with args.output.open(mode, encoding="utf-8") as handle:
        for prompt, model, run in iter_jobs(prompts, list(args.models), args.runs):
            prompt_id = str(prompt["prompt_id"])
            key = (prompt_id, model, run)
            if key in existing_keys:
                skipped += 1
                continue

            raw_response = complete_with_retry(
                client,
                model=model,
                prompt_text=str(prompt["prompt_text"]),
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                retries=args.retries,
                backoff_base=args.backoff_base,
            )
            parsed = parse_response(raw_response)
            output_row = {
                "prompt_id": prompt_id,
                "item_id": prompt.get("item_id", ""),
                "condition": prompt.get("condition", ""),
                "model": model,
                "run": run,
                "predicted_template": parsed["predicted_template"],
                "predicted_verdict": parsed["predicted_verdict"],
                "reason": parsed["reason"],
                "caveat": parsed["caveat"],
                "raw_response": raw_response,
            }
            handle.write(json.dumps(output_row, ensure_ascii=False) + "\n")
            handle.flush()
            completed += 1
            print(f"wrote {prompt_id} model={model} run={run}", file=sys.stderr)

    print(
        json.dumps(
            {
                "prompt_count": len(prompts),
                "models": args.models,
                "runs": args.runs,
                "total_jobs": total_jobs,
                "completed": completed,
                "skipped": skipped,
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
