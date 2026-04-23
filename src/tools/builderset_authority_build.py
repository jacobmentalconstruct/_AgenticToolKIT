"""
FILE: builderset_authority_build.py
ROLE: Build the packed BuilderSET authority SQLite artifact.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.builderset_authority import build_builderset_authority


FILE_METADATA = {
    "tool_name": "builderset_authority_build",
    "version": "1.0.0",
    "entrypoint": "src/tools/builderset_authority_build.py",
    "category": "packaging",
    "summary": "Build the toolbox-resident packed BuilderSET authority from a live source snapshot.",
    "mcp_name": "builderset_authority_build",
    "input_schema": {
        "type": "object",
        "properties": {
            "source_project_root": {"type": "string"},
            "output_db": {"type": "string"},
            "output_manifest": {"type": "string"},
        },
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    result = build_builderset_authority(
        source_project_root=arguments.get("source_project_root"),
        output_db=arguments.get("output_db"),
        output_manifest=arguments.get("output_manifest"),
    )
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
