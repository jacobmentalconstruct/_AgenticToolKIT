"""Local Ollama-backed sidecar agent runtime floor."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import ensure_dir, standard_main, tool_error, tool_result, write_json
from lib.text_workspace import resolve_project_root, runtime_root, safe_relative
from tools.directory_scaffold import FILE_METADATA as DIRECTORY_SCAFFOLD_METADATA, run as run_directory_scaffold
from tools.git_private_workspace import FILE_METADATA as GIT_PRIVATE_METADATA, run as run_git_private_workspace
from tools.journal_write import FILE_METADATA as JOURNAL_WRITE_METADATA, run as run_journal_write
from tools.agent_run_trace import run as run_agent_run_trace
from tools.local_agent_bootstrap import run as run_local_agent_bootstrap
from tools.project_setup import run as run_project_setup
from tools.session_evidence_store import FILE_METADATA as SESSION_EVIDENCE_METADATA, run as run_session_evidence_store
from tools.text_file_reader import FILE_METADATA as TEXT_FILE_READER_METADATA, run as run_text_file_reader
from tools.text_file_validator import FILE_METADATA as TEXT_FILE_VALIDATOR_METADATA, run as run_text_file_validator
from tools.text_file_writer import FILE_METADATA as TEXT_FILE_WRITER_METADATA, run as run_text_file_writer
from tools.workspace_boundary_audit import run as run_workspace_boundary_audit


FILE_METADATA = {
    "tool_name": "local_sidecar_agent",
    "version": "1.0.0",
    "entrypoint": "src/tools/local_sidecar_agent.py",
    "category": "agent-runtime",
    "summary": "Run the safe floor of an Ollama-backed local sidecar agent through guarded toolbox tools.",
    "mcp_name": "local_sidecar_agent",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["status", "models", "run"], "default": "run"},
            "project_root": {"type": "string", "default": "."},
            "prompt": {"type": "string", "description": "User task for the local sidecar agent."},
            "ollama_base_url": {"type": "string", "default": "http://localhost:11434"},
            "planner_model": {"type": "string", "default": "qwen2.5-coder:7b"},
            "response_model": {"type": "string", "default": "qwen3.5:4b"},
            "timeout_seconds": {"type": "number", "default": 60},
            "max_tool_rounds": {"type": "integer", "default": 4},
            "allowed_tools": {"type": "array", "items": {"type": "string"}},
            "confirm_mutations": {"type": "boolean", "default": False},
            "confirm_checkpoint": {"type": "boolean", "default": False},
            "checkpoint": {"type": "boolean", "default": True},
            "confirm_evidence": {"type": "boolean", "default": False},
            "session_id": {"type": "string"},
            "window_turns": {"type": "integer", "default": 8},
            "use_evidence_shelf": {"type": "boolean", "default": True},
            "write_trace": {"type": "boolean", "default": True},
            "mock_ollama_failure": {
                "type": "string",
                "enum": ["request_timeout", "ollama_unreachable", "model_missing"],
                "description": "Deterministic model transport failure for smoke tests.",
            },
            "mock_ollama_responses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Deterministic model responses for smoke tests.",
            },
            "write_session": {"type": "boolean", "default": True},
        },
        "additionalProperties": False,
    },
}


TOOL_CALL_RE = re.compile(r"```tool_call\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
DEFAULT_ALLOWED_TOOLS = [
    "text_file_reader",
    "text_file_writer",
    "directory_scaffold",
    "text_file_validator",
    "git_private_workspace",
    "journal_write",
    "session_evidence_store",
]
MUTATING_TOOLS = {"text_file_writer", "directory_scaffold", "journal_write"}
MUTATING_EVIDENCE_ACTIONS = {"init", "append", "archive_window", "export"}
RISKY_GIT_ACTIONS = {"init", "add", "commit", "checkout", "pull", "push"}


@dataclass
class AgentConfig:
    project_root: str
    ollama_base_url: str = "http://localhost:11434"
    planner_model: str = "qwen2.5-coder:7b"
    response_model: str = "qwen3.5:4b"
    timeout_seconds: int = 60
    max_tool_rounds: int = 4
    allowed_tools: list[str] = field(default_factory=lambda: list(DEFAULT_ALLOWED_TOOLS))
    confirm_mutations: bool = False
    confirm_checkpoint: bool = False
    checkpoint: bool = True
    confirm_evidence: bool = False
    session_id: str = ""
    window_turns: int = 8
    use_evidence_shelf: bool = True
    write_trace: bool = True


TOOL_REGISTRY: dict[str, tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "text_file_reader": (TEXT_FILE_READER_METADATA, run_text_file_reader),
    "text_file_writer": (TEXT_FILE_WRITER_METADATA, run_text_file_writer),
    "directory_scaffold": (DIRECTORY_SCAFFOLD_METADATA, run_directory_scaffold),
    "text_file_validator": (TEXT_FILE_VALIDATOR_METADATA, run_text_file_validator),
    "git_private_workspace": (GIT_PRIVATE_METADATA, run_git_private_workspace),
    "journal_write": (JOURNAL_WRITE_METADATA, run_journal_write),
    "session_evidence_store": (SESSION_EVIDENCE_METADATA, run_session_evidence_store),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def _runtime_paths(project_root: Path) -> dict[str, Path]:
    base = runtime_root(project_root) / "local_agent"
    return {
        "base": base,
        "sessions": base / "sessions",
        "logs": base / "logs",
        "state": base / "state",
        "runs": base / "runs",
        "outputs": base / "outputs",
        "parts": base / "parts",
        "ref": base / "ref",
        "tools": base / "tools",
        "audit_log": base / "logs" / "audit.jsonl",
        "action_journal": base / "logs" / "action_journal.jsonl",
    }


def _ensure_runtime(project_root: Path) -> dict[str, Path]:
    paths = _runtime_paths(project_root)
    for key in ["base", "sessions", "logs", "state", "runs", "outputs", "parts", "ref", "tools"]:
        ensure_dir(paths[key])
    return paths


def _public_runtime(paths: dict[str, Path], project_root: Path) -> dict[str, str]:
    return {
        key: safe_relative(value, project_root)
        for key, value in paths.items()
        if key not in {"audit_log", "action_journal"}
    }


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _timeout(arguments: dict[str, Any]) -> int:
    try:
        value = int(arguments.get("timeout_seconds", 60))
    except (TypeError, ValueError):
        return 60
    return max(1, min(value, 300))


def _config(arguments: dict[str, Any], project_root: Path) -> AgentConfig:
    allowed_tools = arguments.get("allowed_tools")
    if not isinstance(allowed_tools, list) or not allowed_tools:
        allowed = list(DEFAULT_ALLOWED_TOOLS)
    else:
        allowed = [str(item) for item in allowed_tools]
    try:
        max_rounds = int(arguments.get("max_tool_rounds", 4))
    except (TypeError, ValueError):
        max_rounds = 4
    try:
        window_turns = int(arguments.get("window_turns", 8))
    except (TypeError, ValueError):
        window_turns = 8
    return AgentConfig(
        project_root=str(project_root),
        ollama_base_url=str(arguments.get("ollama_base_url", "http://localhost:11434")).rstrip("/"),
        planner_model=str(arguments.get("planner_model", "qwen2.5-coder:7b")),
        response_model=str(arguments.get("response_model", "qwen3.5:4b")),
        timeout_seconds=_timeout(arguments),
        max_tool_rounds=max(1, min(max_rounds, 12)),
        allowed_tools=allowed,
        confirm_mutations=arguments.get("confirm_mutations") is True,
        confirm_checkpoint=arguments.get("confirm_checkpoint") is True,
        checkpoint=arguments.get("checkpoint", True) is not False,
        confirm_evidence=arguments.get("confirm_evidence") is True,
        session_id=str(arguments.get("session_id", "")).strip(),
        window_turns=max(0, min(window_turns, 50)),
        use_evidence_shelf=arguments.get("use_evidence_shelf", True) is not False,
        write_trace=arguments.get("write_trace", True) is not False,
    )


def _scan_models(base_url: str, timeout: int) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"available": False, "base_url": base_url, "models": [], "error": str(exc)}
    models = data.get("models", []) if isinstance(data, dict) else []
    names = [item.get("name", "") for item in models if isinstance(item, dict)]
    return {"available": True, "base_url": base_url, "models": names, "model_count": len(names)}


def _ollama_chat(config: AgentConfig, messages: list[dict[str, str]], model: str) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    request = urllib.request.Request(
        f"{config.ollama_base_url}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
        data = json.loads(response.read().decode("utf-8"))
    message = data.get("message", {}) if isinstance(data, dict) else {}
    content = message.get("content", "") if isinstance(message, dict) else ""
    return str(content)


def _sanitize_model_text(text: str) -> str:
    return THINK_RE.sub("", text).strip()


def _tool_catalog_text(allowed_tools: list[str]) -> str:
    lines = []
    for name in allowed_tools:
        item = TOOL_REGISTRY.get(name)
        if not item:
            continue
        metadata, _ = item
        lines.append(f"- {name}: {metadata.get('summary', '')}")
        props = metadata.get("input_schema", {}).get("properties", {})
        if props:
            lines.append(f"  args: {', '.join(sorted(props.keys()))}")
    return "\n".join(lines)


def _system_prompt(config: AgentConfig, bootstrap_summary: str, evidence_summary: str) -> str:
    return (
        "You are a local sidecar agent. Use only the listed toolbox tools.\n"
        "Never claim a file was created, modified, or validated unless a tool result proves it.\n"
        "Return tool calls as fenced JSON blocks exactly like:\n"
        "```tool_call\n{\"tool\":\"text_file_reader\",\"arguments\":{\"path\":\"README.md\"}}\n```\n"
        "Do not use raw shell, PowerShell, cmd, bash, cat, echo, or arbitrary commands.\n"
        "All paths are relative to the project root; the runtime injects project_root.\n\n"
        f"Project root: {config.project_root}\n"
        f"Allowed tools:\n{_tool_catalog_text(config.allowed_tools)}\n\n"
        f"Bootstrap summary:\n{bootstrap_summary[:3000]}\n\n"
        f"Evidence Shelf:\n{evidence_summary[:2000]}"
    )


def _parse_tool_calls(text: str) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for match in TOOL_CALL_RE.finditer(text):
        raw = match.group(1).strip()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            calls.append({"tool": "__malformed__", "arguments": {}, "raw": raw, "error": str(exc)})
            continue
        if not isinstance(payload, dict):
            calls.append({"tool": "__malformed__", "arguments": {}, "raw": raw, "error": "tool_call must be a JSON object"})
            continue
        tool_name = str(payload.get("tool", payload.get("name", ""))).strip()
        arguments = payload.get("arguments", payload.get("args", {}))
        if not isinstance(arguments, dict):
            calls.append({"tool": "__malformed__", "arguments": {}, "raw": raw, "error": "arguments must be an object"})
            continue
        calls.append({"tool": tool_name, "arguments": arguments, "raw": raw})
    return calls


def _validate_schema(metadata: dict[str, Any], args: dict[str, Any]) -> list[str]:
    schema = metadata.get("input_schema", {})
    props = schema.get("properties", {})
    errors: list[str] = []
    if schema.get("additionalProperties") is False:
        for key in args:
            if key not in props:
                errors.append(f"unexpected argument: {key}")
    for key, spec in props.items():
        if key not in args:
            continue
        value = args[key]
        expected = spec.get("type") if isinstance(spec, dict) else None
        if expected == "string" and not isinstance(value, str):
            errors.append(f"{key} must be a string")
        elif expected == "boolean" and not isinstance(value, bool):
            errors.append(f"{key} must be a boolean")
        elif expected == "array" and not isinstance(value, list):
            errors.append(f"{key} must be an array")
        elif expected == "object" and not isinstance(value, dict):
            errors.append(f"{key} must be an object")
        elif expected == "integer" and not isinstance(value, int):
            errors.append(f"{key} must be an integer")
        enum = spec.get("enum") if isinstance(spec, dict) else None
        if enum and value not in enum:
            errors.append(f"{key} must be one of: {', '.join(map(str, enum))}")
    return errors


def _is_mutating(tool_name: str, args: dict[str, Any]) -> bool:
    if tool_name == "git_private_workspace":
        return str(args.get("action", "status")) in RISKY_GIT_ACTIONS
    if tool_name == "session_evidence_store":
        return str(args.get("action", "status")) in MUTATING_EVIDENCE_ACTIONS
    return tool_name in MUTATING_TOOLS


def _inject_confirm(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    updated = dict(args)
    if tool_name in {"text_file_writer", "directory_scaffold", "git_private_workspace", "session_evidence_store"}:
        updated["confirm"] = True
    return updated


def _execute_tool_call(
    call: dict[str, Any],
    *,
    config: AgentConfig,
    project_root: Path,
    runtime_paths: dict[str, Path],
    touched_paths: list[str],
) -> dict[str, Any]:
    tool_name = call["tool"]
    if tool_name == "__malformed__":
        return {
            "status": "error",
            "tool": "__malformed__",
            "input": call,
            "result": {"message": call.get("error", "malformed tool call"), "raw": call.get("raw", "")[:800]},
        }
    if tool_name not in config.allowed_tools:
        return tool_error("local_sidecar_agent", call, f"tool is not allowlisted: {tool_name}")
    entry = TOOL_REGISTRY.get(tool_name)
    if not entry:
        return tool_error("local_sidecar_agent", call, f"unknown tool: {tool_name}")
    metadata, runner = entry
    args = dict(call.get("arguments", {}))
    args["project_root"] = str(project_root)
    schema_errors = _validate_schema(metadata, args)
    if schema_errors:
        return tool_error("local_sidecar_agent", call, "; ".join(schema_errors))
    mutating = _is_mutating(tool_name, args)
    if mutating and not config.confirm_mutations:
        return tool_result(
            "local_sidecar_agent",
            call,
            {
                "approval_required": True,
                "tool": tool_name,
                "reason": "mutating tool call requires confirm_mutations=true",
                "arguments": args,
            },
            status="approval_required",
        )
    if mutating:
        args = _inject_confirm(tool_name, args)
    started = time.time()
    result = runner(args)
    duration_ms = round((time.time() - started) * 1000)
    _append_jsonl(
        runtime_paths["audit_log"],
        {
            "ts": _now(),
            "tool": tool_name,
            "status": result.get("status"),
            "duration_ms": duration_ms,
            "mutating": mutating,
        },
    )
    if result.get("status") == "ok":
        payload = result.get("result", {})
        if isinstance(payload, dict) and payload.get("path"):
            touched_paths.append(str(payload["path"]))
        if tool_name == "directory_scaffold":
            for item in payload.get("entries", []) if isinstance(payload, dict) else []:
                if isinstance(item, dict) and item.get("path"):
                    touched_paths.append(str(item["path"]))
    return result


def _format_tool_results(results: list[dict[str, Any]]) -> str:
    slim = []
    for result in results:
        text = json.dumps(result, sort_keys=True)
        slim.append(text[:4000])
    return "\n".join(f"[tool_result]\n{item}\n[/tool_result]" for item in slim)


def _validate_touched(project_root: Path, touched_paths: list[str]) -> dict[str, Any]:
    unique = sorted(set(touched_paths))
    checks = []
    for rel in unique:
        path = project_root / rel
        checks.append({"path": rel, "exists": path.exists(), "is_file": path.is_file()})
    return {
        "touched_paths": unique,
        "checks": checks,
        "valid": all(item["exists"] for item in checks),
    }


def _checkpoint(project_root: Path, touched_paths: list[str], config: AgentConfig, summary: str) -> dict[str, Any]:
    if not config.checkpoint or not touched_paths:
        return {"skipped": True, "reason": "checkpoint disabled or no touched paths"}
    if not config.confirm_checkpoint:
        return {"skipped": True, "approval_required": True, "reason": "checkpoint requires confirm_checkpoint=true"}
    init = run_git_private_workspace({"project_root": str(project_root), "action": "init", "confirm": True})
    if init.get("status") != "ok":
        return {"skipped": False, "status": "error", "step": "init", "result": init}
    add = run_git_private_workspace({
        "project_root": str(project_root),
        "action": "add",
        "paths": sorted(set(touched_paths)),
        "confirm": True,
    })
    if add.get("status") != "ok":
        return {"skipped": False, "status": "error", "step": "add", "result": add}
    message = f"local_sidecar_agent checkpoint | files={len(set(touched_paths))} | {summary[:80]}"
    commit = run_git_private_workspace({
        "project_root": str(project_root),
        "action": "commit",
        "message": message,
        "confirm": True,
    })
    return {"skipped": False, "status": commit.get("status"), "message": message, "result": commit}


def _model_response(
    *,
    config: AgentConfig,
    messages: list[dict[str, str]],
    model: str,
    mock_responses: list[str],
    mock_failure: str,
    round_index: int,
) -> str:
    if round_index == 0 and mock_failure:
        if mock_failure == "request_timeout":
            raise TimeoutError("timed out")
        if mock_failure == "ollama_unreachable":
            raise urllib.error.URLError("connection refused")
        if mock_failure == "model_missing":
            raise RuntimeError(f"model not found: {model}")
    if mock_responses:
        if round_index < len(mock_responses):
            return mock_responses[round_index]
        return "No further tool calls."
    return _ollama_chat(config, messages, model)


def _evidence_shelf_text(evidence_shelf: dict[str, Any]) -> str:
    payload = evidence_shelf.get("result", {}) if isinstance(evidence_shelf, dict) else {}
    if not isinstance(payload, dict) or not payload:
        return "No Evidence Shelf available."
    lines = [
        f"Session: {payload.get('session_id', '')}",
        f"Items: {payload.get('item_count', 0)}",
    ]
    if payload.get("rolling_summary"):
        lines.append(f"Summary: {payload.get('rolling_summary')}")
    for label in ["open_loops", "decisions"]:
        values = payload.get(label, [])
        if isinstance(values, list) and values:
            lines.append(f"{label.replace('_', ' ').title()}:")
            lines.extend(f"- {item}" for item in values[:8])
    index = payload.get("item_index", [])
    if isinstance(index, list) and index:
        lines.append("Evidence Index:")
        for item in index[:12]:
            if isinstance(item, dict):
                lines.append(f"- {item.get('item_id')}: {item.get('summary')}")
    return "\n".join(lines)


def _evidence_turns(prompt: str, rounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = [{
        "sequence": 1,
        "role": "user",
        "kind": "user_turn",
        "content": prompt,
        "summary": f"User prompt: {prompt[:160]}",
        "tags": ["local-agent", "user-turn"],
    }]
    sequence = 2
    for round_item in rounds:
        response = str(round_item.get("response", ""))
        if response:
            turns.append({
                "sequence": sequence,
                "role": "assistant",
                "kind": "agent_round",
                "content": response,
                "summary": f"Agent round {round_item.get('round')}: {response[:160]}",
                "tags": ["local-agent", "agent-round"],
            })
            sequence += 1
        results = round_item.get("results", [])
        if isinstance(results, list) and results:
            tools = [str(result.get("tool", "")) for result in results if isinstance(result, dict) and result.get("tool")]
            turns.append({
                "sequence": sequence,
                "role": "tool",
                "kind": "tool_result",
                "content": json.dumps(results, indent=2, sort_keys=False),
                "summary": f"Tool results for round {round_item.get('round')}: {', '.join(tools) or 'none'}",
                "tags": ["local-agent", "tool-result"],
                "tools": tools,
            })
            sequence += 1
    return turns


def _archive_evidence(
    project_root: Path,
    *,
    session_id: str,
    prompt: str,
    rounds: list[dict[str, Any]],
    config: AgentConfig,
    approval_required: bool,
) -> dict[str, Any]:
    if not config.use_evidence_shelf:
        return {"skipped": True, "reason": "use_evidence_shelf=false"}
    if not config.confirm_evidence:
        return {"skipped": True, "approval_required": True, "reason": "evidence archive requires confirm_evidence=true"}
    turns = _evidence_turns(prompt, rounds)
    return run_session_evidence_store({
        "project_root": str(project_root),
        "action": "archive_window",
        "confirm": True,
        "session_id": session_id,
        "turns": turns,
        "window_turns": config.window_turns,
        "rolling_summary": f"Local agent session evidence for latest prompt: {prompt[:160]}",
        "open_loops": ["Approval required before continuing."] if approval_required else [],
        "tags": ["local-agent", "bag-of-evidence"],
    })


def _recovery_from_exception(exc: Exception, config: AgentConfig) -> dict[str, Any]:
    message = str(exc)
    lowered = message.lower()
    if isinstance(exc, TimeoutError) or "timed out" in lowered or "timeout" in lowered:
        recovery_class = "request_timeout"
        next_actions = ["increase_timeout", "retry_run", "refresh_models"]
    elif isinstance(exc, urllib.error.URLError) or "connection refused" in lowered or "failed to establish" in lowered:
        recovery_class = "ollama_unreachable"
        next_actions = ["check_ollama_service", "refresh_models", "retry_run"]
    elif "model" in lowered and ("not found" in lowered or "missing" in lowered):
        recovery_class = "model_missing"
        next_actions = ["refresh_models", "choose_available_model", "retry_run"]
    else:
        recovery_class = "model_request_failed"
        next_actions = ["inspect_details", "refresh_models", "retry_run"]
    return {
        "class": recovery_class,
        "message": message,
        "next_actions": next_actions,
        "selected_models": {
            "planner_model": config.planner_model,
            "response_model": config.response_model,
        },
        "timeout_seconds": config.timeout_seconds,
    }


def _evidence_ids(evidence_archive: dict[str, Any]) -> list[str]:
    payload = evidence_archive.get("result", evidence_archive)
    evidence_items = payload.get("archived_items", []) if isinstance(payload, dict) else []
    return [
        str(item.get("item_id"))
        for item in evidence_items
        if isinstance(item, dict) and item.get("item_id")
    ]


def _trace_payload(
    *,
    session_id: str,
    prompt: str,
    config: AgentConfig,
    status: str,
    recovery: dict[str, Any] | None,
    rounds: list[dict[str, Any]],
    touched_paths: list[str],
    validation: dict[str, Any],
    evidence_ids: list[str],
    journal_entry_uid: str,
    duration_ms: int,
    summary: str,
) -> dict[str, Any]:
    tool_results: list[dict[str, Any]] = []
    for round_item in rounds:
        for result in round_item.get("results", []):
            if isinstance(result, dict):
                tool_results.append({
                    "round": round_item.get("round"),
                    "tool": result.get("tool"),
                    "status": result.get("status"),
                })
    return {
        "action": "append",
        "confirm": True,
        "session_id": session_id,
        "status": status,
        "recovery_class": (recovery or {}).get("class", ""),
        "recovery_message": (recovery or {}).get("message", ""),
        "prompt": prompt,
        "summary": summary,
        "selected_models": {
            "planner_model": config.planner_model,
            "response_model": config.response_model,
            "ollama_base_url": config.ollama_base_url,
            "timeout_seconds": config.timeout_seconds,
        },
        "allowed_tools": config.allowed_tools,
        "tool_calls": [
            {"round": item.get("round"), "tool_call_count": item.get("tool_call_count", 0)}
            for item in rounds
        ],
        "tool_results": tool_results,
        "approvals": {
            "confirm_mutations": config.confirm_mutations,
            "confirm_checkpoint": config.confirm_checkpoint,
            "confirm_evidence": config.confirm_evidence,
        },
        "touched_paths": sorted(set(touched_paths)),
        "evidence_ids": evidence_ids,
        "verification": validation,
        "journal_entry_uid": journal_entry_uid,
        "duration_ms": duration_ms,
        "trace": {
            "rounds": rounds,
            "recovery": recovery or {},
            "builder_loop_step": "local_sidecar_agent_run",
        },
    }


def _record_run_trace(project_root: Path, config: AgentConfig, payload: dict[str, Any]) -> dict[str, Any]:
    if not config.write_trace:
        return {"status": "skipped", "result": {"reason": "write_trace=false"}}
    try:
        trace_input = dict(payload)
        trace_input["project_root"] = str(project_root)
        return run_agent_run_trace(trace_input)
    except Exception as exc:  # pragma: no cover - trace failure must not break agent runs
        return {"status": "error", "tool": "agent_run_trace", "input": {}, "result": {"message": str(exc)}}


def _run_agent(arguments: dict[str, Any], project_root: Path) -> dict[str, Any]:
    config = _config(arguments, project_root)
    prompt = str(arguments.get("prompt", "")).strip()
    if not prompt:
        return tool_error(FILE_METADATA["tool_name"], arguments, "prompt is required for action=run")

    runtime_paths = _ensure_runtime(project_root)
    run_started = time.time()
    session_id = config.session_id or f"{_stamp()}_{uuid.uuid4().hex[:8]}"
    mock_responses = arguments.get("mock_ollama_responses")
    if not isinstance(mock_responses, list):
        mock_responses = []
    mock_responses = [str(item) for item in mock_responses]
    mock_failure = str(arguments.get("mock_ollama_failure", "")).strip()

    bootstrap = run_local_agent_bootstrap({
        "project_root": str(project_root),
        "format": "markdown",
        "include_markdown": True,
        "journal_limit": 5,
        "timeout_seconds": min(config.timeout_seconds, 10),
        "include_evidence_shelf": config.use_evidence_shelf,
        "evidence_session_id": session_id,
        "evidence_limit": 12,
    })
    boundary = run_workspace_boundary_audit({"project_root": str(project_root), "max_depth": 2})
    setup = run_project_setup({"project_root": str(project_root), "action": "audit"})

    evidence_shelf = run_session_evidence_store({
        "project_root": str(project_root),
        "action": "shelf",
        "session_id": session_id,
        "limit": 12,
    }) if config.use_evidence_shelf else {"status": "skipped", "result": {"reason": "use_evidence_shelf=false"}}
    evidence_summary = _evidence_shelf_text(evidence_shelf)
    bootstrap_summary = str(bootstrap.get("result", {}).get("rendered", ""))[:3000]
    messages = [
        {"role": "system", "content": _system_prompt(config, bootstrap_summary, evidence_summary)},
        {"role": "user", "content": prompt},
    ]

    touched_paths: list[str] = []
    rounds: list[dict[str, Any]] = []
    final_text = ""
    approval_required = False
    halted_reason = ""

    for round_index in range(config.max_tool_rounds):
        try:
            response = _sanitize_model_text(_model_response(
                config=config,
                messages=messages,
                model=config.planner_model if round_index == 0 else config.response_model,
                mock_responses=mock_responses,
                mock_failure=mock_failure,
                round_index=round_index,
            ))
        except Exception as exc:
            recovery = _recovery_from_exception(exc, config)
            halted_reason = recovery["class"]
            rounds.append({
                "round": round_index + 1,
                "tool_call_count": 0,
                "results": [],
                "response": "",
                "recovery": recovery,
            })
            validation = _validate_touched(project_root, touched_paths)
            evidence_archive = _archive_evidence(
                project_root,
                session_id=session_id,
                prompt=prompt,
                rounds=rounds,
                config=config,
                approval_required=False,
            )
            evidence_ids = _evidence_ids(evidence_archive)
            journal = run_journal_write({
                "project_root": str(project_root),
                "action": "create",
                "title": "Local sidecar agent recovery event",
                "body": (
                    f"Prompt: {prompt}\n\n"
                    f"Recovery: {recovery['class']} - {recovery['message']}\n\n"
                    f"Evidence IDs: {', '.join(evidence_ids) or 'none'}"
                ),
                "kind": "agent-recovery",
                "source": "local_sidecar_agent",
                "author": "local_sidecar_agent",
                "tags": ["local-agent", "sidecar", "recovery", "tranche-12"],
                "status": "blocked",
                "related_path": ".dev-tools/runtime/local_agent",
                "metadata": {
                    "session_id": session_id,
                    "recovery": recovery,
                    "evidence_item_ids": evidence_ids,
                    "evidence_archive_status": evidence_archive.get("status"),
                },
            })
            journal_uid = journal.get("result", {}).get("entry", {}).get("entry_uid", "")
            trace = _record_run_trace(project_root, config, _trace_payload(
                session_id=session_id,
                prompt=prompt,
                config=config,
                status="error",
                recovery=recovery,
                rounds=rounds,
                touched_paths=touched_paths,
                validation=validation,
                evidence_ids=evidence_ids,
                journal_entry_uid=journal_uid,
                duration_ms=round((time.time() - run_started) * 1000),
                summary=f"Recovery event: {recovery['class']}",
            ))
            session = {
                "session_id": session_id,
                "created_at": _now(),
                "config": asdict(config),
                "prompt": prompt,
                "recovery": recovery,
                "evidence_shelf": evidence_shelf,
                "evidence_archive": evidence_archive,
                "rounds": rounds,
                "validation": validation,
                "checkpoint": {"skipped": True, "reason": "model recovery event"},
                "journal": journal,
                "trace": trace,
                "halted_reason": halted_reason,
                "approval_required": False,
            }
            if arguments.get("write_session", True) is not False:
                write_json(runtime_paths["sessions"] / f"{session_id}.json", session)
            _append_jsonl(runtime_paths["action_journal"], {
                "ts": _now(),
                "action": "agent_recovery",
                "session_id": session_id,
                "summary": prompt[:160],
                "halted_reason": halted_reason,
                "recovery_class": recovery["class"],
            })
            return tool_result(
                FILE_METADATA["tool_name"],
                arguments,
                {
                    "session_id": session_id,
                    "project_root": str(project_root),
                    "runtime": _public_runtime(runtime_paths, project_root),
                    "round_count": len(rounds),
                    "touched_paths": sorted(set(touched_paths)),
                    "validation": validation,
                    "recovery": recovery,
                    "evidence_shelf": evidence_shelf.get("result", {}),
                    "evidence_archive": evidence_archive.get("result", evidence_archive),
                    "trace": trace.get("result", trace),
                    "journal_entry_uid": journal_uid,
                    "halted_reason": halted_reason,
                    "approval_required": False,
                    "final_text": "",
                },
                status="error",
            )
        final_text = response
        calls = _parse_tool_calls(response)
        round_results: list[dict[str, Any]] = []
        for call in calls:
            result = _execute_tool_call(
                call,
                config=config,
                project_root=project_root,
                runtime_paths=runtime_paths,
                touched_paths=touched_paths,
            )
            round_results.append(result)
            if result.get("status") == "approval_required":
                approval_required = True
                halted_reason = "approval_required"
                break
        rounds.append({"round": round_index + 1, "tool_call_count": len(calls), "results": round_results, "response": response})
        if approval_required or not calls:
            break
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": _format_tool_results(round_results)})
    else:
        halted_reason = "max_tool_rounds_exhausted"

    validation = _validate_touched(project_root, touched_paths)
    evidence_archive = _archive_evidence(
        project_root,
        session_id=session_id,
        prompt=prompt,
        rounds=rounds,
        config=config,
        approval_required=approval_required,
    )
    checkpoint = _checkpoint(project_root, touched_paths, config, prompt) if not approval_required else {
        "skipped": True,
        "approval_required": True,
        "reason": "turn stopped before checkpoint",
    }
    evidence_payload = evidence_archive.get("result", evidence_archive)
    evidence_ids = _evidence_ids(evidence_archive)
    evidence_status = evidence_archive.get("status", "skipped")
    recovery = {"class": halted_reason, "message": halted_reason, "next_actions": []} if halted_reason else {}

    journal = run_journal_write({
        "project_root": str(project_root),
        "action": "create",
        "title": "Local sidecar agent turn",
        "body": (
            f"Prompt: {prompt}\n\n"
            f"Touched paths: {', '.join(sorted(set(touched_paths))) or 'none'}\n\n"
            f"Evidence archive: {evidence_status}"
            f"{' (' + ', '.join(evidence_ids) + ')' if evidence_ids else ''}\n\n"
            f"Halted: {halted_reason or 'no'}"
        ),
        "kind": "agent-turn",
        "source": "local_sidecar_agent",
        "author": "local_sidecar_agent",
        "tags": ["local-agent", "sidecar", "evidence", "tranche-9", "tranche-11"],
        "status": "active" if not approval_required else "blocked",
        "related_path": ".dev-tools/runtime/local_agent",
        "metadata": {
            "session_id": session_id,
            "halted_reason": halted_reason,
            "evidence_archive_status": evidence_status,
            "evidence_item_ids": evidence_ids,
            "evidence_archive": evidence_payload,
        },
    })
    journal_uid = journal.get("result", {}).get("entry", {}).get("entry_uid", "")
    result_status = "approval_required" if approval_required else "ok"
    trace = _record_run_trace(project_root, config, _trace_payload(
        session_id=session_id,
        prompt=prompt,
        config=config,
        status=result_status,
        recovery=recovery,
        rounds=rounds,
        touched_paths=touched_paths,
        validation=validation,
        evidence_ids=evidence_ids,
        journal_entry_uid=journal_uid,
        duration_ms=round((time.time() - run_started) * 1000),
        summary=f"Local sidecar agent run: {result_status}",
    ))

    session = {
        "session_id": session_id,
        "created_at": _now(),
        "config": asdict(config),
        "prompt": prompt,
        "bootstrap_status": bootstrap.get("status"),
        "boundary_status": boundary.get("status"),
        "setup_status": setup.get("status"),
        "evidence_shelf": evidence_shelf,
        "evidence_archive": evidence_archive,
        "rounds": rounds,
        "validation": validation,
        "checkpoint": checkpoint,
        "journal": journal,
        "trace": trace,
        "halted_reason": halted_reason,
        "approval_required": approval_required,
    }
    if arguments.get("write_session", True) is not False:
        write_json(runtime_paths["sessions"] / f"{session_id}.json", session)
    _append_jsonl(runtime_paths["action_journal"], {
        "ts": _now(),
        "action": "agent_turn",
        "session_id": session_id,
        "summary": prompt[:160],
        "touched_paths": sorted(set(touched_paths)),
        "halted_reason": halted_reason,
    })

    return tool_result(
        FILE_METADATA["tool_name"],
        arguments,
        {
            "session_id": session_id,
            "project_root": str(project_root),
            "runtime": _public_runtime(runtime_paths, project_root),
            "round_count": len(rounds),
            "touched_paths": sorted(set(touched_paths)),
            "validation": validation,
            "evidence_shelf": evidence_shelf.get("result", {}),
            "evidence_archive": evidence_archive.get("result", evidence_archive),
            "trace": trace.get("result", trace),
            "checkpoint": checkpoint,
            "journal_entry_uid": journal_uid,
            "halted_reason": halted_reason,
            "approval_required": approval_required,
            "final_text": final_text,
        },
        status=result_status,
    )


def run(arguments: dict[str, Any]) -> dict[str, Any]:
    action = str(arguments.get("action", "run")).strip().lower()
    if action not in {"status", "models", "run"}:
        return tool_error(FILE_METADATA["tool_name"], arguments, f"unsupported action: {action}")
    try:
        project_root = resolve_project_root(arguments.get("project_root"))
    except Exception as exc:
        return tool_error(FILE_METADATA["tool_name"], arguments, str(exc))
    if not project_root.is_dir():
        return tool_error(FILE_METADATA["tool_name"], arguments, f"Not a directory: {project_root}")

    config = _config(arguments, project_root)
    if action == "status":
        paths = _runtime_paths(project_root)
        return tool_result(FILE_METADATA["tool_name"], arguments, {
            "project_root": str(project_root),
            "runtime": _public_runtime(paths, project_root),
            "runtime_exists": paths["base"].exists(),
            "allowed_tools": config.allowed_tools,
            "config": asdict(config),
        })
    if action == "models":
        return tool_result(FILE_METADATA["tool_name"], arguments, _scan_models(config.ollama_base_url, min(config.timeout_seconds, 30)))
    return _run_agent(arguments, project_root)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
