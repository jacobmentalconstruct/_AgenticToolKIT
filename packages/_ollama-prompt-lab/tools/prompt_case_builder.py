"""
FILE: prompt_case_builder.py
ROLE: Generate structured test case files for prompt evaluation.
WHAT IT DOES:
  - Takes a template definition (fields, constraints, edge-case hints)
  - Produces a set of well-formed case JSON objects ready for ollama_prompt_lab
  - Supports manual case specification, combinatorial expansion, and edge-case seeding
  - Saves output as a reusable job file or returns inline
HOW TO USE:
  - python _ollama-prompt-lab/tools/prompt_case_builder.py metadata
  - python _ollama-prompt-lab/tools/prompt_case_builder.py run --input-json '{"fields": ["topic"], "values": {"topic": ["math", "history"]}, "checks": [{"type": "contains", "value": "answer"}]}'
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import ensure_dir, now_stamp, standard_main, tool_result, tool_error, write_json


FILE_METADATA = {
    "tool_name": "prompt_case_builder",
    "version": "1.0.0",
    "entrypoint": "tools/prompt_case_builder.py",
    "category": "evaluation",
    "summary": "Generate structured test case files for prompt evaluation from field definitions, value sets, and optional checks.",
    "mcp_name": "prompt_case_builder",
    "input_schema": {
        "type": "object",
        "required": ["fields", "values"],
        "properties": {
            "fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of field names used in prompt templates (e.g. ['topic', 'difficulty'])."
            },
            "values": {
                "type": "object",
                "description": "Map of field name -> list of possible values. Combinatorial expansion produces all combinations.",
                "additionalProperties": {"type": "array", "items": {}}
            },
            "manual_cases": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Explicit case objects to include as-is (bypass combinatorial expansion)."
            },
            "checks": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Default deterministic checks applied to every generated case. Each check: {type, value, field?}. Types: contains, not_contains, regex, min_length, max_length."
            },
            "edge_cases": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Edge case overrides: [{field: 'topic', value: '', label: 'empty_input'}]. Added as extra cases."
            },
            "id_prefix": {
                "type": "string",
                "default": "case",
                "description": "Prefix for auto-generated case IDs."
            },
            "output_file": {
                "type": "string",
                "description": "If set, saves the generated cases to this JSON file path."
            }
        }
    }
}


def _generate_combinatorial(fields: list[str], values: dict[str, list], id_prefix: str) -> list[dict]:
    """Generate all combinations of field values."""
    if not fields:
        return []

    # Get value lists in field order
    value_lists = [values.get(f, [""]) for f in fields]
    cases = []

    for i, combo in enumerate(itertools.product(*value_lists), start=1):
        case: dict[str, Any] = {"id": f"{id_prefix}_{i:03d}"}
        for field, val in zip(fields, combo):
            case[field] = val
        cases.append(case)

    return cases


def _generate_edge_cases(fields: list[str], edge_cases: list[dict], id_prefix: str, start_idx: int) -> list[dict]:
    """Generate edge cases from override specs."""
    cases = []
    for i, edge in enumerate(edge_cases, start=start_idx):
        case: dict[str, Any] = {"id": f"{id_prefix}_edge_{i:03d}"}
        # Fill defaults
        for f in fields:
            case[f] = edge.get(f, "")
        # Apply the specific edge value
        field = edge.get("field", "")
        if field:
            case[field] = edge.get("value", "")
        if edge.get("label"):
            case["_edge_label"] = edge["label"]
        cases.append(case)

    return cases


def _attach_checks(cases: list[dict], checks: list[dict] | None) -> list[dict]:
    """Attach default checks to cases that don't already have them."""
    if not checks:
        return cases
    for case in cases:
        if "checks" not in case:
            case["checks"] = checks
    return cases


def run(arguments: dict) -> dict:
    fields = arguments["fields"]
    values = arguments["values"]
    manual_cases = arguments.get("manual_cases", [])
    checks = arguments.get("checks")
    edge_cases = arguments.get("edge_cases", [])
    id_prefix = arguments.get("id_prefix", "case")
    output_file = arguments.get("output_file")

    try:
        # Generate combinatorial cases
        combo_cases = _generate_combinatorial(fields, values, id_prefix)

        # Generate edge cases
        edge_generated = _generate_edge_cases(
            fields, edge_cases, id_prefix, start_idx=len(combo_cases) + 1
        )

        # Merge all
        all_cases = combo_cases + edge_generated + manual_cases

        # Attach default checks
        all_cases = _attach_checks(all_cases, checks)

        # Save if requested
        if output_file:
            out_path = Path(output_file)
            ensure_dir(out_path.parent)
            write_json(out_path, {"cases": all_cases})

        result = {
            "case_count": len(all_cases),
            "combinatorial": len(combo_cases),
            "edge_cases": len(edge_generated),
            "manual_cases": len(manual_cases),
            "fields": fields,
            "cases": all_cases,
        }
        if output_file:
            result["saved_to"] = str(Path(output_file).resolve())

        return tool_result(FILE_METADATA["tool_name"], arguments, result)

    except Exception as exc:
        return tool_error(FILE_METADATA["tool_name"], arguments, str(exc))


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
