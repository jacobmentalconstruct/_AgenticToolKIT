from __future__ import annotations

import sqlite3
from pathlib import Path


SHIM_DIR = Path(__file__).resolve().parent
AUTHORITY_DB_PATH = SHIM_DIR / "authority.sqlite3"
RUNTIME_DIR = SHIM_DIR / "runtime"


def target_project_root() -> Path:
    return SHIM_DIR.parents[1]


def ensure_runtime() -> Path:
    runtime_server = RUNTIME_DIR / "src" / "mcp_server.py"
    if runtime_server.exists():
        return RUNTIME_DIR
    unpack_runtime(AUTHORITY_DB_PATH, RUNTIME_DIR)
    return RUNTIME_DIR


def unpack_runtime(db_path: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute("SELECT relative_path, body_hash FROM packed_tools ORDER BY relative_path").fetchall()
        for row in rows:
            blob = connection.execute(
                "SELECT content_text FROM blob_store WHERE content_hash = ?",
                (row["body_hash"],),
            ).fetchone()
            if blob is None:
                continue
            target_path = target_dir / row["relative_path"]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(blob["content_text"], encoding="utf-8")
    finally:
        connection.close()
