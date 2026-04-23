"""
FILE: builderset_authority_export.py
ROLE: Export selected packed BuilderSET files to disk on demand.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.builderset_authority import export_builderset_content


FILE_METADATA = {
    "tool_name": "builderset_authority_export",
    "version": "1.0.0",
    "entrypoint": "src/tools/builderset_authority_export.py",
    "category": "export",
    "summary": "Export selected BuilderSET authority files from SQLite without hydrating the full codex.",
    "mcp_name": "builderset_authority_export",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_path": {"type": "string"},
            "destination_root": {"type": "string"},
            "content_class": {"type": "string"},
            "relative_paths": {"type": "array", "items": {"type": "string"}},
            "relative_path_prefix": {"type": "string"},
            "overwrite": {"type": "boolean"},
        },
        "required": ["destination_root"],
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    result = export_builderset_content(
        db_path=arguments.get("db_path"),
        destination_root=arguments["destination_root"],
        content_class=arguments.get("content_class"),
        relative_paths=arguments.get("relative_paths"),
        relative_path_prefix=arguments.get("relative_path_prefix"),
        overwrite=bool(arguments.get("overwrite", False)),
    )
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
