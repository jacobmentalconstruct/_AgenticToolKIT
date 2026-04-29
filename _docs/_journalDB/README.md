# _journalDB

This folder holds runtime-generated SQLite state for the toolbox's own
journal. The working `app_journal.sqlite3` file is generated on demand by
`journal_init` and is gitignored — it is not part of the clean vendored
source state and is not shipped by the sidecar installer.

The authoritative human-readable project log is `_docs/DEV_LOG.md`.
