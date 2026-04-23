"""
FILE: smoke_test.py
ROLE: Portable self-test for _constraint-registry.
WHAT IT DOES: Verifies CLI, query, and MCP paths for the constraint registry.
HOW TO USE:
  - python _constraint-registry/smoke_test.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _run_json(args: list[str]) -> dict:
    completed = subprocess.run(
        args, cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    return json.loads(completed.stdout)


def _mcp_message(message: dict) -> bytes:
    return json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n"


def _mcp_read(stdout) -> dict:
    while True:
        line = stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed before responding.")
        stripped = line.strip()
        if stripped:
            return json.loads(stripped.decode("utf-8"))


def test_build_metadata() -> None:
    result = _run_json([sys.executable, str(ROOT / "tools" / "registry_build.py"), "metadata"])
    assert result["tool_name"] == "registry_build", f"Unexpected tool name: {result['tool_name']}"
    assert "input_schema" in result
    print("  [PASS] registry_build metadata")


def test_query_metadata() -> None:
    result = _run_json([sys.executable, str(ROOT / "tools" / "constraint_query.py"), "metadata"])
    assert result["tool_name"] == "constraint_query", f"Unexpected tool name: {result['tool_name']}"
    assert "input_schema" in result
    print("  [PASS] constraint_query metadata")


def test_build_and_query() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "test_registry.sqlite3")

        # Build
        build_result = _run_json([
            sys.executable, str(ROOT / "tools" / "registry_build.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "force": True})
        ])
        assert build_result["status"] == "ok", f"Build failed: {build_result}"
        assert build_result["result"]["constraint_units"] > 50, \
            f"Expected >50 ACUs, got {build_result['result']['constraint_units']}"
        print(f"  [PASS] registry_build: {build_result['result']['constraint_units']} ACUs, "
              f"{build_result['result']['task_profiles']} profiles")

        # Query by profile
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "profile": "ui_implementation"})
        ])
        assert query_result["status"] == "ok", f"Profile query failed: {query_result}"
        constraints = query_result["result"]["constraints"]
        assert len(constraints) > 0, "Expected constraints for ui_implementation profile"
        # Verify HARD_BLOCKs come first
        severities = [c["severity"] for c in constraints]
        hard_block_indices = [i for i, s in enumerate(severities) if s == "HARD_BLOCK"]
        non_hard_indices = [i for i, s in enumerate(severities) if s != "HARD_BLOCK"]
        if hard_block_indices and non_hard_indices:
            assert max(hard_block_indices) < min(non_hard_indices), "HARD_BLOCKs should sort first"
        print(f"  [PASS] constraint_query profile: {len(constraints)} constraints for ui_implementation")

        # Query by domain
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "domain": "ownership"})
        ])
        assert query_result["status"] == "ok"
        assert query_result["result"]["constraint_count"] > 0
        print(f"  [PASS] constraint_query domain: {query_result['result']['constraint_count']} ownership constraints")

        # Query by severity
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "severity": "HARD_BLOCK"})
        ])
        assert query_result["status"] == "ok"
        for c in query_result["result"]["constraints"]:
            assert c["severity"] == "HARD_BLOCK", f"Expected HARD_BLOCK, got {c['severity']}"
        print(f"  [PASS] constraint_query severity: {query_result['result']['constraint_count']} HARD_BLOCK constraints")

        # Query by tier
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "tier": "gate"})
        ])
        assert query_result["status"] == "ok"
        for c in query_result["result"]["constraints"]:
            assert c["tier"] == "gate"
        print(f"  [PASS] constraint_query tier: {query_result['result']['constraint_count']} gate-tier constraints")

        # List profiles
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "list_profiles": True})
        ])
        assert query_result["status"] == "ok"
        profile_ids = [p["profile_id"] for p in query_result["result"]["profiles"]]
        for expected in ("ui_implementation", "core_implementation", "refactoring", "cleanup", "documentation"):
            assert expected in profile_ids, f"Missing profile: {expected}"
        print(f"  [PASS] constraint_query list_profiles: {len(profile_ids)} profiles")

        # List domains
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "list_domains": True})
        ])
        assert query_result["status"] == "ok"
        domains = query_result["result"]["domains"]
        for expected in ("ownership", "ui", "core", "boundary", "sourcing"):
            assert expected in domains, f"Missing domain: {expected}"
        print(f"  [PASS] constraint_query list_domains: {len(domains)} domains")

        # Stats
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "stats": True})
        ])
        assert query_result["status"] == "ok"
        assert query_result["result"]["total_constraints"] > 50
        print(f"  [PASS] constraint_query stats: {query_result['result']['total_constraints']} total")

        # Query by UIDs
        query_result = _run_json([
            sys.executable, str(ROOT / "tools" / "constraint_query.py"),
            "run", "--input-json", json.dumps({"db_path": db_path, "uids": ["BCC-4.1", "BCC-2.0", "BCC-FAKE"]})
        ])
        assert query_result["status"] == "ok"
        assert query_result["result"]["constraint_count"] == 2
        assert "BCC-FAKE" in query_result["result"].get("missing_uids", [])
        print("  [PASS] constraint_query uids: found 2, reported 1 missing")


def test_mcp_smoke() -> None:
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "mcp_server.py")],
        cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        assert proc.stdin is not None
        assert proc.stdout is not None

        # Initialize
        proc.stdin.write(_mcp_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}))
        proc.stdin.flush()
        init_response = _mcp_read(proc.stdout)
        assert init_response.get("result", {}).get("serverInfo", {}).get("name") == "constraint-registry"

        # List tools
        proc.stdin.write(_mcp_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
        proc.stdin.flush()
        list_response = _mcp_read(proc.stdout)
        tool_names = [t["name"] for t in list_response.get("result", {}).get("tools", [])]
        assert "registry_build" in tool_names
        assert "constraint_query" in tool_names

        print("  [PASS] MCP server: initialize + tools/list")
    finally:
        proc.kill()
        proc.wait(timeout=5)


def main() -> int:
    print("=== _constraint-registry smoke test ===")
    try:
        test_build_metadata()
        test_query_metadata()
        test_build_and_query()
        test_mcp_smoke()
        print("=== ALL TESTS PASSED ===")
        return 0
    except Exception as exc:
        print(f"\n  [FAIL] {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
