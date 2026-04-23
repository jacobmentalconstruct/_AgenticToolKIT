"""
FILE: common.py
ROLE: Shared CLI runtime for _constraint-registry tools.
WHAT IT DOES: Provides standard_main, tool_result, tool_error for consistent
  CLI and MCP contract compliance across all tools in this package.
HOW TO USE: Import from common in any tool script.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tool_result(tool: str, inp: dict, result: dict) -> dict:
    return {"status": "ok", "tool": tool, "input": inp, "result": result}


def tool_error(tool: str, inp: dict, message: str) -> dict:
    return {"status": "error", "tool": tool, "input": inp, "result": {"message": message}}


def emit_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2))


def load_input(args: argparse.Namespace) -> dict:
    if getattr(args, "input_json", None):
        return json.loads(args.input_json)
    if getattr(args, "input_file", None):
        return json.loads(Path(args.input_file).read_text(encoding="utf-8"))
    return {}


def standard_main(metadata: dict, run_fn) -> None:
    parser = argparse.ArgumentParser(description=metadata.get("summary", ""))
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("metadata", help="Print tool metadata as JSON")

    run_p = sub.add_parser("run", help="Execute the tool")
    run_p.add_argument("--input-json", dest="input_json", default=None)
    run_p.add_argument("--input-file", dest="input_file", default=None)

    args = parser.parse_args()

    if args.command == "metadata":
        emit_json(metadata)
    elif args.command == "run":
        emit_json(run_fn(load_input(args)))
    else:
        parser.print_help()
        sys.exit(1)
