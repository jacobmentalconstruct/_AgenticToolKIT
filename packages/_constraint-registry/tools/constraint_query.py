"""
FILE: constraint_query.py
ROLE: Query the constraint registry for task-relevant constraint packets.
WHAT IT DOES:
  - Retrieves constraints by task profile, domain tags, severity, or individual UID
  - Returns distilled constraint packets sized for the requesting agent's capacity
  - Supports tier filtering (spirit/letter/gate) to match model size
HOW TO USE:
  - python _constraint-registry/tools/constraint_query.py metadata
  - python _constraint-registry/tools/constraint_query.py run --input-json '{"profile": "ui_implementation"}'
  - python _constraint-registry/tools/constraint_query.py run --input-json '{"domain": "ownership", "severity": "HARD_BLOCK"}'
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import standard_main, tool_result, tool_error

FILE_METADATA = {
    "tool_name": "constraint_query",
    "version": "1.0.0",
    "entrypoint": "tools/constraint_query.py",
    "category": "query",
    "summary": "Query the constraint registry for task-relevant constraint packets.",
    "mcp_name": "constraint_query",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_path": {
                "type": "string",
                "description": "Path to the registry SQLite file. Defaults to <package>/constraint_registry.sqlite3"
            },
            "profile": {
                "type": "string",
                "description": "Task profile ID to retrieve a pre-built constraint packet (e.g. 'ui_implementation', 'refactoring', 'cleanup')."
            },
            "domain": {
                "type": "string",
                "description": "Filter by domain tag (e.g. 'ownership', 'ui', 'boundary', 'sourcing')."
            },
            "severity": {
                "type": "string",
                "enum": ["HARD_BLOCK", "PUSHBACK", "ADVISORY"],
                "description": "Filter by minimum severity level."
            },
            "tier": {
                "type": "string",
                "enum": ["spirit", "letter", "gate"],
                "description": "Filter by tier. 'spirit' = high-level intent (large models), 'letter' = specific rules (mid models), 'gate' = binary decisions (small models)."
            },
            "uids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Retrieve specific constraint units by UID."
            },
            "list_profiles": {
                "type": "boolean",
                "default": False,
                "description": "If true, return available task profiles instead of constraints."
            },
            "list_domains": {
                "type": "boolean",
                "default": False,
                "description": "If true, return all unique domain tags in the registry."
            },
            "stats": {
                "type": "boolean",
                "default": False,
                "description": "If true, return registry statistics."
            }
        }
    }
}

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

SEVERITY_RANK = {"HARD_BLOCK": 3, "PUSHBACK": 2, "ADVISORY": 1}


def _connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(
            f"Registry not found at {db_path}. Run registry_build first."
        )
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    results = []
    for row in rows:
        d = dict(row)
        if "domain_tags" in d:
            d["domain_tags"] = json.loads(d["domain_tags"])
        if "constraint_uids" in d:
            d["constraint_uids"] = json.loads(d["constraint_uids"])
        results.append(d)
    return results


def _query_by_profile(conn: sqlite3.Connection, profile_id: str, tier: str | None) -> dict:
    """Get constraints for a pre-built task profile."""
    row = conn.execute(
        "SELECT * FROM task_profiles WHERE profile_id = ?", (profile_id,)
    ).fetchone()
    if not row:
        available = [r["profile_id"] for r in conn.execute("SELECT profile_id FROM task_profiles").fetchall()]
        raise ValueError(f"Unknown profile '{profile_id}'. Available: {available}")

    profile = dict(row)
    uids = json.loads(profile["constraint_uids"])
    placeholders = ",".join("?" for _ in uids)

    query = f"SELECT * FROM constraint_units WHERE uid IN ({placeholders})"
    params: list = list(uids)

    if tier:
        query += " AND tier = ?"
        params.append(tier)

    query += " ORDER BY CASE severity WHEN 'HARD_BLOCK' THEN 1 WHEN 'PUSHBACK' THEN 2 ELSE 3 END"

    constraints = _rows_to_dicts(conn.execute(query, params).fetchall())
    return {
        "profile_id": profile_id,
        "profile_description": profile["description"],
        "constraint_count": len(constraints),
        "constraints": constraints,
    }


def _query_by_filters(
    conn: sqlite3.Connection,
    domain: str | None,
    severity: str | None,
    tier: str | None,
) -> dict:
    """Get constraints matching domain/severity/tier filters."""
    clauses: list[str] = []
    params: list = []

    if domain:
        clauses.append("domain_tags LIKE ?")
        params.append(f'%"{domain}"%')
    if severity:
        min_rank = SEVERITY_RANK.get(severity, 0)
        matching = [s for s, r in SEVERITY_RANK.items() if r >= min_rank]
        placeholders = ",".join("?" for _ in matching)
        clauses.append(f"severity IN ({placeholders})")
        params.extend(matching)
    if tier:
        clauses.append("tier = ?")
        params.append(tier)

    where = " AND ".join(clauses) if clauses else "1=1"
    query = f"""SELECT * FROM constraint_units WHERE {where}
                ORDER BY CASE severity WHEN 'HARD_BLOCK' THEN 1 WHEN 'PUSHBACK' THEN 2 ELSE 3 END"""

    constraints = _rows_to_dicts(conn.execute(query, params).fetchall())
    return {
        "filters": {"domain": domain, "severity": severity, "tier": tier},
        "constraint_count": len(constraints),
        "constraints": constraints,
    }


def _query_by_uids(conn: sqlite3.Connection, uids: list[str]) -> dict:
    """Get specific constraints by UID."""
    placeholders = ",".join("?" for _ in uids)
    rows = conn.execute(
        f"SELECT * FROM constraint_units WHERE uid IN ({placeholders})", uids
    ).fetchall()
    constraints = _rows_to_dicts(rows)
    found_uids = {c["uid"] for c in constraints}
    missing = [u for u in uids if u not in found_uids]
    result: dict = {"constraint_count": len(constraints), "constraints": constraints}
    if missing:
        result["missing_uids"] = missing
    return result


def _list_profiles(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("SELECT * FROM task_profiles ORDER BY profile_id").fetchall()
    profiles = _rows_to_dicts(rows)
    return {"profile_count": len(profiles), "profiles": profiles}


def _list_domains(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("SELECT domain_tags FROM constraint_units").fetchall()
    all_tags: set[str] = set()
    for row in rows:
        all_tags.update(json.loads(row["domain_tags"]))
    sorted_tags = sorted(all_tags)
    return {"domain_count": len(sorted_tags), "domains": sorted_tags}


def _get_stats(conn: sqlite3.Connection) -> dict:
    total = conn.execute("SELECT COUNT(*) FROM constraint_units").fetchone()[0]
    severity_counts = {}
    for row in conn.execute("SELECT severity, COUNT(*) as cnt FROM constraint_units GROUP BY severity").fetchall():
        severity_counts[row["severity"]] = row["cnt"]
    tier_counts = {}
    for row in conn.execute("SELECT tier, COUNT(*) as cnt FROM constraint_units GROUP BY tier").fetchall():
        tier_counts[row["tier"]] = row["cnt"]
    profile_count = conn.execute("SELECT COUNT(*) FROM task_profiles").fetchone()[0]
    meta = {}
    for row in conn.execute("SELECT key, value FROM registry_meta").fetchall():
        meta[row["key"]] = row["value"]
    return {
        "total_constraints": total,
        "severity_counts": severity_counts,
        "tier_counts": tier_counts,
        "task_profiles": profile_count,
        "meta": meta,
    }


def run(arguments: dict) -> dict:
    db_path = Path(arguments.get("db_path") or (PACKAGE_ROOT / "constraint_registry.sqlite3"))

    try:
        conn = _connect(db_path)

        if arguments.get("list_profiles"):
            result = _list_profiles(conn)
        elif arguments.get("list_domains"):
            result = _list_domains(conn)
        elif arguments.get("stats"):
            result = _get_stats(conn)
        elif arguments.get("uids"):
            result = _query_by_uids(conn, arguments["uids"])
        elif arguments.get("profile"):
            result = _query_by_profile(conn, arguments["profile"], arguments.get("tier"))
        else:
            result = _query_by_filters(
                conn,
                arguments.get("domain"),
                arguments.get("severity"),
                arguments.get("tier"),
            )

        conn.close()
        return tool_result(FILE_METADATA["tool_name"], arguments, result)

    except Exception as exc:
        return tool_error(FILE_METADATA["tool_name"], arguments, str(exc))


if __name__ == "__main__":
    standard_main(FILE_METADATA, run)
