"""
FILE: builderset_authority_manifest.py
ROLE: Inspect the packed BuilderSET authority manifest and schema summary.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.builderset_authority import inspect_builderset_authority


FILE_METADATA = {
    "tool_name": "builderset_authority_manifest",
    "version": "1.0.0",
    "entrypoint": "src/tools/builderset_authority_manifest.py",
    "category": "introspection",
    "summary": "Inspect the packed BuilderSET authority DB, manifest, and onboarding metadata.",
    "mcp_name": "builderset_authority_manifest",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_path": {"type": "string"},
        },
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    result = inspect_builderset_authority(db_path=arguments.get("db_path"))
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
