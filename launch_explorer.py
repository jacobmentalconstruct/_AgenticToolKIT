"""
FILE: launch_explorer.py
ROLE: Open the offline onboarding microsite in the default browser.
"""

from __future__ import annotations

import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
START_PAGE = ROOT / "onboarding" / "START_HERE.html"


def main() -> int:
    resolved = START_PAGE.resolve()
    print(f"Opening {resolved}")
    webbrowser.open(resolved.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
