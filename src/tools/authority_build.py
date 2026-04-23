"""
FILE: authority_build.py
ROLE: Build the packed authority.sqlite3 artifact for the vendored kit.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.authority_package import build_authority_package


FILE_METADATA = {
    "tool_name": "authority_build",
    "version": "2.0.0",
    "entrypoint": "src/tools/authority_build.py",
    "category": "packaging",
    "summary": "Build the packed authority.sqlite3 artifact for the vendored authority kit.",
    "mcp_name": "authority_build",
    "input_schema": {
        "type": "object",
        "properties": {
            "package_root": {"type": "string"},
            "output_db": {"type": "string"},
        },
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    result = build_authority_package(
        package_root=arguments.get("package_root"),
        output_db=arguments.get("output_db"),
    )
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
