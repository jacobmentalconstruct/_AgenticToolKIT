from __future__ import annotations

import os
import sys

from common import ensure_runtime, target_project_root


def main() -> int:
    runtime_dir = ensure_runtime()
    os.chdir(target_project_root())
    runtime_launcher = runtime_dir / "src" / "launch_ui.py"
    os.execv(sys.executable, [sys.executable, str(runtime_launcher), *sys.argv[1:]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
