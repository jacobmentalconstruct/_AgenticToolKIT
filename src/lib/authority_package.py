"""
FILE: authority_package.py
ROLE: Build/install helpers for the vendored authority kit.
WHAT IT DOES: Builds authority.sqlite3 from the source project and installs a
    thin _project-authority shim into target projects.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from contextlib import closing
from pathlib import Path
from typing import Any

from common import now_stamp, read_json, write_json
from lib.journal_store import _connect, initialize_store
from lib.scaffolds import list_templates, seed_templates
from lib.tool_pack import pack_package


AUTHORITY_DB_NAME = "authority.sqlite3"
SHIM_FOLDER_NAME = "_project-authority"
SHIM_SOURCE_DIRNAME = "shim"
BUILD_EXCLUDE = {
    "__pycache__",
    ".pyc",
    ".pyo",
    ".git",
    ".venv",
    "_parts",
    "_docs",
    AUTHORITY_DB_NAME,
    "runtime",
}
SHIM_FILES = [
    "common.py",
    "bootstrap.py",
    "mcp_server.py",
    "launch_ui.py",
    "tool_manifest.json",
    AUTHORITY_DB_NAME,
]


def _portable_db_manifest() -> dict[str, Any]:
    return {
        "db_manifest_version": "2.0",
        "schema_version": "2.0.0",
        "sqlite_user_version": 2,
        "package_name": "project-authority",
        "package_manifest_version": "2.0",
        "package_status": "active",
        "package_description": "DB-packed project authority kit with exported starter docs and additive scaffold support.",
        "db_schema": {
            "table_names": [
                "journal_meta",
                "journal_migrations",
                "journal_entries",
                "blob_store",
                "scaffold_templates",
                "packed_tools",
                "action_log",
                "snapshots",
                "snapshot_items",
                "project_registry",
            ],
            "entry_primary_id": "entry_uid",
            "metadata_store": "journal_meta",
            "migration_store": "journal_migrations",
            "content_store": "blob_store",
            "schema_version": "2.0.0",
        },
        "project_convention": {
            "project_root": "{{PROJECT_ROOT}}",
            "db_path": "_docs/_journalDB/app_journal.sqlite3",
            "app_dir": "_docs/_AppJOURNAL",
            "exports_dir": "_docs/_AppJOURNAL/exports",
        },
        "agent_entrypoints": {
            "mcp": "src/mcp_server.py",
            "cli_tools": [
                "src/tools/journal_init.py",
                "src/tools/journal_write.py",
                "src/tools/journal_query.py",
                "src/tools/journal_export.py",
                "src/tools/journal_manifest.py",
                "src/tools/journal_acknowledge.py",
                "src/tools/journal_actions.py",
                "src/tools/journal_scaffold.py",
                "src/tools/journal_pack.py",
                "src/tools/journal_snapshot.py",
                "src/tools/authority_build.py",
                "src/tools/authority_install.py",
            ],
        },
    }


def _sanitize_authority_store(connection) -> None:
    connection.execute("DELETE FROM action_log")
    connection.execute("DELETE FROM project_registry")
    connection.execute("DELETE FROM snapshot_items")
    connection.execute("DELETE FROM snapshots")
    connection.execute("DELETE FROM journal_entries WHERE kind <> 'contract'")
    connection.execute("UPDATE journal_entries SET project_id = ''")
    connection.execute(
        "INSERT OR REPLACE INTO journal_meta(key, value) VALUES(?, ?)",
        ("project_root", "{{PROJECT_ROOT}}"),
    )
    connection.execute(
        "INSERT OR REPLACE INTO journal_meta(key, value) VALUES(?, ?)",
        ("db_manifest_json", json.dumps(_portable_db_manifest(), sort_keys=True)),
    )


def package_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def build_authority_package(
    package_root: str | Path | None = None,
    *,
    output_db: str | Path | None = None,
) -> dict[str, Any]:
    package_root_path = Path(package_root).resolve() if package_root else package_root_from_here()
    output_db_path = Path(output_db).resolve() if output_db else package_root_path / AUTHORITY_DB_NAME

    with tempfile.TemporaryDirectory(prefix="authority_build_") as temp_dir_str:
        temp_project_root = Path(temp_dir_str) / "packaging_context"
        temp_project_root.mkdir(parents=True, exist_ok=True)
        paths = initialize_store(project_root=temp_project_root)

        with closing(_connect(paths["db_path"])) as connection:
            templates_seeded = seed_templates(connection)
            templates_available = len(list_templates(connection))
            packed = pack_package(
                connection,
                package_root_path,
                exclude_patterns=BUILD_EXCLUDE,
            )
            connection.execute(
                "INSERT OR REPLACE INTO journal_meta(key, value) VALUES(?, ?)",
                ("authority_package_db_name", AUTHORITY_DB_NAME),
            )
            connection.execute(
                "INSERT OR REPLACE INTO journal_meta(key, value) VALUES(?, ?)",
                ("authority_package_built_at", now_stamp()),
            )
            connection.execute(
                "INSERT OR REPLACE INTO journal_meta(key, value) VALUES(?, ?)",
                ("authority_shim_dir_name", SHIM_FOLDER_NAME),
            )
            _sanitize_authority_store(connection)
            connection.commit()

        output_db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths["db_path"], output_db_path)
        return {
            "package_root": str(package_root_path),
            "working_db_path": paths["db_path"],
            "authority_db_path": str(output_db_path),
            "templates_seeded": templates_seeded,
            "templates_available": templates_available,
            "packed_count": packed["packed_count"],
            "packed_files": packed["files"],
        }


def _installed_manifest(source_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_version": source_manifest.get("manifest_version", "2.0"),
        "name": "project-authority",
        "description": "Thin vendored shim for the DB-packed Project Authority Kit.",
        "portable_project": True,
        "isolated_folder": True,
        "status": "active",
        "vendoring": {
            "mode": "installed_thin_shim",
            "shim_dir": f".dev-tools/{SHIM_FOLDER_NAME}",
            "shim_files": SHIM_FILES,
            "packed_db": AUTHORITY_DB_NAME,
            "consumer_rule": "Run bootstrap.py or mcp_server.py from the shim to unpack runtime files on demand.",
        },
        "mcp_entrypoint": "mcp_server.py",
        "ui_entrypoint": "launch_ui.py",
        "bootstrap_entrypoint": "bootstrap.py",
        "self_test_entrypoint": "",
    }


def install_authority_shim(
    target_project_root: str | Path,
    *,
    package_root: str | Path | None = None,
    overwrite: bool = False,
    preview: bool = False,
) -> dict[str, Any]:
    package_root_path = Path(package_root).resolve() if package_root else package_root_from_here()
    build_summary = build_authority_package(package_root_path)
    target_root = Path(target_project_root).resolve()
    shim_dir = target_root / ".dev-tools" / SHIM_FOLDER_NAME
    shim_source_dir = package_root_path / "src" / SHIM_SOURCE_DIRNAME
    source_manifest = read_json(package_root_path / "tool_manifest.json")

    files_to_write = {
        "common.py": shim_source_dir / "common.py",
        "bootstrap.py": shim_source_dir / "bootstrap.py",
        "mcp_server.py": shim_source_dir / "mcp_server.py",
        "launch_ui.py": shim_source_dir / "launch_ui.py",
        AUTHORITY_DB_NAME: Path(build_summary["authority_db_path"]),
    }
    results = []

    if not preview:
        shim_dir.mkdir(parents=True, exist_ok=True)

    for relative_name, source_path in files_to_write.items():
        target_path = shim_dir / relative_name
        if target_path.exists() and not overwrite:
            results.append({"path": str(target_path), "status": "skipped"})
            continue
        if preview:
            results.append({"path": str(target_path), "status": "would_create"})
            continue
        shutil.copy2(source_path, target_path)
        results.append({"path": str(target_path), "status": "overwritten" if target_path.exists() and overwrite else "created"})

    manifest_path = shim_dir / "tool_manifest.json"
    manifest_status = "would_create" if preview else ("skipped" if manifest_path.exists() and not overwrite else "created")
    if preview:
        results.append({"path": str(manifest_path), "status": manifest_status})
    elif manifest_path.exists() and not overwrite:
        results.append({"path": str(manifest_path), "status": "skipped"})
    else:
        write_json(manifest_path, _installed_manifest(source_manifest))
        results.append({"path": str(manifest_path), "status": manifest_status})

    return {
        "package_root": str(package_root_path),
        "target_project_root": str(target_root),
        "shim_dir": str(shim_dir),
        "preview": preview,
        "files": results,
        "build_summary": build_summary,
    }
