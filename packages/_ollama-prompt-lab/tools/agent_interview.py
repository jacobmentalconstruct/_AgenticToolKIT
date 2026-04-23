"""
FILE: agent_interview.py
ROLE: Run a scripted multi-turn interview with a local Ollama model.
WHAT IT DOES:
  - Takes an interview script (ordered questions with optional follow-ups)
  - Runs a multi-turn conversation with an Ollama model
  - Maintains conversation context across turns
  - Captures and evaluates responses per turn
  - Supports deterministic checks on individual responses
  - Saves the full transcript as an artifact
HOW TO USE:
  - python _ollama-prompt-lab/tools/agent_interview.py metadata
  - python _ollama-prompt-lab/tools/agent_interview.py run --input-json '{"model": "qwen3:1.7b", "script": {"system": "...", "turns": [...]}}'
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
    "tool_name": "agent_interview",
    "version": "1.0.0",
    "entrypoint": "tools/agent_interview.py",
    "category": "evaluation",
    "summary": "Run a scripted multi-turn interview with a local Ollama model to test context retention, constraint following, and coherence.",
    "mcp_name": "agent_interview",
    "input_schema": {
        "type": "object",
        "required": ["model", "script"],
        "properties": {
            "model": {
                "type": "string",
                "description": "Ollama model to interview (e.g. 'qwen3:1.7b')."
            },
            "script": {
                "type": "object",
                "required": ["turns"],
                "properties": {
                    "system": {
                        "type": "string",
                        "description": "System prompt / context provided before the conversation."
                    },
                    "turns": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["question"],
                            "properties": {
                                "id": {"type": "string"},
                                "question": {"type": "string"},
                                "checks": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                    "description": "Deterministic checks: {type, value}. Types: contains, not_contains, regex, min_length."
                                },
                                "follow_up": {
                                    "type": "string",
                                    "description": "Follow-up question sent if the main question's response fails checks."
                                }
                            }
                        },
                        "description": "Ordered list of interview turns."
                    }
                },
                "description": "Interview script with optional system prompt and ordered turns."
            },
            "timeout_seconds": {
                "type": "integer",
                "default": 60,
                "description": "Timeout per turn."
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the interview transcript."
            }
        }
    }
}


ANSI_PATTERN = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _clean_response(text: str) -> str:
    """Strip ANSI codes and normalize whitespace."""
    cleaned = ANSI_PATTERN.sub("", text)
    return cleaned.strip()


def _build_conversation_prompt(system: str, history: list[dict], question: str) -> str:
    """Build a full conversation prompt with history for a single Ollama call."""
    parts = []
    if system:
        parts.append(f"[System]\n{system}\n")

    for turn in history:
        parts.append(f"[User]\n{turn['question']}\n")
        parts.append(f"[Assistant]\n{turn['response']}\n")

    parts.append(f"[User]\n{question}\n")
    parts.append("[Assistant]\n")

    return "\n".join(parts)


def _call_model(model: str, prompt: str, timeout: int) -> dict[str, Any]:
    """Call Ollama with the conversation prompt."""
    started = time.perf_counter()
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
        duration = round(time.perf_counter() - started, 3)

        if completed.returncode != 0:
            return {"error": completed.stderr.strip() or "Non-zero exit", "duration": duration}

        response = _clean_response(completed.stdout)
        return {"response": response, "duration": duration}

    except subprocess.TimeoutExpired:
        return {"error": "Timed out", "duration": round(time.perf_counter() - started, 3)}
    except Exception as exc:
        return {"error": str(exc), "duration": 0}


def _run_checks(response: str, checks: list[dict]) -> list[dict]:
    """Run deterministic checks on a response."""
    results = []
    for check in checks:
        check_type = check.get("type", "")
        value = check.get("value", "")
        passed = False

        if check_type == "contains":
            passed = value.lower() in response.lower()
        elif check_type == "not_contains":
            passed = value.lower() not in response.lower()
        elif check_type == "regex":
            passed = bool(re.search(value, response, re.IGNORECASE))
        elif check_type == "min_length":
            passed = len(response) >= int(value)

        results.append({
            "type": check_type,
            "value": value,
            "passed": passed,
        })

    return results


def run(arguments: dict) -> dict:
    model = arguments["model"]
    script = arguments["script"]
    timeout = arguments.get("timeout_seconds", 60)
    output_dir = arguments.get("output_dir")

    system = script.get("system", "")
    turns = script["turns"]

    if not turns:
        return tool_error(FILE_METADATA["tool_name"], arguments, "Script has no turns.")

    try:
        history: list[dict] = []
        transcript: list[dict] = []
        total_checks = 0
        checks_passed = 0
        total_duration = 0.0

        for i, turn in enumerate(turns):
            turn_id = turn.get("id", f"turn_{i+1:02d}")
            question = turn["question"]
            checks = turn.get("checks", [])

            # Build prompt with full conversation history
            prompt = _build_conversation_prompt(system, history, question)
            result = _call_model(model, prompt, timeout)

            turn_record: dict[str, Any] = {
                "turn_id": turn_id,
                "question": question,
                "duration": result.get("duration", 0),
            }
            total_duration += result.get("duration", 0)

            if "error" in result:
                turn_record["error"] = result["error"]
                transcript.append(turn_record)
                continue

            response = result["response"]
            turn_record["response"] = response
            history.append({"question": question, "response": response})

            # Run checks
            if checks:
                check_results = _run_checks(response, checks)
                turn_record["checks"] = check_results
                passed = sum(1 for c in check_results if c["passed"])
                turn_record["checks_passed"] = passed
                turn_record["checks_total"] = len(check_results)
                total_checks += len(check_results)
                checks_passed += passed

                # Follow-up if checks failed
                all_passed = all(c["passed"] for c in check_results)
                if not all_passed and turn.get("follow_up"):
                    follow_prompt = _build_conversation_prompt(system, history, turn["follow_up"])
                    follow_result = _call_model(model, follow_prompt, timeout)
                    if "response" in follow_result:
                        turn_record["follow_up_question"] = turn["follow_up"]
                        turn_record["follow_up_response"] = follow_result["response"]
                        history.append({"question": turn["follow_up"], "response": follow_result["response"]})
                        total_duration += follow_result.get("duration", 0)

            transcript.append(turn_record)

        # Summary
        result_data: dict[str, Any] = {
            "model": model,
            "turns_completed": len(transcript),
            "turns_with_errors": sum(1 for t in transcript if "error" in t),
            "total_duration_seconds": round(total_duration, 3),
            "transcript": transcript,
        }
        if total_checks > 0:
            result_data["checks_passed"] = checks_passed
            result_data["checks_total"] = total_checks
            result_data["check_pass_rate"] = round(checks_passed / total_checks, 3)

        # Save
        if output_dir:
            out_path = Path(output_dir)
            ensure_dir(out_path)
            write_json(out_path / f"interview_{model.replace(':', '_')}_{now_stamp()}.json", result_data)
            result_data["saved_to"] = str(out_path)

        return tool_result(FILE_METADATA["tool_name"], arguments, result_data)

    except Exception as exc:
        return tool_error(FILE_METADATA["tool_name"], arguments, str(exc))


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
