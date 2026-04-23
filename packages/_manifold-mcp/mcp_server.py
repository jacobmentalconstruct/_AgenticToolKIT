"""
FILE: mcp_server.py
ROLE: MCP stdio server for _manifold-mcp.
WHAT IT DOES: Exposes reversible manifold tools through MCP using the same underlying `run(arguments)` functions used by CLI execution.
HOW TO USE:
  - Start: python _manifold-mcp/mcp_server.py
  - Connect as a stdio MCP server from an MCP-capable client.
TOOLS:
  - manifold_ingest
  - manifold_query
  - manifold_extract
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from tools.manifold_extract import FILE_METADATA as EXTRACT_METADATA, run as run_manifold_extract
from tools.manifold_ingest import FILE_METADATA as INGEST_METADATA, run as run_manifold_ingest
from tools.manifold_query import FILE_METADATA as QUERY_METADATA, run as run_manifold_query


SERVER_INFO = {
    "name": "manifold-mcp",
    "version": "1.0.0"
}

TOOL_REGISTRY = {
    INGEST_METADATA["mcp_name"]: (INGEST_METADATA, run_manifold_ingest),
    QUERY_METADATA["mcp_name"]: (QUERY_METADATA, run_manifold_query),
    EXTRACT_METADATA["mcp_name"]: (EXTRACT_METADATA, run_manifold_extract)
}


def _success(result: dict) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
        "structuredContent": result,
        "isError": result.get("status") == "error"
    }


def _tool_list() -> list[dict]:
    return [
        {
            "name": metadata["mcp_name"],
            "description": metadata["summary"],
            "inputSchema": metadata["input_schema"]
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
            "status": "error",
            "tool": name,
            "input": arguments,
            "result": {
                "message": str(exc),
                "traceback": traceback.format_exc()
            }
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
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "protocolVersion": client_version,
                "serverInfo": SERVER_INFO,
                "capabilities": {"tools": {}}
            }
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": message_id, "result": {"tools": _tool_list()}}
    if method == "tools/call":
        return {"jsonrpc": "2.0", "id": message_id, "result": _call_tool(params["name"], params.get("arguments", {}))}
    return {
        "jsonrpc": "2.0",
        "id": message_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
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
