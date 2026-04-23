"""
FILE: builderset_authority.py
ROLE: Package the live BuilderSET repo into a toolbox-resident SQLite authority.
WHAT IT DOES: Stores the BuilderSET codex as runtime/reference content, prepares
    cache-hydrated runtime trees, supports selective export, and validates the
    packed runtime without depending on the live source repo at runtime.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import shutil
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from common import now_stamp, write_json


AUTHORITY_SCHEMA_VERSION = "1.0.0"
AUTHORITY_DB_NAME = "builderset_authority.sqlite3"
AUTHORITY_MANIFEST_NAME = "builderset_authority_manifest.json"
AUTHORITY_LABEL = "_builderset-authority"
CONTENT_RUNTIME = "runtime_executable"
CONTENT_REFERENCE = "reference_only"
PACKAGE_EXCLUDES = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".claude",
    ".dev-tools",
    "__pycache__",
}
RUNTIME_TOP_LEVEL = {"src", "library", "assets"}
REFERENCE_TOP_LEVEL = {"_docs", "_smoke-tests", "finals", "_archives", "_output", "_sandbox"}
RUNTIME_ROOT_FILES = {
    ".mcp.json",
    "requirements.txt",
    "run.bat",
    "run_sandboxer.bat",
    "setup_env.bat",
}
MAX_BLOB_BYTES = 50 * 1024 * 1024  # 50 MB — skip files larger than this


def package_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def source_project_root_from_here() -> Path | None:
    """Default source root is the project that contains .dev-tools (three levels up from src/lib/).
    Returns None if .dev-tools appears to be the canonical/source copy rather than a vendored install."""
    candidate = Path(__file__).resolve().parents[3]
    devtools_dir = Path(__file__).resolve().parents[2]
    # Sanity check: the candidate should contain .dev-tools as a child,
    # and should look like a real project (not a broad workspace folder).
    if (candidate / ".dev-tools").resolve() == devtools_dir.resolve():
        return candidate
    return None


def authority_root_from_here() -> Path:
    return package_root_from_here() / "authorities" / AUTHORITY_LABEL


def default_output_db_path() -> Path:
    return authority_root_from_here() / "artifacts" / AUTHORITY_DB_NAME


def default_output_manifest_path() -> Path:
    return authority_root_from_here() / "artifacts" / AUTHORITY_MANIFEST_NAME


def default_runtime_cache_root() -> Path:
    return package_root_from_here() / "runtime" / AUTHORITY_LABEL


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    return connection


def _initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS authority_meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS authority_blobs(
            content_hash TEXT PRIMARY KEY,
            content BLOB NOT NULL,
            byte_size INTEGER NOT NULL,
            content_encoding TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            preview_text TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS authority_files(
            relative_path TEXT PRIMARY KEY,
            top_level TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            content_class TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            byte_size INTEGER NOT NULL,
            is_text INTEGER NOT NULL,
            executable INTEGER NOT NULL,
            source_mtime TEXT NOT NULL,
            notes_json TEXT NOT NULL DEFAULT '{}'
        );

        CREATE INDEX IF NOT EXISTS idx_authority_files_class
            ON authority_files(content_class);

        CREATE INDEX IF NOT EXISTS idx_authority_files_top_level
            ON authority_files(top_level);

        CREATE TABLE IF NOT EXISTS authority_builds(
            build_id TEXT PRIMARY KEY,
            built_at TEXT NOT NULL,
            source_root TEXT NOT NULL,
            source_branch TEXT NOT NULL,
            source_commit TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            runtime_hash TEXT NOT NULL,
            reference_hash TEXT NOT NULL,
            file_count INTEGER NOT NULL,
            runtime_file_count INTEGER NOT NULL,
            reference_file_count INTEGER NOT NULL,
            manifest_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS authority_onboarding(
            step_number INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            body TEXT NOT NULL
        );
        """
    )
    connection.execute(f"PRAGMA user_version = {int(AUTHORITY_SCHEMA_VERSION.split('.')[0])}")


def _try_run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _git_metadata(source_root: Path) -> dict[str, str]:
    return {
        "branch": _try_run(["git", "rev-parse", "--abbrev-ref", "HEAD"], source_root) or "unknown",
        "commit": _try_run(["git", "rev-parse", "HEAD"], source_root) or "unknown",
    }


def _is_excluded(relative_path: Path) -> bool:
    for part in relative_path.parts:
        if part in PACKAGE_EXCLUDES:
            return True
        if part.endswith(".pyc"):
            return True
    return False


def _content_class_for(relative_path: Path) -> str:
    top_level = relative_path.parts[0]
    if top_level in RUNTIME_TOP_LEVEL or relative_path.as_posix() in RUNTIME_ROOT_FILES:
        return CONTENT_RUNTIME
    if top_level in REFERENCE_TOP_LEVEL:
        return CONTENT_REFERENCE
    return CONTENT_REFERENCE


def _top_level_for(relative_path: Path) -> str:
    return relative_path.parts[0] if len(relative_path.parts) > 1 else "(root)"


def _detect_content(file_path: Path) -> tuple[bytes, int, str]:
    data = file_path.read_bytes()
    try:
        data.decode("utf-8")
        return data, 1, "utf-8"
    except UnicodeDecodeError:
        return data, 0, "binary"


def _preview_text(data: bytes, is_text: int) -> str:
    if not is_text:
        return ""
    return data.decode("utf-8", errors="replace")[:2000]


def _guess_mime(relative_path: Path, is_text: int) -> str:
    mime, _ = mimetypes.guess_type(relative_path.name)
    if mime:
        return mime
    return "text/plain" if is_text else "application/octet-stream"


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _aggregate_hash(entries: Iterable[dict[str, Any]]) -> str:
    hasher = hashlib.sha256()
    for entry in entries:
        row = "|".join(
            [
                entry["relative_path"],
                entry["content_class"],
                entry["content_hash"],
                str(entry["byte_size"]),
                str(entry["is_text"]),
                str(entry["executable"]),
            ]
        )
        hasher.update(row.encode("utf-8"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def _onboarding_rows() -> list[tuple[int, str, str]]:
    return [
        (
            1,
            "Read the manifest",
            "Start with the embedded manifest_json or the on-disk builderset_authority_manifest.json to learn the build_id, entrypoints, and content classes.",
        ),
        (
            2,
            "Hydrate runtime",
            "Use builderset_authority_prepare_runtime before invoking BuilderSET code. It extracts only runtime_executable files into a cache keyed by build_id.",
        ),
        (
            3,
            "Use MCP first",
            "Primary packed entrypoint is src/mcp/server.py from the hydrated cache. UI remains optional and is launched from src/app.py ui when needed.",
        ),
        (
            4,
            "Query without extracting",
            "Use builderset_authority_manifest and builderset_authority_query to inspect the codex directly from SQLite without materializing reference data.",
        ),
        (
            5,
            "Export deliberately",
            "Reference-only content is preserved in the DB and should be exported on demand instead of copied wholesale into the runtime cache.",
        ),
    ]


def _clear_authority_tables(connection: sqlite3.Connection) -> None:
    connection.execute("DELETE FROM authority_files")
    connection.execute("DELETE FROM authority_builds")
    connection.execute("DELETE FROM authority_onboarding")


def _prune_unreferenced_blobs(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        DELETE FROM authority_blobs
        WHERE content_hash NOT IN (
            SELECT DISTINCT content_hash FROM authority_files
        )
        """
    )


def _set_meta(connection: sqlite3.Connection, key: str, value: Any) -> None:
    connection.execute(
        "INSERT OR REPLACE INTO authority_meta(key, value) VALUES(?, ?)",
        (key, json.dumps(value) if not isinstance(value, str) else value),
    )


def _runtime_pointer_path(cache_root: Path, build_id: str) -> Path:
    return cache_root / f"{build_id}.runtime_pointer.json"


def _read_runtime_pointer(cache_root: Path, build_id: str) -> Path | None:
    pointer_path = _runtime_pointer_path(cache_root, build_id)
    if not pointer_path.exists():
        return None
    try:
        payload = json.loads(pointer_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    cache_dir = payload.get("cache_dir", "")
    if not cache_dir:
        return None
    resolved = Path(cache_dir)
    if not resolved.exists():
        return None
    return resolved


def _write_runtime_pointer(cache_root: Path, build_id: str, cache_dir: Path) -> None:
    write_json(
        _runtime_pointer_path(cache_root, build_id),
        {
            "build_id": build_id,
            "cache_dir": str(cache_dir),
            "updated_at": now_stamp(),
        },
    )


def _sqlite_user_version(connection: sqlite3.Connection) -> int:
    row = connection.execute("PRAGMA user_version").fetchone()
    if row is None:
        return 0
    return int(row[0])


def _manifest_payload(
    *,
    build_id: str,
    built_at: str,
    source_root: Path,
    git_meta: dict[str, str],
    file_count: int,
    runtime_file_count: int,
    reference_file_count: int,
    content_hash: str,
    runtime_hash: str,
    reference_hash: str,
    output_db_path: Path,
    cache_root: Path,
) -> dict[str, Any]:
    return {
        "manifest_version": "1.0",
        "authority_name": AUTHORITY_LABEL,
        "schema_version": AUTHORITY_SCHEMA_VERSION,
        "status": "active",
        "description": "Toolbox-resident packed authority for the AgenticToolboxBuilderSET codex.",
        "build": {
            "build_id": build_id,
            "built_at": built_at,
            "source_root": str(source_root),
            "source_branch": git_meta["branch"],
            "source_commit": git_meta["commit"],
            "content_hash": content_hash,
            "runtime_hash": runtime_hash,
            "reference_hash": reference_hash,
        },
        "artifact": {
            "db_path": str(output_db_path),
            "db_name": output_db_path.name,
            "cache_root": str(cache_root),
        },
        "content_classes": {
            CONTENT_RUNTIME: {
                "description": "Files required to run packed BuilderSET surfaces from the hydrated cache.",
                "default_materialization": True,
                "includes": sorted(RUNTIME_TOP_LEVEL | set(RUNTIME_ROOT_FILES)),
            },
            CONTENT_REFERENCE: {
                "description": "Searchable/exportable codex material preserved in the DB but not hydrated by default.",
                "default_materialization": False,
                "includes": sorted(REFERENCE_TOP_LEVEL),
            },
        },
        "entrypoints": {
            "mcp": "src/mcp/server.py",
            "ui": "src/app.py ui",
            "catalog_probe": "src/app.py catalog",
        },
        "counts": {
            "files_total": file_count,
            "runtime_files": runtime_file_count,
            "reference_files": reference_file_count,
        },
        "agent_onboarding": [
            {"step_number": number, "title": title, "body": body}
            for number, title, body in _onboarding_rows()
        ],
    }


def build_builderset_authority(
    *,
    source_project_root: str | Path | None = None,
    output_db: str | Path | None = None,
    output_manifest: str | Path | None = None,
) -> dict[str, Any]:
    if source_project_root:
        source_root = Path(source_project_root).resolve()
    else:
        auto = source_project_root_from_here()
        if auto is None:
            raise ValueError(
                "Cannot auto-detect the project root. "
                "This .dev-tools appears to be the canonical source copy, not a vendored install. "
                "Pass source_project_root explicitly to specify which project to pack."
            )
        source_root = auto
    output_db_path = Path(output_db).resolve() if output_db else default_output_db_path()
    output_manifest_path = Path(output_manifest).resolve() if output_manifest else default_output_manifest_path()
    cache_root = default_runtime_cache_root()
    git_meta = _git_metadata(source_root)
    built_at = now_stamp()

    output_db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = _connect(output_db_path)
    try:
        _initialize_schema(connection)
        _clear_authority_tables(connection)
        packed_rows: list[dict[str, Any]] = []

        for file_path in sorted(source_root.rglob("*")):
            if not file_path.is_file():
                continue
            relative_path = file_path.relative_to(source_root)
            if _is_excluded(relative_path):
                continue

            # Skip files that exceed the BLOB size cap
            file_size = file_path.stat().st_size
            if file_size > MAX_BLOB_BYTES:
                continue

            data, is_text, content_encoding = _detect_content(file_path)
            content_hash = _hash_bytes(data)
            byte_size = len(data)
            executable = 1 if os.access(file_path, os.X_OK) else 0
            content_class = _content_class_for(relative_path)
            top_level = _top_level_for(relative_path)
            mime_type = _guess_mime(relative_path, is_text)
            preview_text = _preview_text(data, is_text)
            notes = {
                "source_relative_path": relative_path.as_posix(),
                "content_encoding": content_encoding,
            }

            connection.execute(
                """
                INSERT OR REPLACE INTO authority_blobs(
                    content_hash, content, byte_size, content_encoding, mime_type, preview_text
                ) VALUES(?, ?, ?, ?, ?, ?)
                """,
                (content_hash, sqlite3.Binary(data), byte_size, content_encoding, mime_type, preview_text),
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO authority_files(
                    relative_path, top_level, content_hash, content_class, mime_type,
                    byte_size, is_text, executable, source_mtime, notes_json
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relative_path.as_posix(),
                    top_level,
                    content_hash,
                    content_class,
                    mime_type,
                    byte_size,
                    is_text,
                    executable,
                    str(int(file_path.stat().st_mtime)),
                    json.dumps(notes, sort_keys=True),
                ),
            )
            packed_rows.append(
                {
                    "relative_path": relative_path.as_posix(),
                    "content_class": content_class,
                    "content_hash": content_hash,
                    "byte_size": byte_size,
                    "is_text": is_text,
                    "executable": executable,
                }
            )

        runtime_rows = [row for row in packed_rows if row["content_class"] == CONTENT_RUNTIME]
        reference_rows = [row for row in packed_rows if row["content_class"] == CONTENT_REFERENCE]
        content_hash = _aggregate_hash(packed_rows)
        runtime_hash = _aggregate_hash(runtime_rows)
        reference_hash = _aggregate_hash(reference_rows)
        build_id = content_hash[:16]

        manifest = _manifest_payload(
            build_id=build_id,
            built_at=built_at,
            source_root=source_root,
            git_meta=git_meta,
            file_count=len(packed_rows),
            runtime_file_count=len(runtime_rows),
            reference_file_count=len(reference_rows),
            content_hash=content_hash,
            runtime_hash=runtime_hash,
            reference_hash=reference_hash,
            output_db_path=output_db_path,
            cache_root=cache_root,
        )

        connection.execute(
            """
            INSERT OR REPLACE INTO authority_builds(
                build_id, built_at, source_root, source_branch, source_commit, content_hash,
                runtime_hash, reference_hash, file_count, runtime_file_count, reference_file_count,
                manifest_json
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                build_id,
                built_at,
                str(source_root),
                git_meta["branch"],
                git_meta["commit"],
                content_hash,
                runtime_hash,
                reference_hash,
                len(packed_rows),
                len(runtime_rows),
                len(reference_rows),
                json.dumps(manifest, sort_keys=True),
            ),
        )
        for row in _onboarding_rows():
            connection.execute(
                "INSERT OR REPLACE INTO authority_onboarding(step_number, title, body) VALUES(?, ?, ?)",
                row,
            )
        _prune_unreferenced_blobs(connection)
        _set_meta(connection, "authority_name", AUTHORITY_LABEL)
        _set_meta(connection, "schema_version", AUTHORITY_SCHEMA_VERSION)
        _set_meta(connection, "current_build_id", build_id)
        _set_meta(connection, "current_manifest_json", manifest)
        _set_meta(connection, "runtime_cache_root", str(cache_root))
        _set_meta(connection, "source_project_root", str(source_root))
        _set_meta(connection, "source_branch", git_meta["branch"])
        _set_meta(connection, "source_commit", git_meta["commit"])
        _set_meta(connection, "built_at", built_at)
        connection.commit()
    finally:
        connection.close()

    write_json(output_manifest_path, manifest)
    return {
        "authority_root": str(authority_root_from_here()),
        "source_project_root": str(source_root),
        "authority_db_path": str(output_db_path),
        "authority_manifest_path": str(output_manifest_path),
        "build_id": build_id,
        "counts": manifest["counts"],
        "entrypoints": manifest["entrypoints"],
        "git": {
            "branch": git_meta["branch"],
            "commit": git_meta["commit"],
        },
    }


def _load_manifest(connection: sqlite3.Connection) -> dict[str, Any]:
    row = connection.execute(
        "SELECT manifest_json FROM authority_builds ORDER BY built_at DESC LIMIT 1"
    ).fetchone()
    if row is None:
        raise ValueError("BuilderSET authority has not been built yet.")
    return json.loads(row["manifest_json"])


def inspect_builderset_authority(*, db_path: str | Path | None = None) -> dict[str, Any]:
    resolved_db_path = Path(db_path).resolve() if db_path else default_output_db_path()
    connection = _connect(resolved_db_path)
    try:
        manifest = _load_manifest(connection)
        user_version = _sqlite_user_version(connection)
        rows = connection.execute(
            """
            SELECT content_class, COUNT(*) AS file_count, COALESCE(SUM(byte_size), 0) AS byte_count
            FROM authority_files
            GROUP BY content_class
            ORDER BY content_class
            """
        ).fetchall()
        onboarding = connection.execute(
            "SELECT step_number, title, body FROM authority_onboarding ORDER BY step_number"
        ).fetchall()
        file_count = connection.execute("SELECT COUNT(*) AS count FROM authority_files").fetchone()["count"]
        blob_count = connection.execute("SELECT COUNT(*) AS count FROM authority_blobs").fetchone()["count"]
        return {
            "db_path": str(resolved_db_path),
            "manifest": manifest,
            "db_summary": {
                "schema_version": AUTHORITY_SCHEMA_VERSION,
                "sqlite_user_version": user_version,
                "file_count": file_count,
                "blob_count": blob_count,
                "content_classes": [
                    {
                        "content_class": row["content_class"],
                        "file_count": row["file_count"],
                        "byte_count": row["byte_count"],
                    }
                    for row in rows
                ],
            },
            "onboarding": [
                {
                    "step_number": row["step_number"],
                    "title": row["title"],
                    "body": row["body"],
                }
                for row in onboarding
            ],
        }
    finally:
        connection.close()


def query_builderset_authority(
    *,
    db_path: str | Path | None = None,
    content_class: str | None = None,
    top_level: str | None = None,
    path_contains: str | None = None,
    limit: int = 50,
    include_preview: bool = False,
) -> dict[str, Any]:
    resolved_db_path = Path(db_path).resolve() if db_path else default_output_db_path()
    connection = _connect(resolved_db_path)
    try:
        clauses: list[str] = []
        params: list[Any] = []
        if content_class:
            clauses.append("f.content_class = ?")
            params.append(content_class)
        if top_level:
            clauses.append("f.top_level = ?")
            params.append(top_level)
        if path_contains:
            clauses.append("f.relative_path LIKE ?")
            params.append(f"%{path_contains}%")

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        select_preview = ", b.preview_text" if include_preview else ""
        rows = connection.execute(
            f"""
            SELECT f.relative_path, f.top_level, f.content_class, f.mime_type, f.byte_size, f.is_text, f.executable
            {select_preview}
            FROM authority_files AS f
            LEFT JOIN authority_blobs AS b ON b.content_hash = f.content_hash
            {where_sql}
            ORDER BY f.relative_path
            LIMIT ?
            """,
            [*params, limit],
        ).fetchall()
        return {
            "db_path": str(resolved_db_path),
            "filters": {
                "content_class": content_class or "",
                "top_level": top_level or "",
                "path_contains": path_contains or "",
                "limit": limit,
            },
            "matches": [
                {
                    "relative_path": row["relative_path"],
                    "top_level": row["top_level"],
                    "content_class": row["content_class"],
                    "mime_type": row["mime_type"],
                    "byte_size": row["byte_size"],
                    "is_text": bool(row["is_text"]),
                    "executable": bool(row["executable"]),
                    **({"preview_text": row["preview_text"]} if include_preview else {}),
                }
                for row in rows
            ],
        }
    finally:
        connection.close()


def _current_build_id(connection: sqlite3.Connection) -> str:
    row = connection.execute(
        "SELECT value FROM authority_meta WHERE key = 'current_build_id'"
    ).fetchone()
    if row is None:
        raise ValueError("BuilderSET authority has no current_build_id. Run a build first.")
    return row["value"]


def prepare_builderset_runtime(
    *,
    db_path: str | Path | None = None,
    cache_root: str | Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    resolved_db_path = Path(db_path).resolve() if db_path else default_output_db_path()
    resolved_cache_root = Path(cache_root).resolve() if cache_root else default_runtime_cache_root()
    resolved_cache_root.mkdir(parents=True, exist_ok=True)
    connection = _connect(resolved_db_path)
    try:
        manifest = _load_manifest(connection)
        build_id = _current_build_id(connection)
        primary_cache_dir = resolved_cache_root / build_id
        active_cache_dir = _read_runtime_pointer(resolved_cache_root, build_id) or primary_cache_dir
        runtime_manifest_path = active_cache_dir / "builderset_runtime_manifest.json"

        reused = active_cache_dir.exists() and runtime_manifest_path.exists() and not force
        if reused:
            return {
                "db_path": str(resolved_db_path),
                "cache_root": str(resolved_cache_root),
                "cache_dir": str(active_cache_dir),
                "build_id": build_id,
                "reused": True,
                "runtime_file_count": manifest["counts"]["runtime_files"],
                "entrypoints": manifest["entrypoints"],
                "cache_strategy": "pointer_reuse" if active_cache_dir != primary_cache_dir else "primary_reuse",
            }

        if force:
            if primary_cache_dir.exists():
                refresh_token = now_stamp().replace(":", "").replace("-", "")
                target_cache_dir = resolved_cache_root / f"{build_id}.__refresh__.{refresh_token}"
            else:
                target_cache_dir = primary_cache_dir
        else:
            target_cache_dir = primary_cache_dir

        if target_cache_dir.exists():
            shutil.rmtree(target_cache_dir)
        target_cache_dir.mkdir(parents=True, exist_ok=True)

        rows = connection.execute(
            """
            SELECT f.relative_path, f.executable, b.content
            FROM authority_files AS f
            JOIN authority_blobs AS b ON b.content_hash = f.content_hash
            WHERE f.content_class = ?
            ORDER BY f.relative_path
            """,
            (CONTENT_RUNTIME,),
        ).fetchall()
        for row in rows:
            target_path = target_cache_dir / row["relative_path"]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(row["content"])
            if row["executable"]:
                target_path.chmod(target_path.stat().st_mode | stat.S_IEXEC)

        runtime_manifest = {
            "authority_name": AUTHORITY_LABEL,
            "build_id": build_id,
            "hydrated_at": now_stamp(),
            "db_path": str(resolved_db_path),
            "entrypoints": manifest["entrypoints"],
            "source_commit": manifest["build"]["source_commit"],
            "source_branch": manifest["build"]["source_branch"],
        }
        write_json(target_cache_dir / "builderset_runtime_manifest.json", runtime_manifest)
        _write_runtime_pointer(resolved_cache_root, build_id, target_cache_dir)
        return {
            "db_path": str(resolved_db_path),
            "cache_root": str(resolved_cache_root),
            "cache_dir": str(target_cache_dir),
            "build_id": build_id,
            "reused": False,
            "runtime_file_count": manifest["counts"]["runtime_files"],
            "entrypoints": manifest["entrypoints"],
            "cache_strategy": (
                "forced_sidecar_refresh"
                if force and target_cache_dir != primary_cache_dir
                else ("forced_primary_refresh" if force else "primary_hydrate")
            ),
        }
    finally:
        connection.close()


def export_builderset_content(
    *,
    destination_root: str | Path,
    db_path: str | Path | None = None,
    content_class: str | None = None,
    relative_paths: list[str] | None = None,
    relative_path_prefix: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    resolved_db_path = Path(db_path).resolve() if db_path else default_output_db_path()
    resolved_destination = Path(destination_root).resolve()
    connection = _connect(resolved_db_path)
    try:
        clauses: list[str] = []
        params: list[Any] = []
        if content_class:
            clauses.append("f.content_class = ?")
            params.append(content_class)
        if relative_path_prefix:
            clauses.append("f.relative_path LIKE ?")
            params.append(f"{relative_path_prefix}%")
        if relative_paths:
            placeholders = ", ".join(["?"] * len(relative_paths))
            clauses.append(f"f.relative_path IN ({placeholders})")
            params.extend(relative_paths)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        rows = connection.execute(
            f"""
            SELECT f.relative_path, b.content
            FROM authority_files AS f
            JOIN authority_blobs AS b ON b.content_hash = f.content_hash
            {where_sql}
            ORDER BY f.relative_path
            """,
            params,
        ).fetchall()
        if not rows:
            raise ValueError("No BuilderSET authority files matched the export request.")

        written = []
        for row in rows:
            target_path = resolved_destination / row["relative_path"]
            if target_path.exists() and not overwrite:
                written.append({"path": str(target_path), "status": "skipped"})
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(row["content"])
            written.append({"path": str(target_path), "status": "written"})
        return {
            "db_path": str(resolved_db_path),
            "destination_root": str(resolved_destination),
            "files": written,
            "matched_count": len(rows),
        }
    finally:
        connection.close()


def describe_builderset_launch(
    *,
    db_path: str | Path | None = None,
    cache_root: str | Path | None = None,
    surface: str = "mcp",
    python_executable: str | None = None,
) -> dict[str, Any]:
    runtime = prepare_builderset_runtime(db_path=db_path, cache_root=cache_root)
    runtime_root = Path(runtime["cache_dir"])
    python_path = python_executable or sys.executable
    if surface == "mcp":
        entrypoint = runtime_root / "src" / "mcp" / "server.py"
        command = [python_path, str(entrypoint)]
    elif surface == "ui":
        entrypoint = runtime_root / "src" / "app.py"
        command = [python_path, str(entrypoint), "ui"]
    elif surface == "catalog":
        entrypoint = runtime_root / "src" / "app.py"
        command = [python_path, str(entrypoint), "catalog"]
    else:
        raise ValueError("surface must be one of: mcp, ui, catalog")
    return {
        "surface": surface,
        "entrypoint": str(entrypoint),
        "command": command,
        "runtime": runtime,
    }


def _mcp_message(message: dict[str, Any]) -> bytes:
    body = json.dumps(message).encode("utf-8")
    return body + b"\n"


def _mcp_read_content_length(stdout, first_line: bytes) -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    line = first_line
    while True:
        if not line:
            return None
        if line in {b"\r\n", b"\n"}:
            break
        key, _, value = line.decode("utf-8").partition(":")
        headers[key.strip().lower()] = value.strip()
        line = stdout.readline()
    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None
    body = stdout.read(content_length)
    if not body:
        return None
    return json.loads(body.decode("utf-8"))


def _mcp_read(stdout) -> dict[str, Any]:
    while True:
        line = stdout.readline()
        if not line:
            raise RuntimeError("Packed MCP server closed before responding.")
        stripped = line.strip()
        if not stripped:
            continue
        if b"content-length" in stripped.lower():
            payload = _mcp_read_content_length(stdout, line)
            if payload is None:
                continue
            return payload
        return json.loads(stripped.decode("utf-8"))


def _mcp_read_response(stdout, message_id: int) -> dict[str, Any]:
    while True:
        payload = _mcp_read(stdout)
        if payload.get("id") == message_id:
            return payload


def probe_builderset_surface(
    *,
    db_path: str | Path | None = None,
    cache_root: str | Path | None = None,
    surface: str = "mcp",
    python_executable: str | None = None,
) -> dict[str, Any]:
    launch = describe_builderset_launch(
        db_path=db_path,
        cache_root=cache_root,
        surface="mcp" if surface == "mcp" else "catalog",
        python_executable=python_executable,
    )
    runtime_root = Path(launch["runtime"]["cache_dir"])
    python_path = python_executable or sys.executable

    if surface == "mcp":
        proc = subprocess.Popen(
            launch["command"],
            cwd=str(runtime_root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            assert proc.stdin is not None and proc.stdout is not None
            proc.stdin.write(
                _mcp_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "builderset-authority-probe", "version": "1.0"},
                        },
                    }
                )
            )
            proc.stdin.flush()
            init_response = _mcp_read_response(proc.stdout, 1)
            proc.stdin.write(
                _mcp_message({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            )
            proc.stdin.flush()
            proc.stdin.write(_mcp_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
            proc.stdin.flush()
            tools_response = _mcp_read_response(proc.stdout, 2)
            return {
                "surface": "mcp",
                "runtime_root": str(runtime_root),
                "server_info": init_response.get("result", {}).get("serverInfo", {}),
                "tool_names": sorted(
                    tool["name"] for tool in tools_response.get("result", {}).get("tools", [])
                ),
            }
        finally:
            proc.kill()
            proc.wait(timeout=5)

    if surface == "ui":
        command = [
            python_path,
            "-c",
            (
                "import sys; "
                f"sys.path.insert(0, r'{runtime_root}'); "
                "from src.ui.main_gui import launch; "
                "print('ui_import_ok')"
            ),
        ]
        completed = subprocess.run(
            command,
            cwd=str(runtime_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or completed.stdout or "UI import probe failed.")
        return {
            "surface": "ui",
            "runtime_root": str(runtime_root),
            "probe": completed.stdout.strip(),
        }

    if surface == "catalog":
        command = [python_path, str(runtime_root / "src" / "app.py"), "catalog"]
        completed = subprocess.run(
            command,
            cwd=str(runtime_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or completed.stdout or "Catalog probe failed.")
        return {
            "surface": "catalog",
            "runtime_root": str(runtime_root),
            "stdout": completed.stdout.strip(),
        }

    raise ValueError("surface must be one of: mcp, ui, catalog")
