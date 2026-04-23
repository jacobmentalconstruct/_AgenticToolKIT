"""
FILE: authority_install.py
ROLE: Install the vendored thin shim into a target project.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import standard_main, tool_result
from lib.authority_package import install_authority_shim


FILE_METADATA = {
    "tool_name": "authority_install",
    "version": "2.0.0",
    "entrypoint": "src/tools/authority_install.py",
    "category": "install",
    "summary": "Install the DB-packed thin _project-authority shim into a target project.",
    "mcp_name": "authority_install",
    "input_schema": {
        "type": "object",
        "properties": {
            "target_project_root": {"type": "string"},
            "package_root": {"type": "string"},
            "overwrite": {"type": "boolean", "default": False},
            "preview": {"type": "boolean", "default": False},
        },
        "required": ["target_project_root"],
        "additionalProperties": False,
    },
}


def run(arguments: dict) -> dict:
    result = install_authority_shim(
        arguments["target_project_root"],
        package_root=arguments.get("package_root"),
        overwrite=arguments.get("overwrite", False),
        preview=arguments.get("preview", False),
    )
    return tool_result(FILE_METADATA["tool_name"], arguments, result)


if __name__ == "__main__":
    raise SystemExit(standard_main(FILE_METADATA, run))
