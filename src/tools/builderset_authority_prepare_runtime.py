"""
FILE: builderset_authority_prepare_runtime.py
ROLE: Hydrate the packed BuilderSET runtime cache from the authority DB.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.builderset_authority import prepare_builderset_runtime


FILE_METADATA = {
    "tool_name": "builderset_authority_prepare_runtime",
    "version": "1.0.0",
    "entrypoint": "src/tools/builderset_authority_prepare_runtime.py",
    "category": "runtime",
    "summary": "Hydrate or reuse the cache-backed packed BuilderSET runtime from SQLite.",
    "mcp_name": "builderset_authority_prepare_runtime",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_path": {"type": "string"},
            "cache_root": {"type": "string"},
            "force": {"type": "boolean"},
        },
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    result = prepare_builderset_runtime(
        db_path=arguments.get("db_path"),
        cache_root=arguments.get("cache_root"),
        force=bool(arguments.get("force", False)),
    )
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
