# Dev Log

_Last updated: 2026-04-11. Journal mirror lives in
`_docs/_journalDB/app_journal.sqlite3`._

---

## How to use this log

- Append a new dated section for each meaningful work phase.
- Record what changed, why it changed, and any trust boundary that matters.
- Keep summaries concise but complete.
- Use the journal DB for durable machine-queryable memory; use this file for
  fast human scanning.

---

## 2026-03-28 — Initial project authority kit (v2.0.0)

- Built the core `_app-journal` package with 10 MCP tools, Tkinter UI, and
  SQLite-backed journal store.
- Established the tool contract pattern: `FILE_METADATA` + `run(arguments)` +
  `standard_main()` + CLI via `metadata`/`run --input-json`.
- Seeded builder constraint contract, CAS blob store, action ledger, merkle
  snapshots.
- All 31 smoke tests passing at this point.

---

## 2026-04-02 — Intake cleanup: new builder tools

- Cleaned `_Possible_Intake` folder. Evaluated all candidates against existing
  tool surface.
- Packaged 4 new builder tools into `src/tools/`:
  - `module_decomp_planner` — AST-based module decomposition, groups defs by
    section headers, detects dependencies, scores extractability.
  - `tokenizing_patcher` — whitespace-immune hunk-based patcher using
    tokenization. Supports single-file, multi-target, and manifest modes.
  - `domain_boundary_audit` — AST-based domain boundary violation detector.
    Classifies imports into domains, flags functions crossing too many.
  - `scan_blocking_calls` — scans for `subprocess.run`, `time.sleep`,
    `os.system`, `urlopen`, etc. Supports custom `extra_blocking` patterns.
- Added `should_skip_dir()` and `DEFAULT_IGNORED_DIRS` to `src/common.py`.
- Registered all 4 in `tool_manifest.json` and `src/mcp_server.py`.
- Cleared `_Possible_Intake`.

---

## 2026-04-02 — Second intake dump: non-redundant tools extracted

- Received a second batch of loose files from a side branch.
- Found `domain_boundary_audit` and `scan_blocking_calls` as non-redundant
  additions (the first two had already been packaged).
- Cleared intake after extraction.

---

## 2026-04-11 — Three-tier architecture: vendable packages restored

- Identified that installable packages (`_app-journal`, `_manifold-mcp`,
  `_ollama-prompt-lab`) had drifted out of the canonical `.dev-tools` during
  earlier reorganizations.
- Designed and implemented three-tier toolbox architecture:
  - **Tier 1** (`src/tools/`) — builder tools that stay in the toolbox
  - **Tier 2** (`packages/`) — vendable packages installed INTO target projects
  - **Tier 3** (`templates/`) — vendable documents for cross-project reuse
- Copied all 3 packages from a prior project's `.claude/.dev-tools/`
  into `packages/`.
- Audited each for project-specific drift:
  - `_app-journal` — clean, no drift.
  - `_manifold-mcp` — 2 hardcoded absolute paths in example job files. Fixed
    to relative paths. Also upgraded `mcp_server.py` to support both
    Content-Length and NDJSON framing, and fixed `smoke_test.py` protocol
    mismatch.
  - `_ollama-prompt-lab` — clean, no drift.
- All 3 smoke tests passing.
- Created `toolbox_manifest.json` as the zero-context agent index for the
  three-tier layout.
- Updated `README.md`, `VENDORING.md` to reflect new architecture.
- Created `packages/README.md` and `templates/README.md`.
- Created this dev log.

Current state: 16 builder tools active, 3 vendable packages restored,
templates layer ready for content.

---

## 2026-04-11 — Builder Constraint Contract: vendable doc + atomic registry

- Received `_BuilderConstraintCONTRACT` folder via intake. Audited for
  project-specific drift: clean (only generic "sandbox" architectural
  concepts and proper author attribution). Fixed `LISCENSE.md` typo to
  `LICENSE.md`. Fixed duplicate section numbering (two 7.9s merged into
  7.9 + 7.10). Placed in `templates/_BuilderConstraintCONTRACT/`.
- Designed and built `_constraint-registry` vendable package:
  - Decomposed the 1,250-line BCC into 74 Atomic Constraint Units (ACUs)
  - Each ACU tagged with domain, severity (HARD_BLOCK/PUSHBACK/ADVISORY),
    and tier (spirit/letter/gate)
  - 8 pre-built task profiles: ui_implementation, core_implementation,
    refactoring, sourcing_extraction, documentation, cleanup,
    tool_creation, scaffolding
  - `registry_build` tool — builds the SQLite registry from seed data
  - `constraint_query` tool — queries by profile, domain, severity, tier,
    or specific UIDs
  - Full MCP server (NDJSON + Content-Length dual protocol)
  - 12/12 smoke tests passing
- Established clear separation: vendable registry (packages/_constraint-registry)
  vs full working contract (CONTRACT.md at .dev-tools root, never vended).
- Updated toolbox_manifest.json, packages/README.md, DEV_LOG.md.

Current state: 16 builder tools, 4 vendable packages, 1 vendable document
template. All smoke tests passing.

---

## 2026-04-11 — Three new builder tools: introspection quick wins

- Added `sqlite_schema_inspector` — reads any .sqlite3 file and returns
  structured schema: tables, columns, types, PKs, indexes, foreign keys,
  row counts, optional sample rows. Tested against `authority.sqlite3`
  (10 tables, full schema returned).
- Added `import_graph_mapper` — AST-based project import dependency graph.
  Classifies internal vs external imports, computes fan-in/fan-out per
  module, detects circular import chains. Tested against own `src/tools/`
  (19 modules scanned).
- Added `tkinter_widget_tree` — AST-based Tkinter widget hierarchy mapper.
  Extracts widgets, parent-child nesting, geometry manager calls,
  variable bindings, event bindings. Tested against `app_journal_ui.py`
  (12 widgets, tree structure, geometry calls all captured).
- All three registered in `tool_manifest.json` and `src/mcp_server.py`.
- All three follow the standard tool contract: `FILE_METADATA + run() +
  standard_main()`.

Current state: 19 builder tools, 4 vendable packages, 1 vendable document
template.

---

## 2026-04-11 — Prompt-lab reference pack and stale local toolbox purge

- Added a portable SQLite reference pack to
  `packages/_ollama-prompt-lab/artifacts/reference/`.
- Curated the pack from the canonical vendable package, not from stale hidden
  workspace residue.
- Fixed `packages/_ollama-prompt-lab/jobs/examples/rubric_eval.json`, which was
  missing its final closing brace and therefore was not valid JSON.
- Included:
  - canonical example jobs from `jobs/examples/`
  - all non-dry-run prompt-lab runs present in the vendable package at build
    time
  - onboarding rows, manifest rows, structured run tables, and raw artifact
    file payloads
- Updated `_ollama-prompt-lab/README.md`, `artifacts/README.md`, and
  `tool_manifest.json` so agents can discover the reference bundle without
  guessing.
- Purged the stale `.claude/.dev-tools` copy after packaging so the workspace
  no longer carries a shadow toolbox tree that can confuse audits or
  comparisons.
- Left `.claude/settings.local.json` unchanged because it did not reference the
  stale `.claude/.dev-tools` path and there was no obvious safe rewiring needed.

Current state: canonical prompt-lab data now lives in the updated vendable
package, and the stale hidden toolbox copy has been removed.

---

## 2026-04-11 — BuilderSET packed authority introduced

- Added a new toolbox-resident packed authority surface under
  `authorities/_builderset-authority/`.
- Implemented a dedicated BuilderSET authority library in
  `src/lib/builderset_authority.py`.
- The new authority stores the live BuilderSET codex in a separate SQLite
  artifact, distinct from the generic `authority.sqlite3`.
- Packaged content is split into two classes:
  - `runtime_executable` — BuilderSET runtime closure hydrated into
    `.dev-tools/runtime/_builderset-authority/<build_id>/`
  - `reference_only` — docs, smoke tests, finals, archives, outputs, and other
    codex material kept queryable/exportable without default hydration
- Added six builder tools for the packed authority lifecycle:
  - `builderset_authority_build`
  - `builderset_authority_manifest`
  - `builderset_authority_query`
  - `builderset_authority_prepare_runtime`
  - `builderset_authority_export`
  - `builderset_authority_launch`
- Registered the new tools in `src/mcp_server.py`, `tool_manifest.json`, and
  `toolbox_manifest.json`.
- Documented the new authority in `README.md` and `authorities/README.md`.

Current read: BuilderSET can now be packed into a toolbox-local SQLite
authority with managed runtime hydration instead of relying on the live repo as
the runtime surface.

---

## 2026-04-12 — Ollama prompt lab: 4 planned tools built

- Built all 4 planned tools for `_ollama-prompt-lab`, completing Phase 2+3
  of the package roadmap:
  - `prompt_case_builder` — combinatorial test case generation with edge-case
    seeding and default checks. Tested with 2-field x 2-value expansion
    (4 combos + 1 edge case).
  - `prompt_rubric_judge` — weighted rubric scoring via Ollama judge model.
    Loads outputs from prior runs or inline, pipes to judge, parses JSON
    scores, computes weighted averages.
  - `prompt_diff_report` — baseline vs candidate run comparison. Aligns by
    case+model, classifies as improved/regressed/unchanged, includes
    unified text diffs.
  - `agent_interview` — multi-turn scripted conversation with context
    history, per-turn checks, and automatic follow-up on failed checks.
- All 4 registered in tool_manifest.json and mcp_server.py (5 tools total).
- Promoted from planned_tools to active tools in manifest.
- Updated README.md and ROADMAP.md.

Current state: 19 builder tools, 4 vendable packages (prompt lab now has
5 tools), 1 vendable document template.

---

## 2026-04-13 — Six new builder tools: analysis, testing, introspection

- Added 6 new builder tools to `src/tools/`:
  - `file_tree_snapshot` — walks a project directory producing structured JSON
    tree with file sizes, line counts, timestamps, and optional Python
    docstrings. Respects `should_skip_dir`. Good for fast agent orientation.
  - `smoke_test_runner` — meta-runner that discovers and executes all
    `smoke_test.py` files across the toolbox and vendable packages.
    Aggregates pass/fail with timing, supports per-test timeouts and
    stop-on-failure.
  - `python_complexity_scorer` — scores Python functions by cyclomatic
    complexity, nesting depth, line count, and parameter count. Weighted
    composite score identifies decomposition targets for
    `module_decomp_planner`.
  - `dead_code_finder` — AST cross-references all definitions (functions,
    classes, imports) against usages across all files. Reports unused
    definitions with type/file summaries. Respects entry point exclusions.
  - `test_scaffold_generator` — AST-scans a Python source file, generates
    pytest or unittest test stubs for every public function and method.
    Handles async, class grouping, param hints, docstring hints.
  - `schema_diff_tool` — compares two SQLite database schemas: added/dropped
    tables, column changes, index changes, FK changes, row count deltas.
    Migration planning companion to `sqlite_schema_inspector`.
- All 6 registered in `tool_manifest.json` and `src/mcp_server.py`.
- All 6 tested: metadata + real execution runs pass.

Current state: 25 builder tools, 4 vendable packages, 1 vendable document
template. All new tools follow the standard contract.

---

## 2026-04-23 — Offline onboarding microsite for the main toolbox

- Added an offline onboarding surface at `START_HERE.html` with the full
  walkthrough in `onboarding/`.
- Added `OPEN_ME_FIRST.bat`, `OPEN_ME_FIRST.command`, and `launch_explorer.py`
  so the walkthrough has one obvious entry on copied folders and local
  machines.
- Wrote `_docs/EXPERIENTIAL_WORKFLOW.md` to explain the lived human-agent
  rhythm behind the toolbox, its trust boundaries, and the four-surface model.
- Added guided showcase pages for:
  - why the toolbox matters
  - how new sessions start
  - how the workflow feels in practice
  - how humans and agents share the loop
  - how tools, packages, and templates fit together
  - how vendoring works
  - toolbox atlas / repo map
- Updated `README.md` so the microsite becomes the clearest first-stop for
  humans while keeping the existing CLI, MCP, UI, and package entrypoints
  intact.
- All walkthrough copy was retargeted to this `.dev-tools` repo and its real
  docs. No links point back to old source projects used as design references.

Current state: the toolbox can now be handed to someone as a copied folder and
still provide a readable onboarding path before they move into the raw docs,
manifests, UI, and live tool surfaces.

---

## Template for future entries

Journal entry: pending mirror

- Files changed:
  - list important files or subsystems
- What changed:
  - concise summary
- Why it changed:
  - the design or operational reason
- Validation:
  - tests, smoke checks, or manual verification
- Current read:
  - what is now true
