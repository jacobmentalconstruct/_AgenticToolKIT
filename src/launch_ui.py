"""
FILE: launch_ui.py
ROLE: Convenience launcher for the App Journal Tkinter UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.app_journal_ui import main

if __name__ == "__main__":
    raise SystemExit(main())
