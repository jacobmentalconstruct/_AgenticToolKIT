# Setup Doctrine

_Last updated: 2026-04-29._

This document records the project-setup doctrine that `.dev-tools` expects a
freshly armed agent to follow when entering a new project.

The core rule is simple:

1. set up the project correctly,
2. read the builder constraint contract,
3. then proceed in loyalty to the project and the application being built,
   not in loyalty to short-term convenience or prompt momentum.

---

## First Principle

When an agent is first pointed at a new project and armed with `.dev-tools`, it
must not begin by improvising features.

It must first establish the project scaffold, continuity packet, and trust
boundaries. Only after that should it read the builder constraint contract and
bind itself to the project's long-term structural health.

The operative loyalty is:

- to the project root,
- to the application being born there,
- to the builder constraint contract,
- and to the vendorable, self-contained future of the app.

It is not loyalty to:

- surface-level haste,
- user convenience that contradicts the contract,
- or accidental shortcuts that weaken the app.

---

## Required Setup Sequence

### 1. Establish the project root

- Confirm the active project folder.
- Confirm all writes stay inside project root unless explicitly authorized.
- Confirm the project is vendorable and self-contained.
- Confirm no runtime dependency on sibling folders, `.parts`, `.dev-tools`, or
  external local repos.

### 2. Create the required root scaffold

Required baseline surfaces:

- `src/app.py`
- `src/core/`
- `src/ui/`
- `README.md`
- `LICENSE.md`
- `requirements.txt`
- `setup_env.bat`
- `run.bat`
- `_docs/`
- `tests/`

### 3. Create the core package scaffold

At minimum, a new project should establish clear core ownership areas such as:

- `src/core/config/`
- `src/core/logging/`
- `src/core/coordination/`
- `src/core/representation/`
- `src/core/persistence/`
- `src/core/transformation/`
- `src/core/analysis/`
- `src/core/execution/`

Use `__init__.py` files where package boundaries need to be explicit.

### 4. Create the composition root

`src/app.py` should own:

- CLI entry
- settings load
- logging setup
- engine creation
- `status`
- clear exit codes

### 5. Create the config owner

Define the settings authority explicitly:

- `project_root`
- `docs_root`
- `data_root`
- environment override only when intentional
- project-local path discipline

### 6. Create the logging owner

Logging should be intentional from the start:

- add `configure_logging()`
- use Python logging, not ad hoc `print()`
- keep CLI JSON output separate from logs
- do not create a heavier event spine unless authorized

### 7. Create the engine/status owner

Establish a machine-readable status surface early:

- `ApplicationEngine`
- `SystemStatus`
- `status`
- `project_root`
- `active_tranche`
- `next_tranche`

`status --dump-json` should be readable by both humans and agents.

### 8. Create the required project docs

Required continuity packet:

- `_docs/builder_constraint_contract.md`
- `_docs/PROJECT_STATUS.md` or the local equivalent current-state surface
- `_docs/TODO.md`
- `_docs/THOUGHTS_FOR_NEXT_SESSION.md` or the local equivalent handoff note

Conditionally required when the project grows into them:

- `_docs/ARCHITECTURE.md`
- `_docs/TOOLS.md`
- `_docs/EXPERIENTIAL_WORKFLOW.md`
- `_docs/MCP_SEAM.md`

Keep docs purposeful, not decorative.

### 9. Create the app journal store

Create:

- `_docs/_journalDB/`
- `_docs/_journalDB/app_journal.sqlite3`

The journal is authoritative builder memory, not a decorative sidecar.

### 10. Define the journal doctrine

- Journal is authoritative builder memory.
- Generated mirrors are not canonical truth.
- Entries are append-only.
- Meaningful phases require a journal entry.
- Deferred work belongs in journal/TODO, not chat memory.

### 11. Create initial tests and scripts

At minimum, verify:

- required root files exist
- core packages exist
- `status` works
- the next-tranche/status surfaces are readable
- local setup/run scripts are simple and inspectable

### 12. Run setup verification

Typical setup verification includes:

- `python -m compileall src tests`
- `python -m unittest discover -s tests`
- `python -m src.app status`
- `python -m src.app status --dump-json`
- any local dev-log export or journal export path, if present

### 13. Park the setup tranche

Before feature work begins:

- update setup/status docs
- update TODO/backlog
- write append-only journal entry
- regenerate mirrors if the project uses them
- re-run final verification
- name the next tranche clearly

---

## Non-Negotiable Setup Boundaries

- no hidden external runtime dependencies
- no undeclared runtime coupling to `.dev-tools`
- no generated mirror treated as canonical truth
- no print-based operational logging
- no broad dashboard/server/network layer unless authorized
- no hidden app-state ingestion into semantic truth by default

---

## Relationship To The Contract

Setup comes before meaningful implementation.

But once setup exists, the builder constraint contract becomes the governing
discipline. From that point forward, the builder should interpret requests in
service of the app's structural health and contract compliance, not in service
of momentary expedience.
