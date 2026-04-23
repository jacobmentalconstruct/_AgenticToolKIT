"""
FILE: prompt_rubric_judge.py
ROLE: Score prompt evaluation outputs against a rubric using a local Ollama judge model.
WHAT IT DOES:
  - Loads outputs from a prior ollama_prompt_lab run (or accepts inline)
  - Applies a rubric (list of criteria with descriptions and weights)
  - Sends each output + rubric to a judge model via Ollama
  - Parses scores and produces a structured scoring report
HOW TO USE:
  - python _ollama-prompt-lab/tools/prompt_rubric_judge.py metadata
  - python _ollama-prompt-lab/tools/prompt_rubric_judge.py run --input-json '{"judge_model": "qwen3:1.7b", "rubric": {...}, "outputs": [...]}'
  - python _ollama-prompt-lab/tools/prompt_rubric_judge.py run --input-json '{"judge_model": "qwen3:1.7b", "rubric": {...}, "run_dir": "artifacts/runs/..."}'
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import ensure_dir, now_stamp, standard_main, tool_result, tool_error, write_json


FILE_METADATA = {
    "tool_name": "prompt_rubric_judge",
    "version": "1.0.0",
    "entrypoint": "tools/prompt_rubric_judge.py",
    "category": "evaluation",
    "summary": "Score prompt evaluation outputs against a rubric using a local Ollama judge model.",
    "mcp_name": "prompt_rubric_judge",
    "input_schema": {
        "type": "object",
        "required": ["judge_model", "rubric"],
        "properties": {
            "judge_model": {
                "type": "string",
                "description": "Ollama model to use as the judge (e.g. 'qwen3:1.7b')."
            },
            "rubric": {
                "type": "object",
                "required": ["criteria"],
                "properties": {
                    "criteria": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "description"],
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "weight": {"type": "number", "default": 1.0}
                            }
                        },
                        "description": "List of scoring criteria."
                    },
                    "scale_min": {"type": "integer", "default": 1},
                    "scale_max": {"type": "integer", "default": 5}
                },
                "description": "Rubric definition with criteria and scoring scale."
            },
            "outputs": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Inline outputs to judge. Each: {id, prompt, response, model?}."
            },
            "run_dir": {
                "type": "string",
                "description": "Path to a prior ollama_prompt_lab run directory. Loads outputs from there."
            },
            "timeout_seconds": {
                "type": "integer",
                "default": 60,
                "description": "Timeout per judge call."
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save scoring results."
            }
        }
    }
}


def _build_judge_prompt(response: str, rubric: dict) -> str:
    """Build the scoring prompt for the judge model."""
    criteria = rubric["criteria"]
    scale_min = rubric.get("scale_min", 1)
    scale_max = rubric.get("scale_max", 5)

    criteria_text = ""
    for c in criteria:
        criteria_text += f"- {c['name']}: {c['description']}\n"

    return f"""You are a scoring judge. Rate the following response on each criterion using a scale of {scale_min} to {scale_max}.

CRITERIA:
{criteria_text}
RESPONSE TO JUDGE:
{response}

OUTPUT FORMAT: Return ONLY a JSON object with criterion names as keys and integer scores as values. Example:
{{{", ".join(f'"{c["name"]}": {scale_min}' for c in criteria)}}}

Return ONLY the JSON object, no other text."""


def _call_judge(model: str, prompt: str, timeout: int) -> dict[str, Any]:
    """Call the Ollama judge model and parse scores."""
    try:
        completed = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            return {"error": completed.stderr.strip() or "Non-zero exit"}

        raw = completed.stdout.strip()

        # Try to extract JSON from the response
        json_match = re.search(r"\{[^}]+\}", raw)
        if json_match:
            scores = json.loads(json_match.group())
            return {"scores": scores, "raw": raw}
        else:
            return {"error": "No JSON found in judge response", "raw": raw}

    except subprocess.TimeoutExpired:
        return {"error": "Judge model timed out"}
    except Exception as exc:
        return {"error": str(exc)}


def _load_outputs_from_dir(run_dir: Path) -> list[dict]:
    """Load outputs from a prior run's artifact directory."""
    outputs = []
    # Look for the summary or individual output files
    summary_file = run_dir / "summary.json"
    if summary_file.exists():
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        for entry in summary.get("results", []):
            outputs.append({
                "id": f"{entry.get('case_id', 'unknown')}_{entry.get('model', 'unknown')}",
                "prompt": entry.get("rendered_prompt", ""),
                "response": entry.get("response", ""),
                "model": entry.get("model", ""),
                "case_id": entry.get("case_id", ""),
            })
    if not outputs:
        # Fallback: look for individual .json files
        for f in sorted(run_dir.glob("*.json")):
            if f.name == "summary.json":
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if "response" in data:
                    outputs.append({
                        "id": f.stem,
                        "prompt": data.get("rendered_prompt", data.get("prompt", "")),
                        "response": data["response"],
                        "model": data.get("model", ""),
                    })
            except (json.JSONDecodeError, KeyError):
                continue
    return outputs


def run(arguments: dict) -> dict:
    judge_model = arguments["judge_model"]
    rubric = arguments["rubric"]
    timeout = arguments.get("timeout_seconds", 60)
    output_dir = arguments.get("output_dir")

    # Load outputs
    outputs = arguments.get("outputs", [])
    if not outputs and arguments.get("run_dir"):
        run_dir = Path(arguments["run_dir"])
        if not run_dir.is_dir():
            return tool_error(FILE_METADATA["tool_name"], arguments, f"Run directory not found: {run_dir}")
        outputs = _load_outputs_from_dir(run_dir)

    if not outputs:
        return tool_error(FILE_METADATA["tool_name"], arguments, "No outputs to judge. Provide 'outputs' or 'run_dir'.")

    criteria = rubric["criteria"]
    scale_max = rubric.get("scale_max", 5)

    try:
        scored: list[dict] = []
        errors: list[dict] = []

        for output in outputs:
            response_text = output.get("response", "")
            if not response_text:
                errors.append({"id": output.get("id"), "error": "Empty response"})
                continue

            prompt = _build_judge_prompt(response_text, rubric)
            judge_result = _call_judge(judge_model, prompt, timeout)

            entry: dict[str, Any] = {
                "id": output.get("id", "unknown"),
                "model": output.get("model", ""),
                "case_id": output.get("case_id", output.get("id", "")),
            }

            if "error" in judge_result:
                entry["error"] = judge_result["error"]
                entry["raw"] = judge_result.get("raw", "")
                errors.append(entry)
            else:
                scores = judge_result["scores"]
                # Compute weighted score
                total_weight = sum(c.get("weight", 1.0) for c in criteria)
                weighted_sum = 0.0
                for c in criteria:
                    score = scores.get(c["name"], 0)
                    weighted_sum += score * c.get("weight", 1.0)
                weighted_avg = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0

                entry["scores"] = scores
                entry["weighted_average"] = weighted_avg
                entry["normalized"] = round(weighted_avg / scale_max, 3)
                scored.append(entry)

        # Aggregate
        result: dict[str, Any] = {
            "judge_model": judge_model,
            "outputs_judged": len(scored),
            "errors": len(errors),
            "scored": scored,
        }
        if errors:
            result["error_details"] = errors

        # Overall averages per criterion
        if scored:
            criterion_avgs: dict[str, float] = {}
            for c in criteria:
                vals = [s["scores"].get(c["name"], 0) for s in scored if "scores" in s]
                criterion_avgs[c["name"]] = round(sum(vals) / len(vals), 2) if vals else 0
            result["criterion_averages"] = criterion_avgs
            result["overall_weighted_average"] = round(
                sum(s["weighted_average"] for s in scored) / len(scored), 2
            )

        # Save
        if output_dir:
            out_path = Path(output_dir)
            ensure_dir(out_path)
            write_json(out_path / "rubric_scores.json", result)
            result["saved_to"] = str(out_path / "rubric_scores.json")

        return tool_result(FILE_METADATA["tool_name"], arguments, result)

    except Exception as exc:
        return tool_error(FILE_METADATA["tool_name"], arguments, str(exc))


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
