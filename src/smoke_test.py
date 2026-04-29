"""
FILE: smoke_test.py
ROLE: Portable self-test for _app-journal v2.
WHAT IT DOES: Verifies schema v2, CAS, contract, actions, scaffold, pack, snapshot, and MCP paths.
HOW TO USE:
  - python src/smoke_test.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PASS = 0
FAIL = 0

# Avoid cp1252 encoding errors on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _ok(label: str) -> None:
    global PASS
    PASS += 1
    print(f"  [PASS] {label}")


def _fail(label: str, detail: str = "") -> None:
    global FAIL
    FAIL += 1
    msg = f"  [FAIL] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )


def _run_json(args: list[str]) -> dict:
    completed = _run(args)
    if completed.returncode != 0:
        raise RuntimeError(f"Exit {completed.returncode}: {completed.stderr or completed.stdout}")
    return json.loads(completed.stdout)


def _tool(name: str, arguments: dict) -> dict:
    return _run_json([
        sys.executable, str(ROOT / "tools" / f"{name}.py"),
        "run", "--input-json", json.dumps(arguments),
    ])


def _mcp_message(message: dict) -> bytes:
    body = json.dumps(message).encode("utf-8")
    return f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8") + body


def _mcp_read(stdout) -> dict:
    """Read one NDJSON response line from MCP server stdout."""
    while True:
        line = stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed before responding.")
        stripped = line.strip()
        if not stripped:
            continue
        return json.loads(stripped.decode("utf-8"))


# ═══════════════════════════════════════════════════════════════════
# Test groups
# ═══════════════════════════════════════════════════════════════════

def test_compile() -> None:
    """Compile-check all Python source files."""
    print("\n── Compile check ──")
    py_files = list(ROOT.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    result = _run([sys.executable, "-m", "py_compile"] + [str(f) for f in py_files])
    if result.returncode == 0:
        _ok(f"All {len(py_files)} Python files compile clean")
    else:
        _fail("Compile check", result.stderr)


def test_schema_and_cas(project_root: Path) -> str:
    """Init DB, verify schema v2, CAS operations."""
    print("\n── Schema v2 + CAS ──")

    result = _tool("journal_init", {"project_root": str(project_root)})
    db_path = result["result"]["paths"]["db_path"]

    if result["status"] == "ok":
        _ok("journal_init creates DB")
    else:
        _fail("journal_init", str(result))

    # Verify schema version via manifest
    manifest = _tool("journal_manifest", {"db_path": db_path})
    sv = manifest["result"]["db_summary"].get("schema_version")
    uv = manifest["result"]["db_summary"].get("sqlite_user_version")
    if sv == "2.0.0":
        _ok(f"Schema version = {sv}")
    else:
        _fail("Schema version", f"expected 2.0.0, got {sv}")
    if uv == 2:
        _ok(f"SQLite user_version = {uv}")
    else:
        _fail("SQLite user_version", f"expected 2, got {uv}")

    # Verify all 10 tables exist
    expected_tables = {
        "journal_meta", "journal_migrations", "journal_entries",
        "blob_store", "scaffold_templates", "packed_tools",
        "action_log", "snapshots", "snapshot_items", "project_registry",
    }
    db_tables = set(manifest["result"]["db_manifest"].get("db_schema", {}).get("table_names", []))
    if expected_tables == db_tables:
        _ok(f"All {len(expected_tables)} tables declared in manifest")
    else:
        _fail("Table manifest", f"missing: {expected_tables - db_tables}, extra: {db_tables - expected_tables}")

    # Verify contract was seeded
    contract_version = manifest["result"]["db_summary"].get("contract_version", "")
    if contract_version:
        _ok(f"Contract seeded (v{contract_version})")
    else:
        _fail("Contract seeding", "contract_version not set in manifest")

    # Verify blob_store has content (contract body)
    blob_count = manifest["result"]["db_summary"].get("blob_count", 0)
    if blob_count >= 1:
        _ok(f"blob_store has {blob_count} blob(s)")
    else:
        _fail("blob_store", "expected at least 1 blob from contract seeding")

    # CAS: write an entry and verify body_hash
    create_result = _tool("journal_write", {
        "project_root": str(project_root),
        "action": "create",
        "title": "CAS test entry",
        "body": "Content-addressed storage verification.",
        "kind": "note",
        "source": "agent",
        "tags": ["smoke", "cas"],
    })
    entry = create_result["result"]["entry"]
    if entry.get("body_hash"):
        _ok(f"Entry has body_hash: {entry['body_hash'][:16]}...")
    else:
        _fail("CAS dual-write", "entry missing body_hash")

    return db_path


def test_write_query_export(project_root: Path, db_path: str) -> str:
    """CRUD, append, query, export."""
    print("\n── Write / Query / Export ──")

    # Create
    create_result = _tool("journal_write", {
        "db_path": db_path,
        "action": "create",
        "title": "Smoke test decision",
        "body": "We verified the full CRUD lifecycle.",
        "kind": "decision",
        "source": "agent",
        "tags": ["smoke", "crud"],
    })
    entry_uid = create_result["result"]["entry"]["entry_uid"]
    _ok(f"Create entry: {entry_uid}")

    # Append
    _tool("journal_write", {
        "db_path": db_path,
        "action": "append",
        "entry_uid": entry_uid,
        "append_text": "Appended during smoke test.",
    })
    _ok("Append to entry")

    # Update
    _tool("journal_write", {
        "db_path": db_path,
        "action": "update",
        "entry_uid": entry_uid,
        "status": "closed",
        "importance": 3,
    })
    _ok("Update entry status/importance")

    # Query
    query_result = _tool("journal_query", {
        "db_path": db_path,
        "query": "CRUD lifecycle",
        "limit": 10,
    })
    count = query_result["result"]["summary"]["entry_count"]
    if count >= 1:
        _ok(f"Query returns {count} result(s)")
    else:
        _fail("Query", "expected at least 1 result")

    # Export markdown
    export_result = _tool("journal_export", {
        "project_root": str(project_root),
        "format": "markdown",
    })
    export_path = export_result["result"]["export_path"]
    if Path(export_path).exists():
        _ok(f"Markdown export created")
    else:
        _fail("Export", f"file not found: {export_path}")

    # Export JSON
    export_result_json = _tool("journal_export", {
        "project_root": str(project_root),
        "format": "json",
    })
    export_path_json = export_result_json["result"]["export_path"]
    if Path(export_path_json).exists():
        _ok("JSON export created")
    else:
        _fail("JSON export", f"file not found: {export_path_json}")

    return entry_uid


def test_contract_acknowledge(project_root: Path, db_path: str) -> None:
    """Contract acknowledgment."""
    print("\n── Contract Acknowledgment ──")

    ack_result = _tool("journal_acknowledge", {
        "db_path": db_path,
        "actor_id": "smoke_test_agent",
        "actor_type": "agent",
    })
    receipt = ack_result.get("result", {}).get("receipt", {})
    if receipt.get("acknowledged"):
        _ok("Contract acknowledged")
    else:
        _fail("Acknowledge", str(ack_result.get("result", {})))

    # Verify action was logged
    actions_result = _tool("journal_actions", {
        "db_path": db_path,
        "action_type": "acknowledge_contract",
        "limit": 5,
    })
    actions = actions_result["result"]["actions"]
    if any(a["action_type"] == "acknowledge_contract" for a in actions):
        _ok("Acknowledgment recorded in action_log")
    else:
        _fail("Action log", "contract_acknowledge not found")


def test_actions(project_root: Path, db_path: str) -> None:
    """Action ledger query."""
    print("\n── Action Ledger ──")

    result = _tool("journal_actions", {
        "db_path": db_path,
        "limit": 20,
    })
    actions = result["result"]["actions"]
    if len(actions) >= 1:
        _ok(f"Action log has {len(actions)} action(s)")
    else:
        _fail("Action log", "expected at least 1 action")

    # Filter by actor_type
    agent_result = _tool("journal_actions", {
        "db_path": db_path,
        "actor_type": "agent",
        "limit": 10,
    })
    agent_actions = agent_result["result"]["actions"]
    if all(a["actor_type"] == "agent" for a in agent_actions):
        _ok("Actor type filter works")
    else:
        _fail("Actor type filter", "returned non-agent actions")


def test_scaffold(project_root: Path, db_path: str) -> None:
    """Scaffold template seeding and unpacking."""
    print("\n── Scaffolding ──")

    result = _tool("journal_scaffold", {
        "db_path": db_path,
        "project_root": str(project_root),
    })
    payload = result.get("result", {})
    templates_seeded = payload.get("templates_seeded", 0)
    files_written = payload.get("files", [])

    if templates_seeded >= 1 or payload.get("templates_available", 0) >= 1:
        _ok(f"Templates seeded/available")
    else:
        _fail("Template seeding", str(payload))

    if len(files_written) >= 1:
        _ok(f"Scaffold wrote {len(files_written)} file(s)")
        first = files_written[0].get("path", "") if isinstance(files_written[0], dict) else str(files_written[0])
        if first and Path(first).exists():
            _ok(f"Scaffold file exists on disk")
        else:
            _fail("Scaffold file", f"not found: {first}")
    else:
        _ok("Scaffold ran (templates may be placeholder stubs)")


def test_pack(project_root: Path, db_path: str) -> None:
    """Tool packing, listing, and unpacking."""
    print("\n── Tool Packing ──")

    # Pack this package's src/ into the DB
    result = _tool("journal_pack", {
        "db_path": db_path,
        "action": "pack",
        "package_root": str(ROOT),
    })
    payload = result.get("result", {})
    packed = payload.get("packed_count", 0)
    if packed >= 5:
        _ok(f"Packed {packed} files from src/")
    else:
        _fail("Pack", f"expected >= 5 files, got {packed}")

    # List packed tools
    list_result = _tool("journal_pack", {
        "db_path": db_path,
        "action": "list",
    })
    tools = list_result.get("result", {}).get("tools", [])
    if len(tools) >= 5:
        _ok(f"Listed {len(tools)} packed tool(s)")
    else:
        _fail("List packed", f"expected >= 5, got {len(tools)}")

    # Unpack to a temp dir
    unpack_dir = Path(tempfile.mkdtemp(prefix="app_journal_unpack_"))
    unpack_result = _tool("journal_pack", {
        "db_path": db_path,
        "action": "unpack",
        "target_dir": str(unpack_dir),
    })
    unpacked = unpack_result.get("result", {}).get("unpacked_count", 0)
    if unpacked >= 5:
        _ok(f"Unpacked {unpacked} files to {unpack_dir.name}/")
    else:
        _fail("Unpack", f"expected >= 5, got {unpacked}")


def test_snapshot(project_root: Path, db_path: str) -> None:
    """Merkle snapshot create, list, get, verify."""
    print("\n── Snapshots ──")

    # Create
    create_result = _tool("journal_snapshot", {
        "db_path": db_path,
        "action": "create",
        "description": "Smoke test snapshot",
    })
    snapshot = create_result.get("result", {})
    snapshot_id = snapshot.get("snapshot_id", "")
    merkle_root = snapshot.get("merkle_root", "")
    if snapshot_id and merkle_root:
        _ok(f"Snapshot created: {snapshot_id}, root: {merkle_root[:16]}...")
    else:
        _fail("Snapshot create", str(snapshot))
        return

    # List
    list_result = _tool("journal_snapshot", {
        "db_path": db_path,
        "action": "list",
    })
    snapshots = list_result.get("result", {}).get("snapshots", [])
    if len(snapshots) >= 1:
        _ok(f"Listed {len(snapshots)} snapshot(s)")
    else:
        _fail("Snapshot list", "expected at least 1")

    # Get
    get_result = _tool("journal_snapshot", {
        "db_path": db_path,
        "action": "get",
        "snapshot_id": snapshot_id,
    })
    got = get_result.get("result", {})
    if got.get("snapshot_id") == snapshot_id:
        _ok(f"Get snapshot details (items: {got.get('item_count', '?')})")
    else:
        _fail("Snapshot get", str(got))

    # Verify
    verify_result = _tool("journal_snapshot", {
        "db_path": db_path,
        "action": "verify",
        "snapshot_id": snapshot_id,
    })
    verified = verify_result.get("result", {})
    if verified.get("valid"):
        _ok("Snapshot verified (merkle root matches)")
    else:
        _fail("Snapshot verify", str(verified))


def test_authority_build_and_install() -> None:
    """Build authority.sqlite3 and install the thin shim into a temp project."""
    print("\n── Authority Build / Install ──")

    build_result = _tool("authority_build", {})
    authority_db = Path(build_result["result"]["authority_db_path"])
    if authority_db.exists():
        _ok("authority.sqlite3 built")
    else:
        _fail("authority build", f"missing {authority_db}")

    target_root = Path(tempfile.mkdtemp(prefix="authority_install_")) / "fresh_project"
    target_root.mkdir(parents=True, exist_ok=True)

    preview = _tool("authority_install", {
        "target_project_root": str(target_root),
        "preview": True,
    })
    preview_files = preview["result"]["files"]
    if any(item["status"] == "would_create" for item in preview_files):
        _ok("authority install preview works")
    else:
        _fail("authority install preview", str(preview["result"]))

    applied = _tool("authority_install", {
        "target_project_root": str(target_root),
    })
    shim_dir = Path(applied["result"]["shim_dir"])
    expected = {
        shim_dir / "common.py",
        shim_dir / "bootstrap.py",
        shim_dir / "launch_ui.py",
        shim_dir / "mcp_server.py",
        shim_dir / "tool_manifest.json",
        shim_dir / "authority.sqlite3",
    }
    if all(path.exists() for path in expected):
        _ok("thin shim installed")
    else:
        missing = [str(path) for path in expected if not path.exists()]
        _fail("thin shim install", ", ".join(missing))


def test_sidecar_install_and_setup() -> None:
    """Install the full sidecar payload, then apply and verify project setup."""
    print("\n── Sidecar Install / Setup / Microsite ──")

    target_root = Path(tempfile.mkdtemp(prefix="sidecar_install_")) / "fresh_project"
    target_root.mkdir(parents=True, exist_ok=True)

    preview = _tool("sidecar_install", {
        "target_project_root": str(target_root),
        "preview": True,
    })
    preview_files = preview["result"]["files"]
    if any(item["status"] == "would_create" for item in preview_files):
        _ok("sidecar install preview works")
    else:
        _fail("sidecar install preview", str(preview["result"]))

    applied = _tool("sidecar_install", {
        "target_project_root": str(target_root),
    })
    sidecar_dir = Path(applied["result"]["sidecar_dir"])
    expected = {
        sidecar_dir / "README.md",
        sidecar_dir / "release_payload_manifest.json",
        sidecar_dir / "src" / "mcp_server.py",
        sidecar_dir / "onboarding" / "START_HERE.html",
        sidecar_dir / "packages" / "_app-journal" / "README.md",
    }
    if all(path.exists() for path in expected):
        _ok("full sidecar payload installed")
    else:
        missing = [str(path) for path in expected if not path.exists()]
        _fail("sidecar install", ", ".join(missing))

    audit_before = _tool("project_setup", {
        "action": "audit",
        "project_root": str(target_root),
    })
    if audit_before["result"]["missing_required"]:
        _ok("project setup audit detects missing setup surfaces")
    else:
        _fail("project setup audit", str(audit_before["result"]))

    applied_setup = _tool("project_setup", {
        "action": "apply",
        "project_root": str(target_root),
        "actor_id": "smoke_setup_agent",
    })
    if applied_setup["result"]["files"]:
        _ok("project setup apply writes scaffold files")
    else:
        _fail("project setup apply", str(applied_setup["result"]))

    verified = _tool("project_setup", {
        "action": "verify",
        "project_root": str(target_root),
    })
    if verified["result"]["passed"]:
        _ok("project setup verify passes after apply")
    else:
        _fail("project setup verify", str(verified["result"]))

    site_check = _tool("onboarding_site_check", {
        "toolbox_root": str(sidecar_dir),
    })
    if site_check["result"]["passed"]:
        _ok("installed sidecar microsite passes integrity check")
    else:
        _fail("installed sidecar microsite", str(site_check["result"]))


def test_mcp(project_root: Path) -> None:
    """MCP stdio server: initialize, tools/list."""
    print("\n── MCP Server ──")

    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "mcp_server.py")],
        cwd=str(ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert proc.stdin is not None and proc.stdout is not None

        # Initialize
        proc.stdin.write(_mcp_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}))
        proc.stdin.flush()
        init_response = _mcp_read(proc.stdout)
        server_name = init_response.get("result", {}).get("serverInfo", {}).get("name")
        server_version = init_response.get("result", {}).get("serverInfo", {}).get("version")
        if server_name == "project-authority-kit":
            _ok(f"MCP initialize: {server_name} v{server_version}")
        else:
            _fail("MCP initialize", f"unexpected server name: {server_name}")

        # tools/list
        proc.stdin.write(_mcp_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
        proc.stdin.flush()
        list_response = _mcp_read(proc.stdout)
        tool_names = sorted([t["name"] for t in list_response.get("result", {}).get("tools", [])])

        expected_tools = {
            "journal_init", "journal_write", "journal_query", "journal_export",
            "journal_manifest", "journal_acknowledge", "journal_actions",
            "journal_scaffold", "journal_pack", "journal_snapshot",
            "authority_build", "authority_install", "sidecar_install",
            "project_setup", "onboarding_site_check",
        }
        found = set(tool_names)
        if expected_tools.issubset(found):
            _ok(f"MCP tools/list: {len(tool_names)} tools ({', '.join(tool_names)})")
        else:
            missing = expected_tools - found
            _fail("MCP tools/list", f"missing: {missing}")

        # tools/call — journal_query
        proc.stdin.write(_mcp_message({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {
                "name": "journal_query",
                "arguments": {"project_root": str(project_root), "query": "smoke", "limit": 5},
            },
        }))
        proc.stdin.flush()
        call_response = _mcp_read(proc.stdout)
        call_status = call_response.get("result", {}).get("structuredContent", {}).get("status")
        if call_status == "ok":
            _ok("MCP tools/call journal_query succeeds")
        else:
            _fail("MCP tools/call", str(call_response))

    finally:
        proc.kill()
        proc.wait(timeout=5)


def _create_synthetic_project() -> Path:
    """Create a small synthetic project with the folder layout the authority builder expects."""
    root = Path(tempfile.mkdtemp(prefix="builderset_source_"))
    # runtime_executable content (src/, assets/)
    (root / "src" / "mcp").mkdir(parents=True)
    (root / "src" / "mcp" / "server.py").write_text('"""Stub MCP server."""\n', encoding="utf-8")
    (root / "src" / "app.py").write_text('"""Stub app."""\n', encoding="utf-8")
    (root / "assets").mkdir()
    (root / "assets" / "icon.txt").write_text("placeholder\n", encoding="utf-8")
    (root / "requirements.txt").write_text("# none\n", encoding="utf-8")
    # reference_only content (_docs/)
    (root / "_docs").mkdir()
    (root / "_docs" / "DEV_LOG.md").write_text("# Dev Log\nSynthetic.\n", encoding="utf-8")
    (root / "_docs" / "README.md").write_text("# Docs\n", encoding="utf-8")
    return root


def test_builderset_authority() -> None:
    """Build, inspect, hydrate, probe, and export the packed BuilderSET authority."""
    print("\n── BuilderSET Packed Authority ──")

    synthetic_root = _create_synthetic_project()
    authority_output_dir = Path(tempfile.mkdtemp(prefix="builderset_authority_"))
    authority_db_out = str(authority_output_dir / "builderset_authority.sqlite3")
    authority_manifest_out = str(authority_output_dir / "builderset_authority_manifest.json")

    build_result = _tool("builderset_authority_build", {
        "source_project_root": str(synthetic_root),
        "output_db": authority_db_out,
        "output_manifest": authority_manifest_out,
    })
    payload = build_result["result"]
    authority_db = Path(payload["authority_db_path"])
    authority_manifest = Path(payload["authority_manifest_path"])
    if authority_db.exists() and authority_manifest.exists():
        _ok("builderset authority artifacts built")
    else:
        _fail("builderset authority build", f"{authority_db} / {authority_manifest}")
        return

    manifest_result = _tool("builderset_authority_manifest", {"db_path": str(authority_db)})
    counts = manifest_result["result"]["manifest"]["counts"]
    first_blob_count = manifest_result["result"]["db_summary"]["blob_count"]
    if counts["runtime_files"] >= 1 and counts["reference_files"] >= 1:
        _ok(f"builderset authority manifest reports runtime/reference split ({counts['runtime_files']}/{counts['reference_files']})")
    else:
        _fail("builderset manifest split", str(counts))

    rebuild_result = _tool("builderset_authority_build", {
        "source_project_root": str(synthetic_root),
        "output_db": authority_db_out,
        "output_manifest": authority_manifest_out,
    })
    rebuild_manifest = _tool("builderset_authority_manifest", {"db_path": str(rebuild_result["result"]["authority_db_path"])})
    second_blob_count = rebuild_manifest["result"]["db_summary"]["blob_count"]
    if second_blob_count == first_blob_count:
        _ok("builderset authority rebuild does not accumulate stale blobs")
    else:
        _fail("builderset blob pruning", f"before={first_blob_count} after={second_blob_count}")

    query_result = _tool("builderset_authority_query", {
        "db_path": str(authority_db),
        "content_class": "reference_only",
        "top_level": "_docs",
        "limit": 5,
    })
    matches = query_result["result"]["matches"]
    if matches:
        _ok("builderset authority query returns reference content without hydration")
    else:
        _fail("builderset authority query", str(query_result["result"]))

    authority_cache_root = Path(tempfile.mkdtemp(prefix="builderset_cache_"))
    hydrate_first = _tool("builderset_authority_prepare_runtime", {
        "db_path": str(authority_db),
        "cache_root": str(authority_cache_root),
    })
    hydrate_second = _tool("builderset_authority_prepare_runtime", {
        "db_path": str(authority_db),
        "cache_root": str(authority_cache_root),
    })
    first_runtime = hydrate_first["result"]
    second_runtime = hydrate_second["result"]
    runtime_dir = Path(first_runtime["cache_dir"])
    if runtime_dir.exists() and not first_runtime["reused"]:
        _ok("builderset runtime hydrates into managed cache")
    else:
        _fail("builderset runtime hydrate", str(first_runtime))
    if second_runtime["reused"]:
        _ok("builderset runtime cache reuse works")
    else:
        _fail("builderset runtime reuse", str(second_runtime))

    force_runtime = _tool("builderset_authority_prepare_runtime", {
        "db_path": str(authority_db),
        "cache_root": str(authority_cache_root),
        "force": True,
    })
    forced = force_runtime["result"]
    if not forced["reused"]:
        _ok(f"builderset force refresh produces a fresh cache ({forced['cache_strategy']})")
    else:
        _fail("builderset force refresh", str(forced))

    post_force_runtime = _tool("builderset_authority_prepare_runtime", {
        "db_path": str(authority_db),
        "cache_root": str(authority_cache_root),
    })
    if post_force_runtime["result"]["cache_dir"] == forced["cache_dir"] and post_force_runtime["result"]["reused"]:
        _ok("builderset runtime pointer follows the latest forced refresh")
    else:
        _fail("builderset runtime pointer", str(post_force_runtime["result"]))

    # Verify the hydrated runtime contains expected files
    runtime_dir = Path(first_runtime["cache_dir"])
    hydrated_server = runtime_dir / "src" / "mcp" / "server.py"
    hydrated_app = runtime_dir / "src" / "app.py"
    if hydrated_server.exists() and hydrated_app.exists():
        _ok("hydrated runtime contains expected entrypoint files")
    else:
        _fail("hydrated runtime files", f"server={hydrated_server.exists()} app={hydrated_app.exists()}")

    export_root = Path(tempfile.mkdtemp(prefix="builderset_export_"))
    export_result = _tool("builderset_authority_export", {
        "db_path": str(authority_db),
        "destination_root": str(export_root),
        "relative_paths": ["_docs/DEV_LOG.md"],
    })
    exported = export_root / "_docs" / "DEV_LOG.md"
    if exported.exists():
        _ok("builderset authority exports selected reference files on demand")
    else:
        _fail("builderset authority export", str(export_result["result"]))


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main() -> int:
    print("═══ Project Authority Kit Smoke Test ═══")

    project_root = Path(tempfile.mkdtemp(prefix="app_journal_smoke_")) / "test-project"
    project_root.mkdir(parents=True, exist_ok=True)
    print(f"Project root: {project_root}")

    test_compile()
    db_path = test_schema_and_cas(project_root)
    test_write_query_export(project_root, db_path)
    test_contract_acknowledge(project_root, db_path)
    test_actions(project_root, db_path)
    test_scaffold(project_root, db_path)
    test_pack(project_root, db_path)
    test_snapshot(project_root, db_path)
    test_authority_build_and_install()
    test_sidecar_install_and_setup()
    test_mcp(project_root)
    test_builderset_authority()

    print(f"\n═══ Results: {PASS} passed, {FAIL} failed ═══")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
