"""
FILE: mcp_server.py
ROLE: MCP stdio server for _app-journal v2.
WHAT IT DOES: Exposes all journal tools through MCP using the same run(arguments) functions.
HOW TO USE:
  - Start: python src/mcp_server.py
  - Connect as a stdio MCP server from an MCP-capable client.
TOOLS:
  - journal_init, journal_manifest, journal_write, journal_query, journal_export
  - journal_acknowledge, journal_actions, journal_scaffold, journal_pack, journal_snapshot
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.journal_init import FILE_METADATA as INIT_METADATA, run as run_journal_init
from tools.journal_manifest import FILE_METADATA as MANIFEST_METADATA, run as run_journal_manifest
from tools.journal_write import FILE_METADATA as WRITE_METADATA, run as run_journal_write
from tools.journal_query import FILE_METADATA as QUERY_METADATA, run as run_journal_query
from tools.journal_export import FILE_METADATA as EXPORT_METADATA, run as run_journal_export

# Phase 3+ tools — imported when available
try:
    from tools.journal_acknowledge import FILE_METADATA as ACKNOWLEDGE_METADATA, run as run_journal_acknowledge
except ImportError:
    ACKNOWLEDGE_METADATA, run_journal_acknowledge = None, None

try:
    from tools.journal_actions import FILE_METADATA as ACTIONS_METADATA, run as run_journal_actions
except ImportError:
    ACTIONS_METADATA, run_journal_actions = None, None

try:
    from tools.journal_scaffold import FILE_METADATA as SCAFFOLD_METADATA, run as run_journal_scaffold
except ImportError:
    SCAFFOLD_METADATA, run_journal_scaffold = None, None

try:
    from tools.journal_pack import FILE_METADATA as PACK_METADATA, run as run_journal_pack
except ImportError:
    PACK_METADATA, run_journal_pack = None, None

try:
    from tools.journal_snapshot import FILE_METADATA as SNAPSHOT_METADATA, run as run_journal_snapshot
except ImportError:
    SNAPSHOT_METADATA, run_journal_snapshot = None, None

try:
    from tools.authority_build import FILE_METADATA as AUTHORITY_BUILD_METADATA, run as run_authority_build
except ImportError:
    AUTHORITY_BUILD_METADATA, run_authority_build = None, None

try:
    from tools.authority_install import FILE_METADATA as AUTHORITY_INSTALL_METADATA, run as run_authority_install
except ImportError:
    AUTHORITY_INSTALL_METADATA, run_authority_install = None, None

try:
    from tools.module_decomp_planner import FILE_METADATA as MODULE_DECOMP_METADATA, run as run_module_decomp_planner
except ImportError:
    MODULE_DECOMP_METADATA, run_module_decomp_planner = None, None

try:
    from tools.tokenizing_patcher import FILE_METADATA as TOKENIZING_PATCHER_METADATA, run as run_tokenizing_patcher
except ImportError:
    TOKENIZING_PATCHER_METADATA, run_tokenizing_patcher = None, None

try:
    from tools.domain_boundary_audit import FILE_METADATA as DOMAIN_BOUNDARY_METADATA, run as run_domain_boundary_audit
except ImportError:
    DOMAIN_BOUNDARY_METADATA, run_domain_boundary_audit = None, None

try:
    from tools.scan_blocking_calls import FILE_METADATA as SCAN_BLOCKING_METADATA, run as run_scan_blocking_calls
except ImportError:
    SCAN_BLOCKING_METADATA, run_scan_blocking_calls = None, None

try:
    from tools.sqlite_schema_inspector import FILE_METADATA as SQLITE_INSPECTOR_METADATA, run as run_sqlite_schema_inspector
except ImportError:
    SQLITE_INSPECTOR_METADATA, run_sqlite_schema_inspector = None, None

try:
    from tools.import_graph_mapper import FILE_METADATA as IMPORT_GRAPH_METADATA, run as run_import_graph_mapper
except ImportError:
    IMPORT_GRAPH_METADATA, run_import_graph_mapper = None, None

try:
    from tools.tkinter_widget_tree import FILE_METADATA as TKINTER_TREE_METADATA, run as run_tkinter_widget_tree
except ImportError:
    TKINTER_TREE_METADATA, run_tkinter_widget_tree = None, None

try:
    from tools.file_tree_snapshot import FILE_METADATA as FILE_TREE_METADATA, run as run_file_tree_snapshot
except ImportError:
    FILE_TREE_METADATA, run_file_tree_snapshot = None, None

try:
    from tools.smoke_test_runner import FILE_METADATA as SMOKE_RUNNER_METADATA, run as run_smoke_test_runner
except ImportError:
    SMOKE_RUNNER_METADATA, run_smoke_test_runner = None, None

try:
    from tools.python_complexity_scorer import FILE_METADATA as COMPLEXITY_METADATA, run as run_python_complexity_scorer
except ImportError:
    COMPLEXITY_METADATA, run_python_complexity_scorer = None, None

try:
    from tools.dead_code_finder import FILE_METADATA as DEAD_CODE_METADATA, run as run_dead_code_finder
except ImportError:
    DEAD_CODE_METADATA, run_dead_code_finder = None, None

try:
    from tools.test_scaffold_generator import FILE_METADATA as TEST_SCAFFOLD_METADATA, run as run_test_scaffold_generator
except ImportError:
    TEST_SCAFFOLD_METADATA, run_test_scaffold_generator = None, None

try:
    from tools.schema_diff_tool import FILE_METADATA as SCHEMA_DIFF_METADATA, run as run_schema_diff_tool
except ImportError:
    SCHEMA_DIFF_METADATA, run_schema_diff_tool = None, None

try:
    from tools.builderset_authority_build import FILE_METADATA as BUILDERSET_BUILD_METADATA, run as run_builderset_authority_build
except ImportError:
    BUILDERSET_BUILD_METADATA, run_builderset_authority_build = None, None

try:
    from tools.builderset_authority_manifest import FILE_METADATA as BUILDERSET_MANIFEST_METADATA, run as run_builderset_authority_manifest
except ImportError:
    BUILDERSET_MANIFEST_METADATA, run_builderset_authority_manifest = None, None

try:
    from tools.builderset_authority_query import FILE_METADATA as BUILDERSET_QUERY_METADATA, run as run_builderset_authority_query
except ImportError:
    BUILDERSET_QUERY_METADATA, run_builderset_authority_query = None, None

try:
    from tools.builderset_authority_prepare_runtime import FILE_METADATA as BUILDERSET_RUNTIME_METADATA, run as run_builderset_authority_prepare_runtime
except ImportError:
    BUILDERSET_RUNTIME_METADATA, run_builderset_authority_prepare_runtime = None, None

try:
    from tools.builderset_authority_export import FILE_METADATA as BUILDERSET_EXPORT_METADATA, run as run_builderset_authority_export
except ImportError:
    BUILDERSET_EXPORT_METADATA, run_builderset_authority_export = None, None

try:
    from tools.builderset_authority_launch import FILE_METADATA as BUILDERSET_LAUNCH_METADATA, run as run_builderset_authority_launch
except ImportError:
    BUILDERSET_LAUNCH_METADATA, run_builderset_authority_launch = None, None


SERVER_INFO = {"name": "project-authority-kit", "version": "2.0.0"}

# Build registry from available tools
TOOL_REGISTRY: dict[str, tuple[dict, callable]] = {}
for meta, runner in [
    (INIT_METADATA, run_journal_init),
    (MANIFEST_METADATA, run_journal_manifest),
    (WRITE_METADATA, run_journal_write),
    (QUERY_METADATA, run_journal_query),
    (EXPORT_METADATA, run_journal_export),
    (ACKNOWLEDGE_METADATA, run_journal_acknowledge),
    (ACTIONS_METADATA, run_journal_actions),
    (SCAFFOLD_METADATA, run_journal_scaffold),
    (PACK_METADATA, run_journal_pack),
    (SNAPSHOT_METADATA, run_journal_snapshot),
    (AUTHORITY_BUILD_METADATA, run_authority_build),
    (AUTHORITY_INSTALL_METADATA, run_authority_install),
    (MODULE_DECOMP_METADATA, run_module_decomp_planner),
    (TOKENIZING_PATCHER_METADATA, run_tokenizing_patcher),
    (DOMAIN_BOUNDARY_METADATA, run_domain_boundary_audit),
    (SCAN_BLOCKING_METADATA, run_scan_blocking_calls),
    (SQLITE_INSPECTOR_METADATA, run_sqlite_schema_inspector),
    (IMPORT_GRAPH_METADATA, run_import_graph_mapper),
    (TKINTER_TREE_METADATA, run_tkinter_widget_tree),
    (FILE_TREE_METADATA, run_file_tree_snapshot),
    (SMOKE_RUNNER_METADATA, run_smoke_test_runner),
    (COMPLEXITY_METADATA, run_python_complexity_scorer),
    (DEAD_CODE_METADATA, run_dead_code_finder),
    (TEST_SCAFFOLD_METADATA, run_test_scaffold_generator),
    (SCHEMA_DIFF_METADATA, run_schema_diff_tool),
    (BUILDERSET_BUILD_METADATA, run_builderset_authority_build),
    (BUILDERSET_MANIFEST_METADATA, run_builderset_authority_manifest),
    (BUILDERSET_QUERY_METADATA, run_builderset_authority_query),
    (BUILDERSET_RUNTIME_METADATA, run_builderset_authority_prepare_runtime),
    (BUILDERSET_EXPORT_METADATA, run_builderset_authority_export),
    (BUILDERSET_LAUNCH_METADATA, run_builderset_authority_launch),
]:
    if meta is not None and runner is not None:
        TOOL_REGISTRY[meta["mcp_name"]] = (meta, runner)


def _success(result: dict) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
        "structuredContent": result,
        "isError": result.get("status") == "error",
    }


def _tool_list() -> list[dict]:
    return [
        {
            "name": metadata["mcp_name"],
            "description": metadata["summary"],
            "inputSchema": metadata["input_schema"],
        }
        for metadata, _ in TOOL_REGISTRY.values()
    ]


def _call_tool(name: str, arguments: dict) -> dict:
    entry = TOOL_REGISTRY.get(name)
    if not entry:
        return _success({"status": "error", "tool": name, "input": arguments, "result": {"message": f"Unknown tool: {name}"}})
    _, runner = entry
    try:
        return _success(runner(arguments))
    except Exception as exc:
        return _success({
            "status": "error", "tool": name, "input": arguments,
            "result": {"message": str(exc), "traceback": traceback.format_exc()},
        })


def _read_content_length_message(first_line: bytes) -> dict | None:
    """Read a Content-Length framed MCP message."""
    headers: dict[str, str] = {}
    line = first_line
    while True:
        if not line:
            return None
        if line in {b"\r\n", b"\n"}:
            break
        key, _, value = line.decode("utf-8").partition(":")
        headers[key.strip().lower()] = value.strip()
        line = sys.stdin.buffer.readline()

    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None
    body = sys.stdin.buffer.read(content_length)
    if not body:
        return None
    return json.loads(body.decode("utf-8"))


def _read_message() -> dict | None:
    """Read one stdin message. Supports Content-Length framing and NDJSON fallback."""
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(b"{"):
            return json.loads(stripped.decode("utf-8"))
        if b"content-length" in stripped.lower():
            return _read_content_length_message(line)
        continue


def _write_message(payload: dict) -> None:
    """Write one NDJSON message to stdout."""
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(body + b"\n")
    sys.stdout.buffer.flush()


def _handle_request(message: dict) -> dict | None:
    method = message.get("method")
    message_id = message.get("id")
    params = message.get("params", {})

    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": message_id, "result": {}}
    if method == "initialize":
        client_version = params.get("protocolVersion", "2024-11-05")
        return {
            "jsonrpc": "2.0", "id": message_id,
            "result": {
                "protocolVersion": client_version,
                "serverInfo": SERVER_INFO,
                "capabilities": {"tools": {}},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": message_id, "result": {"tools": _tool_list()}}
    if method == "tools/call":
        return {"jsonrpc": "2.0", "id": message_id, "result": _call_tool(params["name"], params.get("arguments", {}))}
    return {
        "jsonrpc": "2.0", "id": message_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> int:
    while True:
        message = _read_message()
        if message is None:
            return 0
        response = _handle_request(message)
        if response is not None:
            _write_message(response)


if __name__ == "__main__":
    raise SystemExit(main())
