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
from tools.local_agent_bootstrap import run as run_local_agent_bootstrap
from tools.project_setup import run as run_project_setup
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
]
MUTATING_TOOLS = {"text_file_writer", "directory_scaffold", "journal_write"}
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


TOOL_REGISTRY: dict[str, tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "text_file_reader": (TEXT_FILE_READER_METADATA, run_text_file_reader),
    "text_file_writer": (TEXT_FILE_WRITER_METADATA, run_text_file_writer),
    "directory_scaffold": (DIRECTORY_SCAFFOLD_METADATA, run_directory_scaffold),
    "text_file_validator": (TEXT_FILE_VALIDATOR_METADATA, run_text_file_validator),
    "git_private_workspace": (GIT_PRIVATE_METADATA, run_git_private_workspace),
    "journal_write": (JOURNAL_WRITE_METADATA, run_journal_write),
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


def _system_prompt(config: AgentConfig, bootstrap_summary: str) -> str:
    return (
        "You are a local sidecar agent. Use only the listed toolbox tools.\n"
        "Never claim a file was created, modified, or validated unless a tool result proves it.\n"
        "Return tool calls as fenced JSON blocks exactly like:\n"
        "```tool_call\n{\"tool\":\"text_file_reader\",\"arguments\":{\"path\":\"README.md\"}}\n```\n"
        "Do not use raw shell, PowerShell, cmd, bash, cat, echo, or arbitrary commands.\n"
        "All paths are relative to the project root; the runtime injects project_root.\n\n"
        f"Project root: {config.project_root}\n"
        f"Allowed tools:\n{_tool_catalog_text(config.allowed_tools)}\n\n"
        f"Bootstrap summary:\n{bootstrap_summary[:3000]}"
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
    return tool_name in MUTATING_TOOLS


def _inject_confirm(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    updated = dict(args)
    if tool_name in {"text_file_writer", "directory_scaffold", "git_private_workspace"}:
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
    round_index: int,
) -> str:
    if mock_responses:
        if round_index < len(mock_responses):
            return mock_responses[round_index]
        return "No further tool calls."
    return _ollama_chat(config, messages, model)


def _run_agent(arguments: dict[str, Any], project_root: Path) -> dict[str, Any]:
    config = _config(arguments, project_root)
    prompt = str(arguments.get("prompt", "")).strip()
    if not prompt:
        return tool_error(FILE_METADATA["tool_name"], arguments, "prompt is required for action=run")

    runtime_paths = _ensure_runtime(project_root)
    session_id = f"{_stamp()}_{uuid.uuid4().hex[:8]}"
    mock_responses = arguments.get("mock_ollama_responses")
    if not isinstance(mock_responses, list):
        mock_responses = []
    mock_responses = [str(item) for item in mock_responses]

    bootstrap = run_local_agent_bootstrap({
        "project_root": str(project_root),
        "format": "markdown",
        "include_markdown": True,
        "journal_limit": 5,
        "timeout_seconds": min(config.timeout_seconds, 10),
    })
    boundary = run_workspace_boundary_audit({"project_root": str(project_root), "max_depth": 2})
    setup = run_project_setup({"project_root": str(project_root), "action": "audit"})

    bootstrap_summary = str(bootstrap.get("result", {}).get("rendered", ""))[:3000]
    messages = [
        {"role": "system", "content": _system_prompt(config, bootstrap_summary)},
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
                round_index=round_index,
            ))
        except Exception as exc:
            return tool_error(FILE_METADATA["tool_name"], arguments, f"Ollama request failed: {exc}")
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
    checkpoint = _checkpoint(project_root, touched_paths, config, prompt) if not approval_required else {
        "skipped": True,
        "approval_required": True,
        "reason": "turn stopped before checkpoint",
    }

    journal = run_journal_write({
        "project_root": str(project_root),
        "action": "create",
        "title": "Local sidecar agent turn",
        "body": f"Prompt: {prompt}\n\nTouched paths: {', '.join(sorted(set(touched_paths))) or 'none'}\n\nHalted: {halted_reason or 'no'}",
        "kind": "agent-turn",
        "source": "local_sidecar_agent",
        "author": "local_sidecar_agent",
        "tags": ["local-agent", "sidecar", "tranche-9"],
        "status": "active" if not approval_required else "blocked",
        "related_path": ".dev-tools/runtime/local_agent",
        "metadata": {"session_id": session_id, "halted_reason": halted_reason},
    })

    session = {
        "session_id": session_id,
        "created_at": _now(),
        "config": asdict(config),
        "prompt": prompt,
        "bootstrap_status": bootstrap.get("status"),
        "boundary_status": boundary.get("status"),
        "setup_status": setup.get("status"),
        "rounds": rounds,
        "validation": validation,
        "checkpoint": checkpoint,
        "journal": journal,
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

    result_status = "approval_required" if approval_required else "ok"
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
            "checkpoint": checkpoint,
            "journal_entry_uid": journal.get("result", {}).get("entry", {}).get("entry_uid"),
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
