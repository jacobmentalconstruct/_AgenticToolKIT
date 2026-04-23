"""
FILE: builderset_authority_query.py
ROLE: Query packed BuilderSET authority files without hydrating them.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.builderset_authority import query_builderset_authority


FILE_METADATA = {
    "tool_name": "builderset_authority_query",
    "version": "1.0.0",
    "entrypoint": "src/tools/builderset_authority_query.py",
    "category": "introspection",
    "summary": "Query BuilderSET authority contents by content class, top-level area, or path fragment.",
    "mcp_name": "builderset_authority_query",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_path": {"type": "string"},
            "content_class": {"type": "string"},
            "top_level": {"type": "string"},
            "path_contains": {"type": "string"},
            "limit": {"type": "integer"},
            "include_preview": {"type": "boolean"},
        },
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    result = query_builderset_authority(
        db_path=arguments.get("db_path"),
        content_class=arguments.get("content_class"),
        top_level=arguments.get("top_level"),
        path_contains=arguments.get("path_contains"),
        limit=int(arguments.get("limit", 50)),
        include_preview=bool(arguments.get("include_preview", False)),
    )
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
