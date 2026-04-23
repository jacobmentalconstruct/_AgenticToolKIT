# _journalDB

This folder holds runtime-generated SQLite state for the source package.

The packed authority DB that is shipped to child projects is
`authority.sqlite3` at the package root. The working `app_journal.sqlite3`
file for the source package should be generated on demand and is not part of
the clean vendored source state.
