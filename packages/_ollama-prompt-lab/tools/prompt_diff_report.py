"""
FILE: prompt_diff_report.py
ROLE: Compare outputs across two prompt evaluation runs.
WHAT IT DOES:
  - Loads outputs/scores from two run directories (baseline vs candidate)
  - Aligns by case_id and model
  - Reports: regressions, improvements, unchanged, new/missing cases
  - Optionally produces a character-level or line-level diff of responses
HOW TO USE:
  - python _ollama-prompt-lab/tools/prompt_diff_report.py metadata
  - python _ollama-prompt-lab/tools/prompt_diff_report.py run --input-json '{"baseline_dir": "artifacts/runs/run_a", "candidate_dir": "artifacts/runs/run_b"}'
"""

from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import ensure_dir, standard_main, tool_result, tool_error, write_json


FILE_METADATA = {
    "tool_name": "prompt_diff_report",
    "version": "1.0.0",
    "entrypoint": "tools/prompt_diff_report.py",
    "category": "reporting",
    "summary": "Compare outputs across two prompt evaluation runs: regressions, improvements, and diffs.",
    "mcp_name": "prompt_diff_report",
    "input_schema": {
        "type": "object",
        "required": ["baseline_dir", "candidate_dir"],
        "properties": {
            "baseline_dir": {
                "type": "string",
                "description": "Path to the baseline run directory."
            },
            "candidate_dir": {
                "type": "string",
                "description": "Path to the candidate (new) run directory."
            },
            "include_diffs": {
                "type": "boolean",
                "default": True,
                "description": "If true, include text diffs for changed responses."
            },
            "diff_context_lines": {
                "type": "integer",
                "default": 3,
                "description": "Number of context lines in unified diffs."
            },
            "output_file": {
                "type": "string",
                "description": "If set, save the report to this path."
            }
        }
    }
}


def _load_run_data(run_dir: Path) -> dict[str, dict]:
    """Load run outputs keyed by a composite ID (case_id + model)."""
    entries: dict[str, dict] = {}

    summary_file = run_dir / "summary.json"
    if summary_file.exists():
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        for entry in summary.get("results", []):
            case_id = entry.get("case_id", "unknown")
            model = entry.get("model", "unknown")
            key = f"{case_id}::{model}"
            entries[key] = {
                "case_id": case_id,
                "model": model,
                "response": entry.get("response", ""),
                "checks_passed": entry.get("checks_passed"),
                "checks_total": entry.get("checks_total"),
            }
        return entries

    # Fallback: individual files
    for f in sorted(run_dir.glob("*.json")):
        if f.name in {"summary.json", "rubric_scores.json"}:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            case_id = data.get("case_id", f.stem)
            model = data.get("model", "unknown")
            key = f"{case_id}::{model}"
            entries[key] = {
                "case_id": case_id,
                "model": model,
                "response": data.get("response", ""),
                "checks_passed": data.get("checks_passed"),
                "checks_total": data.get("checks_total"),
            }
        except (json.JSONDecodeError, KeyError):
            continue

    # Also load rubric scores if present
    scores_file = run_dir / "rubric_scores.json"
    if scores_file.exists():
        try:
            scores_data = json.loads(scores_file.read_text(encoding="utf-8"))
            for scored in scores_data.get("scored", []):
                # Match back to entries
                key = f"{scored.get('case_id', '')}::{scored.get('model', '')}"
                if key in entries:
                    entries[key]["weighted_average"] = scored.get("weighted_average")
                    entries[key]["scores"] = scored.get("scores")
        except (json.JSONDecodeError, KeyError):
            pass

    return entries


def _compute_diff(baseline_text: str, candidate_text: str, context: int) -> str | None:
    """Compute a unified diff between two responses."""
    if baseline_text == candidate_text:
        return None
    baseline_lines = baseline_text.splitlines(keepends=True)
    candidate_lines = candidate_text.splitlines(keepends=True)
    diff = difflib.unified_diff(
        baseline_lines, candidate_lines,
        fromfile="baseline", tofile="candidate",
        n=context
    )
    return "".join(diff) or None


def run(arguments: dict) -> dict:
    baseline_dir = Path(arguments["baseline_dir"])
    candidate_dir = Path(arguments["candidate_dir"])
    include_diffs = arguments.get("include_diffs", True)
    context_lines = arguments.get("diff_context_lines", 3)
    output_file = arguments.get("output_file")

    if not baseline_dir.is_dir():
        return tool_error(FILE_METADATA["tool_name"], arguments, f"Baseline dir not found: {baseline_dir}")
    if not candidate_dir.is_dir():
        return tool_error(FILE_METADATA["tool_name"], arguments, f"Candidate dir not found: {candidate_dir}")

    try:
        baseline = _load_run_data(baseline_dir)
        candidate = _load_run_data(candidate_dir)

        all_keys = set(baseline.keys()) | set(candidate.keys())
        only_baseline = set(baseline.keys()) - set(candidate.keys())
        only_candidate = set(candidate.keys()) - set(baseline.keys())
        common = set(baseline.keys()) & set(candidate.keys())

        improved: list[dict] = []
        regressed: list[dict] = []
        unchanged: list[dict] = []
        changed_no_score: list[dict] = []

        for key in sorted(common):
            b = baseline[key]
            c = candidate[key]

            entry: dict[str, Any] = {
                "case_id": b["case_id"],
                "model": b["model"],
            }

            # Compare scores if available
            b_score = b.get("weighted_average")
            c_score = c.get("weighted_average")

            # Fall back to check pass rates
            if b_score is None and b.get("checks_total"):
                b_score = (b.get("checks_passed", 0) / b["checks_total"]) if b["checks_total"] > 0 else None
            if c_score is None and c.get("checks_total"):
                c_score = (c.get("checks_passed", 0) / c["checks_total"]) if c["checks_total"] > 0 else None

            response_changed = b.get("response", "") != c.get("response", "")

            if b_score is not None and c_score is not None:
                entry["baseline_score"] = b_score
                entry["candidate_score"] = c_score
                entry["delta"] = round(c_score - b_score, 3)

                if c_score > b_score:
                    if include_diffs and response_changed:
                        diff = _compute_diff(b.get("response", ""), c.get("response", ""), context_lines)
                        if diff:
                            entry["diff"] = diff
                    improved.append(entry)
                elif c_score < b_score:
                    if include_diffs and response_changed:
                        diff = _compute_diff(b.get("response", ""), c.get("response", ""), context_lines)
                        if diff:
                            entry["diff"] = diff
                    regressed.append(entry)
                else:
                    unchanged.append(entry)
            elif response_changed:
                if include_diffs:
                    diff = _compute_diff(b.get("response", ""), c.get("response", ""), context_lines)
                    if diff:
                        entry["diff"] = diff
                changed_no_score.append(entry)
            else:
                unchanged.append(entry)

        result: dict[str, Any] = {
            "baseline_dir": str(baseline_dir),
            "candidate_dir": str(candidate_dir),
            "total_compared": len(common),
            "improved": len(improved),
            "regressed": len(regressed),
            "unchanged": len(unchanged),
            "changed_no_score": len(changed_no_score),
            "only_in_baseline": len(only_baseline),
            "only_in_candidate": len(only_candidate),
        }

        if improved:
            result["improvements"] = improved
        if regressed:
            result["regressions"] = regressed
        if changed_no_score:
            result["changed_unscored"] = changed_no_score
        if only_baseline:
            result["missing_in_candidate"] = sorted(only_baseline)
        if only_candidate:
            result["new_in_candidate"] = sorted(only_candidate)

        # Save
        if output_file:
            out_path = Path(output_file)
            ensure_dir(out_path.parent)
            write_json(out_path, result)
            result["saved_to"] = str(out_path.resolve())

        return tool_result(FILE_METADATA["tool_name"], arguments, result)

    except Exception as exc:
        return tool_error(FILE_METADATA["tool_name"], arguments, str(exc))


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
