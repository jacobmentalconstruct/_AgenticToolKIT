"""Teaching sandbox harness for guarded local-agent practice runs."""

from __future__ import annotations

import ast
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.session_evidence_store import sanitize_text


SCHEMA_VERSION = "1.0.0"
DEFAULT_ALLOWED_TOOLS = [
    "directory_scaffold",
    "text_file_reader",
    "text_file_writer",
    "text_file_validator",
    "session_evidence_store",
    "agent_run_trace",
    "journal_write",
]


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    title: str
    summary: str
    expected_files: tuple[str, ...]
    task_card: str


SCENARIOS: dict[str, Scenario] = {
    "static_task_tracker": Scenario(
        scenario_id="static_task_tracker",
        title="Static Task Tracker",
        summary="Build a static HTML/CSS/JS task app with localStorage and task lifecycle controls.",
        expected_files=("index.html", "styles.css", "app.js", "_docs/TASK_CARD.md"),
        task_card=(
            "# Task Card: Static Task Tracker\n\n"
            "Build a tiny static app using only index.html, styles.css, and app.js.\n\n"
            "Success criteria:\n"
            "- A user can add a task.\n"
            "- A user can mark a task complete.\n"
            "- A user can edit or delete a task.\n"
            "- Tasks persist with localStorage.\n"
            "- The UI is usable by opening index.html directly.\n\n"
            "Use only guarded text/scaffold tools. Do not install packages or run shell commands.\n"
        ),
    ),
    "python_notes_cli": Scenario(
        scenario_id="python_notes_cli",
        title="Python Notes CLI",
        summary="Build a stdlib Python notes CLI with add/list/search and JSON persistence.",
        expected_files=("notes.py", "README.md", "_docs/TASK_CARD.md"),
        task_card=(
            "# Task Card: Python Notes CLI\n\n"
            "Build a tiny stdlib-only command line notes app in notes.py.\n\n"
            "Success criteria:\n"
            "- `add` stores a note in a JSON file.\n"
            "- `list` displays saved notes.\n"
            "- `search` filters saved notes by query text.\n"
            "- README.md documents the commands.\n"
            "- notes.py parses as valid Python and uses only the standard library.\n\n"
            "Use only guarded text/scaffold tools. Do not install packages or run shell commands.\n"
        ),
    ),
}


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def harness_root(toolbox_root: str | Path) -> Path:
    return Path(toolbox_root).resolve() / ".dev-tools" / "runtime" / "teaching_sandbox"


def db_path(toolbox_root: str | Path) -> Path:
    return harness_root(toolbox_root) / "teaching_sandbox.sqlite3"


def status(toolbox_root: str | Path) -> dict[str, Any]:
    root = Path(toolbox_root).resolve()
    database = db_path(root)
    if not database.exists():
        return {
            "exists": False,
            "schema_version": "",
            "harness_root": _relative(harness_root(root), root),
            "scenario_count": len(SCENARIOS),
            "run_count": 0,
            "latest_run_id": "",
        }
    with _connect(database) as conn:
        run_count = conn.execute("SELECT COUNT(*) FROM teaching_runs").fetchone()[0]
        latest = conn.execute("SELECT run_uid FROM teaching_runs ORDER BY id DESC LIMIT 1").fetchone()
        schema_version = _meta(conn, "schema_version") or ""
    return {
        "exists": True,
        "schema_version": schema_version,
        "harness_root": _relative(harness_root(root), root),
        "scenario_count": len(SCENARIOS),
        "run_count": run_count,
        "latest_run_id": latest["run_uid"] if latest else "",
    }


def list_scenarios() -> dict[str, Any]:
    return {
        "scenarios": [
            {
                "scenario_id": item.scenario_id,
                "title": item.title,
                "summary": item.summary,
                "expected_files": list(item.expected_files),
            }
            for item in SCENARIOS.values()
        ]
    }


def scenario_plan(payload: dict[str, Any]) -> dict[str, Any]:
    scenario = _scenario(payload)
    return {
        "scenario_id": scenario.scenario_id,
        "title": scenario.title,
        "summary": scenario.summary,
        "task_card": scenario.task_card,
        "expected_files": list(scenario.expected_files),
        "verification_checks": _verification_check_ids(scenario.scenario_id),
        "allowed_tools": list(DEFAULT_ALLOWED_TOOLS),
    }


def create_project(toolbox_root: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(toolbox_root).resolve()
    scenario = _scenario(payload)
    init_store(root)
    project_id = _project_id(scenario.scenario_id, payload.get("project_id"))
    project_root = harness_root(root) / "projects" / project_id
    if project_root.exists():
        raise ValueError(f"sandbox project already exists: {project_id}")
    project_root.mkdir(parents=True)
    docs_root = project_root / "_docs"
    docs_root.mkdir(parents=True)
    (docs_root / "TASK_CARD.md").write_text(scenario.task_card, encoding="utf-8", newline="")
    contract = root / "_docs" / "builder_constraint_contract.md"
    if contract.exists():
        (docs_root / "builder_constraint_contract.md").write_text(
            contract.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="",
        )
    readme = (
        f"# {scenario.title} Sandbox\n\n"
        "This ignored runtime project is a teaching sandbox for the local sidecar agent.\n"
        "The agent should read `_docs/TASK_CARD.md` and use guarded tools only.\n"
    )
    (project_root / "README.md").write_text(readme, encoding="utf-8", newline="")
    run_record = _insert_run(root, scenario.scenario_id, project_id, project_root)
    return {
        "run_id": run_record["run_id"],
        "scenario_id": scenario.scenario_id,
        "project_id": project_id,
        "sandbox_project_root": _relative(project_root, root),
        "task_card_path": _relative(docs_root / "TASK_CARD.md", root),
        "expected_files": list(scenario.expected_files),
    }


def run_agent(toolbox_root: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    from tools.local_sidecar_agent import run as run_local_sidecar_agent

    root = Path(toolbox_root).resolve()
    run_record = _run_record(root, payload)
    scenario = SCENARIOS[run_record["scenario_id"]]
    project_root = root / run_record["sandbox_project_rel"]
    if not project_root.is_dir():
        raise ValueError("sandbox project does not exist; run create_project first")
    session_id = str(payload.get("session_id", f"teach-{run_record['run_id']}")).strip()
    run_mode = str(payload.get("run_mode", "mocked")).strip().lower() or "mocked"
    if run_mode not in {"mocked", "live"}:
        raise ValueError("run_mode must be mocked or live")
    mock_responses = payload.get("mock_ollama_responses")
    if isinstance(mock_responses, list) and mock_responses:
        mock_responses = [str(item) for item in mock_responses]
    elif run_mode == "mocked":
        mock_responses = _mock_responses(scenario.scenario_id)
    else:
        mock_responses = []
    agent_input = {
        "action": "run",
        "project_root": str(project_root),
        "prompt": str(payload.get("prompt", _agent_prompt(scenario))),
        "ollama_base_url": str(payload.get("ollama_base_url", "http://localhost:11434")),
        "planner_model": str(payload.get("planner_model", "qwen2.5-coder:7b")),
        "response_model": str(payload.get("response_model", "qwen3.5:4b")),
        "timeout_seconds": int(payload.get("timeout_seconds", 60)),
        "max_tool_rounds": int(payload.get("max_tool_rounds", 4)),
        "allowed_tools": _string_list(payload.get("allowed_tools")) or list(DEFAULT_ALLOWED_TOOLS),
        "confirm_mutations": True,
        "confirm_checkpoint": bool(payload.get("confirm_checkpoint", False)),
        "checkpoint": bool(payload.get("checkpoint", False)),
        "confirm_evidence": True,
        "session_id": session_id,
        "window_turns": int(payload.get("window_turns", 8)),
        "use_evidence_shelf": bool(payload.get("use_evidence_shelf", True)),
        "write_trace": True,
        "preflight": bool(payload.get("preflight", False)),
    }
    if mock_responses:
        agent_input["mock_ollama_responses"] = mock_responses
    result = run_local_sidecar_agent(agent_input)
    agent_payload = result.get("result", {}) if isinstance(result.get("result"), dict) else {}
    trace_id = str(agent_payload.get("trace", {}).get("run_id", ""))
    evidence_ids = _string_list(agent_payload.get("evidence_archive", {}).get("archived_items"))
    evidence_ids = [str(item.get("item_id")) for item in agent_payload.get("evidence_archive", {}).get("archived_items", []) if isinstance(item, dict) and item.get("item_id")]
    journal_uid = str(agent_payload.get("journal_entry_uid", ""))
    _update_run(
        root,
        run_record["run_id"],
        status=str(result.get("status", "unknown")),
        session_id=session_id,
        trace_ids=[trace_id] if trace_id else [],
        evidence_ids=evidence_ids,
        journal_entry_uid=journal_uid,
        agent_result=result,
    )
    return {
        "run_id": run_record["run_id"],
        "scenario_id": scenario.scenario_id,
        "session_id": session_id,
        "agent_status": result.get("status"),
        "trace_ids": [trace_id] if trace_id else [],
        "evidence_ids": evidence_ids,
        "journal_entry_uid": journal_uid,
        "agent_result": _sanitize_json(result, root),
    }


def verify_project(toolbox_root: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(toolbox_root).resolve()
    run_record = _run_record(root, payload)
    scenario_id = str(payload.get("scenario_id", run_record["scenario_id"]))
    project_root = root / run_record["sandbox_project_rel"]
    checks = _verify_scenario(project_root, scenario_id)
    passed = sum(1 for item in checks if item["status"] == "pass")
    result = {
        "run_id": run_record["run_id"],
        "scenario_id": scenario_id,
        "sandbox_project_root": _relative(project_root, root),
        "passed": passed,
        "failed": len(checks) - passed,
        "score": round((passed / len(checks)) * 100) if checks else 0,
        "checks": checks,
    }
    _update_run(root, run_record["run_id"], verification=result)
    return result


def score_run(toolbox_root: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(toolbox_root).resolve()
    run_record = _run_record(root, payload)
    verification = run_record.get("verification") or verify_project(root, {"run_id": run_record["run_id"]})
    agent_result = run_record.get("agent_result", {})
    agent_ok = 1 if str(agent_result.get("status", "")) == "ok" else 0
    trace_count = len(run_record.get("trace_ids", []))
    evidence_count = len(run_record.get("evidence_ids", []))
    journal_count = 1 if run_record.get("journal_entry_uid") else 0
    verification_score = int(verification.get("score", 0))
    score = min(100, round((verification_score * 0.7) + (agent_ok * 10) + min(trace_count, 1) * 7 + min(evidence_count, 1) * 7 + journal_count * 6))
    scorecard = {
        "run_id": run_record["run_id"],
        "scenario_id": run_record["scenario_id"],
        "score": score,
        "verification_score": verification_score,
        "agent_status": agent_result.get("status", run_record.get("status", "")),
        "trace_ids": run_record.get("trace_ids", []),
        "evidence_ids": run_record.get("evidence_ids", []),
        "journal_entry_uid": run_record.get("journal_entry_uid", ""),
        "passed": score >= 80 and verification.get("failed", 1) == 0,
        "notes": "Score combines scenario verification, agent completion, trace, evidence, and journal capture.",
    }
    _update_run(root, run_record["run_id"], scorecard=scorecard, score=score)
    return scorecard


def run_scenario(toolbox_root: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(toolbox_root).resolve()
    created = create_project(root, payload)
    run_payload = dict(payload)
    run_payload["run_id"] = created["run_id"]
    agent = run_agent(root, run_payload)
    verified = verify_project(root, {"run_id": created["run_id"]})
    scorecard = score_run(root, {"run_id": created["run_id"]})
    return {
        "run_id": created["run_id"],
        "scenario_id": created["scenario_id"],
        "project": created,
        "agent": agent,
        "verification": verified,
        "scorecard": scorecard,
    }


def export_run(toolbox_root: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(toolbox_root).resolve()
    run_record = _run_record(root, payload)
    fmt = str(payload.get("format", "markdown")).lower()
    export_dir = harness_root(root) / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path = export_dir / f"teaching_sandbox_{run_record['run_id']}_{file_stamp()}.json"
        path.write_text(json.dumps(_sanitize_json(run_record, root), indent=2, sort_keys=False), encoding="utf-8")
    else:
        path = export_dir / f"teaching_sandbox_{run_record['run_id']}_{file_stamp()}.md"
        path.write_text(_run_markdown(run_record, root), encoding="utf-8", newline="")
    _update_run(root, run_record["run_id"], export_paths=[_relative(path, root)])
    return {"run_id": run_record["run_id"], "format": fmt, "export_path": _relative(path, root)}


def init_store(toolbox_root: str | Path) -> dict[str, Any]:
    root = Path(toolbox_root).resolve()
    database = db_path(root)
    database.parent.mkdir(parents=True, exist_ok=True)
    with _connect(database) as conn:
        _create_schema(conn, root)
    return status(root)


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _create_schema(conn: sqlite3.Connection, toolbox_root: Path) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS teaching_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS teaching_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_uid TEXT UNIQUE NOT NULL,
            scenario_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            sandbox_project_rel TEXT NOT NULL,
            status TEXT NOT NULL,
            session_id TEXT,
            trace_ids_json TEXT NOT NULL DEFAULT '[]',
            evidence_ids_json TEXT NOT NULL DEFAULT '[]',
            journal_entry_uid TEXT,
            verification_json TEXT NOT NULL DEFAULT '{}',
            scorecard_json TEXT NOT NULL DEFAULT '{}',
            agent_result_json TEXT NOT NULL DEFAULT '{}',
            export_paths_json TEXT NOT NULL DEFAULT '[]',
            score INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_teaching_runs_scenario ON teaching_runs(scenario_id, id);
        """
    )
    timestamp = now_stamp()
    conn.execute("INSERT OR REPLACE INTO teaching_meta(key, value) VALUES ('schema_version', ?)", (SCHEMA_VERSION,))
    conn.execute("INSERT OR REPLACE INTO teaching_meta(key, value) VALUES ('toolbox_root_hint', ?)", (_relative(toolbox_root, toolbox_root),))
    conn.execute("INSERT OR IGNORE INTO teaching_meta(key, value) VALUES ('initialized_at', ?)", (timestamp,))


def _insert_run(toolbox_root: Path, scenario_id: str, project_id: str, project_root: Path) -> dict[str, Any]:
    timestamp = now_stamp()
    database = db_path(toolbox_root)
    with _connect(database) as conn:
        _create_schema(conn, toolbox_root)
        cursor = conn.execute(
            """
            INSERT INTO teaching_runs(
                run_uid, scenario_id, project_id, sandbox_project_rel, status,
                created_at, updated_at
            ) VALUES ('', ?, ?, ?, 'created', ?, ?)
            """,
            (scenario_id, project_id, _relative(project_root, toolbox_root), timestamp, timestamp),
        )
        run_uid = f"TS{int(cursor.lastrowid):06d}"
        conn.execute("UPDATE teaching_runs SET run_uid = ? WHERE id = ?", (run_uid, cursor.lastrowid))
    return {"run_id": run_uid}


def _update_run(toolbox_root: Path, run_id: str, **updates: Any) -> None:
    if not updates:
        return
    database = db_path(toolbox_root)
    assignments: list[str] = []
    params: list[Any] = []
    mapping = {
        "status": "status",
        "session_id": "session_id",
        "journal_entry_uid": "journal_entry_uid",
        "score": "score",
        "trace_ids": "trace_ids_json",
        "evidence_ids": "evidence_ids_json",
        "verification": "verification_json",
        "scorecard": "scorecard_json",
        "agent_result": "agent_result_json",
        "export_paths": "export_paths_json",
    }
    for key, value in updates.items():
        column = mapping.get(key)
        if not column:
            continue
        assignments.append(f"{column} = ?")
        if column.endswith("_json"):
            params.append(json.dumps(value, sort_keys=True, default=str))
        else:
            params.append(value)
    assignments.append("updated_at = ?")
    params.append(now_stamp())
    params.append(run_id)
    with _connect(database) as conn:
        conn.execute(f"UPDATE teaching_runs SET {', '.join(assignments)} WHERE run_uid = ?", params)


def _run_record(toolbox_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    database = db_path(toolbox_root)
    if not database.exists():
        raise ValueError("teaching sandbox store has not been initialized")
    run_id = str(payload.get("run_id", "")).strip()
    with _connect(database) as conn:
        if run_id:
            row = conn.execute("SELECT * FROM teaching_runs WHERE run_uid = ?", (run_id,)).fetchone()
        else:
            scenario_id = str(payload.get("scenario_id", "")).strip()
            if scenario_id:
                row = conn.execute(
                    "SELECT * FROM teaching_runs WHERE scenario_id = ? ORDER BY id DESC LIMIT 1",
                    (scenario_id,),
                ).fetchone()
            else:
                row = conn.execute("SELECT * FROM teaching_runs ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        raise ValueError("teaching sandbox run not found")
    return _display_run(row, toolbox_root)


def _display_run(row: sqlite3.Row, toolbox_root: Path) -> dict[str, Any]:
    return {
        "run_id": row["run_uid"],
        "scenario_id": row["scenario_id"],
        "project_id": row["project_id"],
        "sandbox_project_rel": row["sandbox_project_rel"],
        "sandbox_project_root": sanitize_text(row["sandbox_project_rel"], toolbox_root),
        "status": row["status"],
        "session_id": row["session_id"] or "",
        "trace_ids": _json_value(row["trace_ids_json"], []),
        "evidence_ids": _json_value(row["evidence_ids_json"], []),
        "journal_entry_uid": row["journal_entry_uid"] or "",
        "verification": _json_value(row["verification_json"], {}),
        "scorecard": _json_value(row["scorecard_json"], {}),
        "agent_result": _json_value(row["agent_result_json"], {}),
        "export_paths": _json_value(row["export_paths_json"], []),
        "score": row["score"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _verify_scenario(project_root: Path, scenario_id: str) -> list[dict[str, Any]]:
    if scenario_id == "static_task_tracker":
        return _verify_static_task_tracker(project_root)
    if scenario_id == "python_notes_cli":
        return _verify_python_notes_cli(project_root)
    raise ValueError(f"unknown scenario: {scenario_id}")


def _verify_static_task_tracker(project_root: Path) -> list[dict[str, Any]]:
    checks = _file_checks(project_root, SCENARIOS["static_task_tracker"].expected_files)
    index = _read(project_root / "index.html")
    script = _read(project_root / "app.js")
    styles = _read(project_root / "styles.css")
    checks.extend([
        _check("html-links-css", "styles.css" in index, "index.html links styles.css"),
        _check("html-links-js", "app.js" in index, "index.html links app.js"),
        _check("js-uses-localstorage", "localStorage" in script, "app.js uses localStorage"),
        _check("js-adds-event-listeners", "addEventListener" in script, "app.js registers event listeners"),
        _check("js-has-task-lifecycle", all(term in script.lower() for term in ["delete", "edit", "complete"]), "app.js covers delete/edit/complete"),
        _check("css-nonempty", len(styles.strip()) > 20, "styles.css is non-empty"),
    ])
    return checks


def _verify_python_notes_cli(project_root: Path) -> list[dict[str, Any]]:
    checks = _file_checks(project_root, SCENARIOS["python_notes_cli"].expected_files)
    source = _read(project_root / "notes.py")
    readme = _read(project_root / "README.md")
    try:
        ast.parse(source or "")
        parses = True
    except SyntaxError:
        parses = False
    lowered = source.lower()
    checks.extend([
        _check("python-ast-parse", parses, "notes.py parses as Python"),
        _check("python-uses-argparse", "argparse" in lowered, "notes.py uses argparse"),
        _check("python-uses-json", "json" in lowered, "notes.py uses JSON persistence"),
        _check("python-has-commands", all(term in lowered for term in ["add", "list", "search"]), "notes.py has add/list/search commands"),
        _check("readme-docs-commands", all(term in readme.lower() for term in ["add", "list", "search"]), "README documents add/list/search"),
    ])
    return checks


def _file_checks(project_root: Path, expected_files: tuple[str, ...]) -> list[dict[str, Any]]:
    return [
        _check(f"file:{rel}", (project_root / rel).is_file(), f"{rel} exists")
        for rel in expected_files
    ]


def _check(check_id: str, passed: bool, message: str) -> dict[str, Any]:
    return {"check_id": check_id, "status": "pass" if passed else "fail", "message": message}


def _verification_check_ids(scenario_id: str) -> list[str]:
    temp = Path("__scenario__")
    return [item["check_id"] for item in _verify_scenario(temp, scenario_id)]


def _mock_responses(scenario_id: str) -> list[str]:
    if scenario_id == "static_task_tracker":
        entries = [
            {"type": "file", "path": "index.html", "content": STATIC_INDEX, "overwrite": True},
            {"type": "file", "path": "styles.css", "content": STATIC_CSS, "overwrite": True},
            {"type": "file", "path": "app.js", "content": STATIC_JS, "overwrite": True},
        ]
    elif scenario_id == "python_notes_cli":
        entries = [
            {"type": "file", "path": "notes.py", "content": NOTES_PY, "overwrite": True},
            {"type": "file", "path": "README.md", "content": NOTES_README, "overwrite": True},
        ]
    else:
        raise ValueError(f"unknown scenario: {scenario_id}")
    call = {"tool": "directory_scaffold", "arguments": {"entries": entries, "dry_run": False, "validate_files": True}}
    return [
        "```tool_call\n" + json.dumps(call, sort_keys=True) + "\n```",
        "Created the requested sandbox app and validated the touched files.",
    ]


def _agent_prompt(scenario: Scenario) -> str:
    return (
        "Read _docs/builder_constraint_contract.md and _docs/TASK_CARD.md first. "
        "Then complete the task card using only allowlisted guarded tools. "
        "When done, summarize touched files and verification evidence.\n\n"
        f"{scenario.task_card}"
    )


def _run_markdown(run_record: dict[str, Any], toolbox_root: Path) -> str:
    clean = _sanitize_json(run_record, toolbox_root)
    scorecard = clean.get("scorecard", {})
    verification = clean.get("verification", {})
    lines = [
        "# Teaching Sandbox Run",
        "",
        f"- Run ID: {clean.get('run_id', '')}",
        f"- Scenario: {clean.get('scenario_id', '')}",
        f"- Status: {clean.get('status', '')}",
        f"- Score: {scorecard.get('score', clean.get('score', 0))}",
        f"- Trace IDs: {', '.join(clean.get('trace_ids', [])) or 'none'}",
        f"- Evidence IDs: {', '.join(clean.get('evidence_ids', [])) or 'none'}",
        f"- Journal Entry: {clean.get('journal_entry_uid', '') or 'none'}",
        "",
        "## Verification",
        "",
    ]
    for item in verification.get("checks", []):
        lines.append(f"- [{item.get('status')}] {item.get('check_id')}: {item.get('message')}")
    return "\n".join(lines) + "\n"


def _scenario(payload: dict[str, Any]) -> Scenario:
    scenario_id = str(payload.get("scenario_id", "static_task_tracker")).strip() or "static_task_tracker"
    if scenario_id not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario_id}")
    return SCENARIOS[scenario_id]


def _project_id(scenario_id: str, requested: Any) -> str:
    value = str(requested or "").strip()
    if value:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in value)
        return safe[:80]
    return f"{scenario_id}_{file_stamp()}"


def _meta(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM teaching_meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def _json_value(text: str, fallback: Any) -> Any:
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return fallback


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return sanitize_text(str(path), root)


def _sanitize_json(value: Any, toolbox_root: Path) -> Any:
    if isinstance(value, str):
        return sanitize_text(value, toolbox_root)
    if isinstance(value, list):
        return [_sanitize_json(item, toolbox_root) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_json(item, toolbox_root) for key, item in value.items()}
    return value


STATIC_INDEX = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Task Tracker</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <main>
    <h1>Task Tracker</h1>
    <form id="task-form">
      <input id="task-input" aria-label="Task" placeholder="New task">
      <button type="submit">Add</button>
    </form>
    <ul id="task-list"></ul>
  </main>
  <script src="app.js"></script>
</body>
</html>
"""


STATIC_CSS = """body {
  font-family: Arial, sans-serif;
  margin: 2rem;
  background: #f7f7f2;
  color: #17202a;
}
main {
  max-width: 42rem;
}
li {
  display: flex;
  gap: .5rem;
  align-items: center;
  margin: .5rem 0;
}
.complete span {
  text-decoration: line-through;
  color: #607080;
}
"""


STATIC_JS = """const form = document.querySelector('#task-form');
const input = document.querySelector('#task-input');
const list = document.querySelector('#task-list');
let tasks = JSON.parse(localStorage.getItem('tasks') || '[]');

function save() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

function render() {
  list.innerHTML = '';
  tasks.forEach((task, index) => {
    const item = document.createElement('li');
    item.className = task.complete ? 'complete' : '';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = task.complete;
    checkbox.addEventListener('change', () => {
      task.complete = checkbox.checked;
      save();
      render();
    });
    const label = document.createElement('span');
    label.textContent = task.text;
    const edit = document.createElement('button');
    edit.textContent = 'Edit';
    edit.addEventListener('click', () => {
      const next = prompt('Edit task', task.text);
      if (next) {
        task.text = next;
        save();
        render();
      }
    });
    const del = document.createElement('button');
    del.textContent = 'Delete';
    del.addEventListener('click', () => {
      tasks.splice(index, 1);
      save();
      render();
    });
    item.append(checkbox, label, edit, del);
    list.appendChild(item);
  });
}

form.addEventListener('submit', event => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  tasks.push({ text, complete: false });
  input.value = '';
  save();
  render();
});

render();
"""


NOTES_PY = """import argparse
import json
from pathlib import Path

DATA_FILE = Path('notes.json')


def load_notes():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding='utf-8'))


def save_notes(notes):
    DATA_FILE.write_text(json.dumps(notes, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Tiny notes CLI')
    sub = parser.add_subparsers(dest='command', required=True)
    add = sub.add_parser('add')
    add.add_argument('text')
    sub.add_parser('list')
    search = sub.add_parser('search')
    search.add_argument('query')
    args = parser.parse_args()
    notes = load_notes()
    if args.command == 'add':
        notes.append({'text': args.text})
        save_notes(notes)
        print('added')
    elif args.command == 'list':
        for index, note in enumerate(notes, start=1):
            print(f'{index}. {note["text"]}')
    elif args.command == 'search':
        for note in notes:
            if args.query.lower() in note['text'].lower():
                print(note['text'])


if __name__ == '__main__':
    main()
"""


NOTES_README = """# Python Notes CLI

Use `python notes.py add "text"` to add a note.
Use `python notes.py list` to list notes.
Use `python notes.py search query` to search notes.
"""
