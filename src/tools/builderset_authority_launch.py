"""
FILE: builderset_authority_launch.py
ROLE: Describe or probe packed BuilderSET launch surfaces from the hydrated cache.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.builderset_authority import describe_builderset_launch, probe_builderset_surface


FILE_METADATA = {
    "tool_name": "builderset_authority_launch",
    "version": "1.0.0",
    "entrypoint": "src/tools/builderset_authority_launch.py",
    "category": "runtime",
    "summary": "Describe or probe packed BuilderSET MCP, UI, or catalog launch surfaces.",
    "mcp_name": "builderset_authority_launch",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_path": {"type": "string"},
            "cache_root": {"type": "string"},
            "surface": {"type": "string"},
            "action": {"type": "string"},
            "python_executable": {"type": "string"},
        },
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    surface = arguments.get("surface", "mcp")
    action = arguments.get("action", "describe")
    if action == "probe":
        result = probe_builderset_surface(
            db_path=arguments.get("db_path"),
            cache_root=arguments.get("cache_root"),
            surface=surface,
            python_executable=arguments.get("python_executable"),
        )
    else:
        result = describe_builderset_launch(
            db_path=arguments.get("db_path"),
            cache_root=arguments.get("cache_root"),
            surface=surface,
            python_executable=arguments.get("python_executable"),
        )
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
