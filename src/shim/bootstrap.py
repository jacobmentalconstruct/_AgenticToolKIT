from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import ensure_runtime, target_project_root


def _tool_script(runtime_dir: Path, tool_name: str) -> Path:
    return runtime_dir / "src" / "tools" / f"{tool_name}.py"


def _run_tool(runtime_dir: Path, tool_name: str, payload: dict) -> dict:
    completed = subprocess.run(
        [
            sys.executable,
            str(_tool_script(runtime_dir, tool_name)),
            "run",
            "--input-json",
            json.dumps(payload),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    return json.loads(completed.stdout)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap a vendored project using the Project Authority Kit.")
    parser.add_argument("--project-root", help="Target project root. Defaults to the parent of .dev-tools.")
    parser.add_argument("--scaffold", action="store_true", help="Also scaffold the default project surfaces.")
    parser.add_argument("--overwrite", action="store_true", help="Allow scaffold overwrites when scaffolding.")
    parser.add_argument("--acknowledge-actor", help="Optional actor id to acknowledge the builder contract.")
    parser.add_argument("--actor-type", default="agent", help="Actor type for contract acknowledgment.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime_dir = ensure_runtime()
    project_root = Path(args.project_root).resolve() if args.project_root else target_project_root()

    result = {
        "runtime_dir": str(runtime_dir),
        "project_root": str(project_root),
        "init": _run_tool(runtime_dir, "journal_init", {"project_root": str(project_root)}),
    }
    if args.scaffold:
        result["scaffold"] = _run_tool(
            runtime_dir,
            "journal_scaffold",
            {"project_root": str(project_root), "overwrite": args.overwrite},
        )
    if args.acknowledge_actor:
        result["acknowledge"] = _run_tool(
            runtime_dir,
            "journal_acknowledge",
            {"project_root": str(project_root), "actor_id": args.acknowledge_actor, "actor_type": args.actor_type},
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
