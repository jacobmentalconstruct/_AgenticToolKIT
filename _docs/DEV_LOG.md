# Dev Log

_Last updated: 2026-04-29. This file is the authoritative human-readable
project log. The runtime SQLite at `_docs/_journalDB/app_journal.sqlite3`
is gitignored and not maintained as a mirror._

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

## 2026-04-29 — Parking doctrine integrated into the toolbox docs

- Added `_docs/PARKING_WORKFLOW.md` as the toolbox-native tranche closeout and
  handoff regimen.
- Added `_docs/WE_ARE_HERE_NOW.md` as the fast pickup surface for current
  toolbox truth.
- Updated `_docs/AGENT_GUIDE.md` to include an explicit inspect/verify/park/
  handoff loop.
- Updated `_docs/EXPERIENTIAL_WORKFLOW.md` so parking is part of the suite's
  lived doctrine rather than external convention.
- Updated `_docs/TODO.md` so the active tranche now reflects doctrine
  hardening, journal-mirroring decisions, and scoping the Windows-safe search
  fallback tool.
- Updated `README.md` so the parking regimen is discoverable from the main
  entry surface.

Current state: the toolbox now carries a clearer internal doctrine for how
meaningful tranches should be parked, documented, and handed off.

---

## 2026-04-29 — Setup doctrine codified for fresh project births

- Added `_docs/SETUP_DOCTRINE.md` to record the setup-first doctrine for new
  projects armed with `.dev-tools`.
- Added builtin scaffold template support for `_docs/SETUP_DOCTRINE.md` so
  freshly scaffolded projects inherit the doctrine automatically.
- Updated the builtin `ANY_NEW_CONVO_READ_THIS_FIRST.md` template so fresh
  agents are told to finish setup first, then read the builder constraint
  contract, then proceed in loyalty to the project and app rather than to
  convenience.
- Updated `README.md`, `_docs/AGENT_GUIDE.md`,
  `_docs/EXPERIENTIAL_WORKFLOW.md`, `_docs/WE_ARE_HERE_NOW.md`, and
  `_docs/TODO.md` so the setup-first regimen is discoverable from the live
  toolbox surfaces too.

Current state: the dev-suite now carries a clearer codified doctrine for how a
newly armed agent should establish a project before beginning meaningful app
implementation.

---

## 2026-04-29 — Sidecar release spine implemented

- Added `release_payload_manifest.json` as the machine-readable inventory for
  the current sidecar release candidate.
- Added `sidecar_install` to copy the full shipped `.dev-tools` payload into a
  target project root instead of requiring an agent to reach back to the source
  toolbox.
- Added `project_setup` so installed sidecars can audit, apply, and verify the
  setup doctrine using the existing journal, scaffold, and contract surfaces.
- Added `onboarding_site_check` so the offline walkthrough and its launch
  surfaces become a verifiable protected capability.
- Updated `install.py` so the human-facing installer now uses the full sidecar
  install path instead of the old thin-shim path.
- Updated the README, vendoring guide, microsite, and agent guide so the new
  install and setup flow is the visible default.

Current state: `.dev-tools` now has a live release spine for manual sidecar
install, project-local setup, and microsite verification. The next real proof
point is the fresh-project trial and the remaining harvest/cleanup
classification work.

---

## 2026-04-29 — Reference harvest boundary set for sidecar installs

- Added `_docs/REFERENCE_HARVEST.md` as the release-harvest map for root
  surfaces, old reference material, generated caches, and protected ship
  surfaces.
- Updated `release_payload_manifest.json` so `authorities/` is retained for
  harvest/provenance review but no longer copied by default sidecar installs.
- Updated `toolbox_manifest.json` so agents treat packed authorities as
  reference/provenance material and use `.potential-intake` as the real intake
  path name.
- Updated continuity docs so the next cleanup step is archive/delete only after
  useful code, setup doctrine, and microsite UX have been harvested.

Current read: the default installed sidecar should now carry the live toolbox,
microsite, docs, packages, templates, and active tools without dragging the old
BuilderSET authority folder into every target project.

---

## 2026-04-29 — Windows-safe repo search tool added

- Added `repo_search`, a project-local search tool that tries `rg` first when
  available and falls back to a native Python text search when `rg` is missing
  or fails.
- The fallback path avoids shell invocation and avoids PowerShell/security
  bypass attempts while still returning structured matches, source engine,
  fallback reason, and warnings.
- Registered the tool in `tool_manifest.json`, `src/mcp_server.py`, and the
  smoke-test MCP expectation.
- Updated continuity docs so this capability-hardening item is now marked
  complete and future refinement is tracked separately.

Current read: agents now have a safe first-party search surface for Windows
inspection friction instead of improvising around `rg` permission failures.

---

## 2026-04-29 — Prototype northstars collapsed and reference shape retired

- Collapsed `_docs/NORTHSTARS.md` from an open-ended parity wishlist into the
  release-scope current truth for the sidecar prototype.
- Retired legacy thin-shim authority install and old BuilderSET packed-authority
  surfaces from the active manifests, MCP registry, README, vendoring guide,
  microsite copy, and smoke tests.
- Removed root authority/reference/cache artifacts from the active repo shape.
- Added `_docs/ARCHITECTURE.md` and `_docs/builder_constraint_contract.md` so
  the continuity packet has stable current-truth architecture and contract
  entrypoints.

Current read: the toolbox is now shaped around one product path: install the
self-contained sidecar, onboard the human through the microsite, onboard the
agent through setup/contract doctrine, then build from project-local tools.

---

## 2026-04-29 — Strangler finalized: root identity is the installer, not the journal

- Removed strangler residue at the toolbox root that still treated this repo as
  the original `_app-journal` package:
  - Deleted `src/launch_ui.py` and `src/ui/app_journal_ui.py` (the journal UI
    belongs only to `packages/_app-journal/`, not the toolbox root).
  - Deleted `run-ui.bat` and `run-ui.sh` (byte-identical duplicates of the
    `run.*` scripts; both pointed at the deleted journal UI).
- Repointed the root entrypoint surface:
  - `run.bat` / `run.sh` now launch `install.py` (the sidecar installer GUI).
  - `tool_manifest.json` replaces `ui_entrypoint` with `installer_entrypoint`.
  - `release_payload_manifest.json` ships only `run.bat` / `run.sh` now.
- Hardened the installer (`install.py`):
  - Detects an existing `.dev-tools/` at the chosen target.
  - Prompts for clean remove-and-reinstall, or cancel. No partial-overwrite
    path — keeps prototype install behavior unambiguous.
  - Dropped the "Overwrite existing files" checkbox in favor of the explicit
    remove/cancel dialog.
- Cleaned remaining old-identity references:
  - `setup_env.bat` / `setup_env.sh` no longer echo `_app-journal`.
  - `requirements.txt` header now reads `.dev-tools dependencies`.
  - `src/lib/journal_store.py` config writer now emits `installer_hint`
    instead of a stale `ui_hint` to the deleted root UI.
  - `onboarding/pages/toolbox-atlas.html` "Operational Entry" card now lists
    `install.py`, `mcp_server.py`, `smoke_test.py`.
  - `_docs/AGENT_GUIDE.md` reference updated.
- Sweep of stale doc claims:
  - `DEV_LOG.md` header date refreshed; the SQLite-mirror claim is removed
    (the runtime SQLite is gitignored; this file is the authoritative log).
  - "Template for future entries" no longer carries the `pending mirror` tag.
  - `_docs/_journalDB/README.md` no longer references the deleted
    `authority.sqlite3`.
  - `_docs/TODO.md` compliance line corrected: the journal DB and exports
    are gitignored runtime surfaces, not part of shipped source state.
- Privacy / leak hardening:
  - `.gitignore` extended: `.claude/`, `.env*`, `*.key`/`*.pem`/`*.pfx`/`*.p12`,
    `credentials.json`, `secrets.json`, `*.log`, `_logs/`, IDE/OS junk.
    `.claude/settings.local.json` (which carries absolute user paths) is now
    ignored to prevent accidental commit.
  - Audit confirmed no API keys, passwords, tokens, or third-party app names
    appear in tracked content. Author attribution in `LICENSE.md` and the
    BCC template is intentional copyright marking and was left untouched.

Validation:

- `python src/smoke_test.py` — 39/39 pass after the cleanup
- 27 MCP tools enumerate cleanly via `mcp_server.py`
- `install.py` imports cleanly; the new remove-and-reinstall dialog path
  exercised by hand on a throwaway target
- Manual sweep confirmed no surviving references to `launch_ui`, `run-ui`,
  `app_journal_ui` outside historical DEV_LOG entries
- Tracked-content audit found no API keys, tokens, third-party app names,
  or other private data; LICENSE attribution intentionally retained

Classification: spiral.

- Capability increased: root identity is now single-purpose, pod-packaging
  is unblocked.
- Uncertainty decreased: the next bounded move (Dockerfile + headless
  install flag) is concrete and small.
- Boundary clarified: root toolbox vs vendable `_app-journal` package no
  longer overlap. Root no longer impersonates the package.

Current read: the root toolbox is now a single-purpose installer surface plus
agent/MCP/smoke-test surfaces. The journal UI lives only inside its vendable
package, and the strangler pattern is complete — no part of the active root
repo still pretends to be the original `_app-journal` package.

---

## 2026-04-29 — Park-doctrine gaps closed; v2 container workspace opened

- Park-doctrine completion (closing the gaps from the prior strangler entry):
  - Added explicit `Validation:` and `Classification: spiral` blocks to the
    strangler-finalization entry above, per `_docs/PARKING_WORKFLOW.md`
    minimum-park-payload requirements.
  - Dropped the stale "compliance checklist not all final" warning from
    `_docs/WE_ARE_HERE_NOW.md`. The compliance checklist is fully `[x]`.
  - Opened a fresh "Current tranche" in `_docs/TODO.md` for the container
    packaging work, with explicit tasks, non-goals, and the previous
    tranche moved into a parked-history block.
- v2 container workspace opened in isolation:
  - Created `_v2-pod/` at the repo root as the dedicated build space for
    wrapping the parked root prototype into a Kubernetes-friendly pod.
  - Created `_v2-pod/README.md` recording intent, layout, working rules,
    and the rule that the parent root is frozen during this tranche.
  - Installed a fresh `.dev-tools/` sidecar into `_v2-pod/.dev-tools/` via
    `sidecar_install` (265 files, full toolkit). This sidecar serves as
    the agent's toolbelt while working in `_v2-pod/`.
  - Added `_v2-pod/.dev-tools/` and `_v2-pod/_docs/_AppJOURNAL/`,
    `_v2-pod/_docs/_journalDB/` to `.gitignore` so the embedded toolkit
    copy and its runtime state are not tracked. Only the wrapper code we
    write inside `_v2-pod/` (Dockerfile, k8s manifests, etc.) gets
    tracked.

Validation:

- `python _v2-pod/.dev-tools/src/smoke_test.py` — 39/39 pass; 27 MCP
  tools enumerate cleanly from inside the installed sidecar
- `git status` confirmed `_v2-pod/.dev-tools/` is properly ignored; only
  `_v2-pod/README.md` shows as a tracked addition under the v2 folder
- DEV_LOG, WE_ARE_HERE_NOW, TODO continuity packet now self-consistent

Classification: spiral.

- Capability increased: an isolated workspace exists with a working
  toolkit copy ready to use, and the container tranche has a concrete
  task list.
- Uncertainty decreased: the "where do we build v2 without disturbing
  v1" question is now answered.
- Boundary clarified: the parent root is parked-frozen for this tranche;
  novel work happens only in `_v2-pod/`.

Current read: doc continuity packet meets the parking protocol's minimum
payload, and the container packaging tranche is open in an isolated
workspace. The parked root remains untouched and authoritative.

---

## 2026-04-29 — Container tranche: Dockerfile, entrypoint, and k8s manifest drafted in `_v2-pod/`

- Confirmed the headless install path was already available: the existing
  `src/tools/sidecar_install.py` uses `standard_main` and accepts
  `python sidecar_install.py run --input-json '{...}'`. No new
  `--headless` flag on `install.py` was needed; `install.py` stays the
  GUI surface, `sidecar_install.py` is the canonical CLI surface, and the
  Dockerfile wires to the latter.
- Added `_v2-pod/Dockerfile` — `python:3.11-slim` base, COPY of the
  embedded sidecar into `/opt/dev-tools/`, entrypoint script as the
  container entrypoint. Stdlib only; no `apt install`, no extra Python
  packages.
- Added `_v2-pod/.dockerignore` — excludes runtime journal state and
  pycache from the build context so the image ships a clean toolkit, not
  the build host's accumulated journal artifacts.
- Added `_v2-pod/entrypoint.sh` — idempotent: installs a fresh sidecar
  into `/workspace` if missing, runs the smoke test (failure aborts the
  pod), then `exec`s into the MCP server so PID 1 is the actual workload.
- Added `_v2-pod/k8s/deployment.yaml` — single-replica Deployment with
  ephemeral default and a commented PVC opt-in path. `replicas` is
  scalable for parallel ephemeral agent sandboxes.
- Documented model decisions in `_v2-pod/README.md`: ephemeral by default
  (PVC opt-in), project mounted at runtime (not baked into the image),
  MCP over stdio (no port exposure), stdlib-only discipline.

Validation:

- `python src/tools/sidecar_install.py metadata` confirms the headless CLI
  surface
- `python _v2-pod/.dev-tools/src/smoke_test.py` — 39/39 pass against the
  embedded sidecar copy, which is what the image will COPY at build time
- `docker build` and `kubectl apply` are pending host-side verification
  (cannot run from the agent sandbox); both are tracked as the remaining
  unchecked items in `_docs/TODO.md`'s active tranche

Classification: spiral.

- Capability increased: pod-image artifacts exist and are coherent.
- Uncertainty decreased: the build/run flow is documented end to end; the
  remaining unknowns are host-side `docker build` quirks, not design
  questions.
- Boundary clarified: parent root remains parked-frozen; all v2 wiring
  lives inside `_v2-pod/`. The Dockerfile builds with `_v2-pod/` itself
  as the build context, so no `.dockerignore` or build artifact at the
  parent root was required.

Current read: `_v2-pod/` now carries a complete first-cut pod packaging
(Dockerfile, entrypoint, k8s manifest, README). The next concrete move is
host-side: `docker build` + a local kind/minikube `kubectl apply` to
verify the image and pod actually behave as designed.

---

## 2026-04-29 — Container tranche: image builds clean, end-to-end pod flow verified

- `docker build -t devtools-pod:v2 .` from `_v2-pod/` succeeds against
  Docker 29.2.1. Image builds in ~10s on a python:3.11-slim base; build
  context is `_v2-pod/` itself so the parked root is untouched.
- `docker run --rm -i devtools-pod:v2 < /dev/null` runs the entrypoint
  end-to-end:
  - `[entrypoint] Installing .dev-tools sidecar into /workspace...`
  - `[entrypoint] Sidecar install complete.`
  - `[entrypoint] Running smoke test...`
  - `[entrypoint] Smoke test passed.`
  - `[entrypoint] Launching MCP server...`
  - MCP exits cleanly when stdin closes.
- Direct verification: 39/39 smoke tests pass inside the running container,
  27 MCP tools enumerate, MCP `tools/list` and `tools/call journal_query`
  both succeed.
- `_v2-pod/k8s/deployment.yaml` parses as valid YAML; structure
  (kind=Deployment, replicas=1, image=devtools-pod:v2) is correct.
- `kubectl apply --dry-run` against a live cluster is still pending — no
  local cluster (kind/minikube) was running at verification time.

Validation:

- `docker --version` → 29.2.1
- `docker build -t devtools-pod:v2 _v2-pod/` → clean build
- `docker run` end-to-end → entrypoint reaches MCP launch successfully
- In-container smoke test → 39/39 pass, 27 MCP tools enumerated
- `python -c "import yaml; yaml.safe_load(...)"` on the Deployment manifest
  → valid YAML with expected fields

Classification: spiral.

- Capability increased: pod packaging is no longer just on paper — image
  builds, runs, and the toolkit functions inside it.
- Uncertainty decreased: the only remaining unknowns are cluster-side
  (does a real k8s pod reach Ready, does `kubectl attach` work cleanly)
  and registry distribution. Both are operational, not design.
- Boundary clarified: the parent root remained untouched throughout
  build and run — `_v2-pod/` is a fully self-contained build space.

Current read: the container tranche is functionally complete inside the
agent sandbox's reach. Remaining work (live k8s deploy + image registry
push) is host/cluster-side and can be done at any time the user has a
cluster up.

---

## 2026-04-30 — Local-agent sys-ops northstar planned and parked

- Promoted the remaining post-RC northstar from broad deferred capability
  notes into a phased local-agent system-operations roadmap.
- Set the implementation sequence: host capability probe, workspace boundary
  audit, command profile detection, process/port inspection, dependency
  readiness, guarded dev-server management, Docker/Kubernetes wrappers,
  secret/runtime-artifact safety, and local-agent bootstrap packet.
- Updated the continuity packet so future sessions can enter through
  `README.md`, `_docs/NORTHSTARS.md`, `_docs/TODO.md`,
  `_docs/WE_ARE_HERE_NOW.md`, `_docs/ARCHITECTURE.md`, and
  `_docs/AGENT_GUIDE.md`.
- Preserved the safety boundary: no raw unrestricted terminal parity. Mutating
  operations must flow through declared command profiles, scoped wrappers, and
  explicit confirmation inputs.

Validation:

- Runtime journal entry written with `journal_write`:
  `journal_1819d44c3943`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.
- `python src/smoke_test.py` -> 39/39 pass.

Classification: spiral.

- Capability increased: the remaining northstar is now implementation-shaped,
  not a vague wishlist.
- Uncertainty decreased: local desktop is the first runtime target, with pod
  support layered through Docker/Kubernetes wrappers.
- Boundary clarified: creative/browser/automation capabilities remain later
  horizons until the sys-ops layer gives local agents a reliable operating
  envelope.

Current read: Tranche 0 is the roadmap parking commit. Tranche 1 begins with
read-only sys-ops tools that expose host, workspace, command, and process/port
truth through MCP-visible structured results.

---

## 2026-04-30 — Tranche 1 local-agent sys-ops introspection implemented

- Added four stdlib-only, read-only builder tools:
  - `host_capability_probe` reports OS, Python, shell, and common developer
    command availability/version text.
  - `workspace_boundary_audit` resolves project root, sidecar root, git root,
    runtime paths, ignored-ish footprint, and write-boundary warnings.
  - `project_command_profile` detects declared setup/test/run/build/dev,
    Docker, and Kubernetes commands and emits stable command IDs.
  - `process_port_inspector` inspects relevant processes and occupied ports
    with platform-specific fallbacks and bounded output.
- Registered all four tools in `tool_manifest.json` and `src/mcp_server.py`.
- Extended the root smoke test with temporary-fixture coverage for the new
  sys-ops tools and MCP enumeration.
- Updated `README.md`, `_docs/AGENT_GUIDE.md`, `_docs/ARCHITECTURE.md`,
  `_docs/NORTHSTARS.md`, `_docs/TODO.md`, and `_docs/WE_ARE_HERE_NOW.md` so
  the new active tool surface and next tranche are discoverable.

Validation:

- `python -m py_compile src/tools/host_capability_probe.py
  src/tools/workspace_boundary_audit.py src/tools/project_command_profile.py
  src/tools/process_port_inspector.py src/mcp_server.py src/smoke_test.py`
  -> pass.
- Focused metadata/run checks for the new tools -> pass.
- `python src/smoke_test.py` -> 43/43 pass; MCP lists 31 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` ->
  5/5 smoke suites pass.
- Runtime journal entry written with `journal_write`:
  `journal_34d0db4663bf`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.
- Runtime journal entry written with `journal_write`:
  `journal_584fc62bf04c`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Classification: spiral.

- Capability increased: a local agent can now learn host capability,
  workspace boundaries, project command declarations, and process/port state
  through structured MCP-visible tools.
- Uncertainty decreased: the first sys-ops layer is read-only and works on the
  current Windows desktop environment.
- Boundary clarified: no dependency installation, server control, process
  killing, Docker mutation, Kubernetes apply, or raw terminal parity was added.

Current read: Tranche 1 is complete. Tranche 2 should add
`dependency_env_check` and refine command-profile IDs so later guarded
operations can reuse one stable command vocabulary.

---

## 2026-04-30 — Tranche 2 dependency readiness and command profile refinement

- Added `dependency_env_check`, a stdlib-only read-only tool that inspects
  Python and Node dependency surfaces without installing anything.
- The new tool reports virtualenv state, requirements/pyproject surfaces,
  package.json and node_modules state, lockfiles, tool availability, optional
  Python import checks, and readiness warnings.
- Refined `project_command_profile` to emit `profile_version`, command line,
  working directory, runtime, requirement hints, tags, and confirmation flags
  for every discovered command.
- Registered `dependency_env_check` in `tool_manifest.json` and
  `src/mcp_server.py`.
- Extended smoke coverage so the temporary sys-ops fixture proves dependency
  readiness checks and command metadata without installing dependencies.
- Updated README, agent guide, architecture, northstars, TODO, and continuity
  state so Tranche 3 is the next active source tranche.

Validation:

- `python -m py_compile src/tools/dependency_env_check.py
  src/tools/project_command_profile.py src/mcp_server.py src/smoke_test.py`
  -> pass.
- Focused `dependency_env_check` and `project_command_profile` runs -> pass.
- `python src/smoke_test.py` -> 44/44 pass; MCP lists 32 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` ->
  5/5 smoke suites pass.

Classification: spiral.

- Capability increased: local agents can now distinguish declared dependency
  surfaces from installed/readiness state before running workflows.
- Uncertainty decreased: later guarded operations can consume a richer command
  profile instead of re-detecting runtime assumptions.
- Boundary clarified: no install, server start/stop, Docker mutation,
  Kubernetes apply, or raw terminal parity was added.

Current read: Tranche 2 is complete pending final verification. Tranche 3
should implement `dev_server_manager` on top of declared command IDs and
gitignored runtime process/log state.

---

## 2026-04-30 — Tranche 3 guarded dev-server manager

- Added `dev_server_manager`, a stdlib-only operations tool for guarded
  `status`, `start`, `stop`, `restart`, `tail`, and `health` actions.
- The manager starts only `dev` or `run` command IDs emitted by
  `project_command_profile`; start/stop/restart require `confirm: true`.
- Runtime process state is written under ignored
  `.dev-tools/runtime/dev_servers/servers.json`, and logs are written under
  ignored `.dev-tools/runtime/dev_servers/logs/`.
- `project_command_profile` now infers `python:dev-server` when a project has a
  root `dev_server.py`, giving tests and small Python projects a stdlib dev
  server command profile.
- Registered `dev_server_manager` in `tool_manifest.json` and
  `src/mcp_server.py`.
- Extended smoke coverage with a temporary HTTP server fixture that verifies
  confirmation refusal, start, health, status, tail, stop, and MCP listing.
- Updated README, agent guide, architecture, northstars, TODO, and continuity
  state so Tranche 4 Docker/Kubernetes wrappers are the next source tranche.
- Runtime journal entry written with `journal_write`:
  `journal_cf51feb7a664`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Validation:

- `python -m py_compile src/tools/dev_server_manager.py
  src/tools/project_command_profile.py src/mcp_server.py src/smoke_test.py`
  -> pass.
- `python src/tools/dev_server_manager.py metadata` -> pass.
- `python src/smoke_test.py` -> 50/50 pass; MCP lists 33 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` ->
  5/5 smoke suites pass.

Classification: spiral.

- Capability increased: a local agent can now manage a project dev server
  lifecycle without raw terminal parity.
- Uncertainty decreased: command-profile IDs now carry through to a real
  guarded process/log/health workflow.
- Boundary clarified: the manager only controls registered processes it
  launched, and mutating lifecycle actions require explicit confirmation.

Current read: Tranche 3 is complete pending final parking verification.
Tranche 4 should add Docker and Kubernetes wrappers, using `_v2-pod/` as the
primary fixture and keeping live side effects behind confirmation.

---

## 2026-04-30 — Tranche 4 Docker and Kubernetes operation wrappers

- Added `docker_ops`, a stdlib-only operations wrapper for Docker `status`,
  `build`, `run_smoke`, `logs`, `tag`, and `push`.
- Docker build contexts must resolve under `project_root`; tag and push require
  `confirm: true`; preview mode lets an agent inspect commands without touching
  Docker.
- Added `k8s_ops`, a stdlib-only operations wrapper for Kubernetes `context`,
  `validate`, `dry_run`, `apply`, `status`, `logs`, and
  `attach_instructions`.
- Kubernetes manifests must resolve under `project_root`; live apply requires
  `confirm: true`; `validate` performs a portable structural manifest check and
  `dry_run` can prepare the kubectl command in preview mode.
- Registered both tools in `tool_manifest.json` and `src/mcp_server.py`.
- Extended smoke coverage with Docker and Kubernetes fixtures that verify
  status, project-scoped build previews, confirmation gates, manifest
  validation, dry-run previews, attach instructions, and MCP listing.
- Verified `_v2-pod/` through the new tools: Docker build/run-smoke previews
  resolve to `_v2-pod`, and `k8s_ops validate` recognizes the Deployment named
  `devtools-pod` using image `devtools-pod:v2`.
- Updated README, agent guide, architecture, northstars, TODO, `_v2-pod`
  README, and continuity state so Tranche 5 safety/cleanup tools are next.
- Runtime journal entry written with `journal_write`:
  `journal_e1f5cc1066a2`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Validation:

- `python -m py_compile src/tools/docker_ops.py src/tools/k8s_ops.py
  src/mcp_server.py src/smoke_test.py` -> pass.
- `python src/tools/docker_ops.py metadata` -> pass.
- `python src/tools/k8s_ops.py metadata` -> pass.
- Focused `_v2-pod` wrapper runs:
  `docker_ops build --preview`, `docker_ops run_smoke --preview`,
  `k8s_ops validate`, and `k8s_ops dry_run --preview` -> pass.
- `python src/smoke_test.py` -> 57/57 pass; MCP lists 35 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` ->
  5/5 smoke suites pass.

Classification: spiral.

- Capability increased: a local or podded agent can now plan and operate
  Docker/Kubernetes workflows through scoped JSON tools rather than raw shell.
- Uncertainty decreased: `_v2-pod` is now visible to the tool layer as a real
  Docker/Kubernetes fixture.
- Boundary clarified: registry mutation and live cluster apply require
  explicit confirmation; portable preview and validation paths avoid accidental
  daemon/cluster side effects.

Current read: Tranche 4 is complete pending final parking verification.
Tranche 5 should add `secret_surface_audit` and `runtime_artifact_cleaner`
with redaction, dry-run defaults, allowlisted cleanup, and tracked-file
protection.

---

## 2026-04-30 — Tranche 5 safety, secrets, and runtime cleanup

- Added `secret_surface_audit`, a stdlib-only read-only scanner for obvious
  secret-like values and risky `.env` exposure.
- Secret findings redact detected values in `redacted_value` and `line_preview`
  so tool output can be shared without leaking the matched value.
- Added `runtime_artifact_cleaner`, a dry-run-first cleaner for allowlisted
  generated artifacts such as caches, logs, journal exports, and known package
  smoke artifacts.
- Cleanup requires `confirm: true` when `dry_run` is false, and tracked files
  are protected unless `allow_tracked: true` is explicitly supplied.
- Registered both tools in `tool_manifest.json` and `src/mcp_server.py`.
- Extended smoke coverage with fake secret fixtures and disposable runtime
  artifacts proving redaction, `.env` exposure detection, dry-run default,
  confirmation gating, and allowlisted cleanup.
- Updated README, agent guide, architecture, northstars, TODO, and continuity
  state so Tranche 6 local-agent bootstrap and northstar closeout are next.
- Runtime journal entry written with `journal_write`:
  `journal_2669d2d7b8fa`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Validation:

- `python -m py_compile src/tools/secret_surface_audit.py
  src/tools/runtime_artifact_cleaner.py src/mcp_server.py src/smoke_test.py`
  -> pass.
- `python src/tools/secret_surface_audit.py metadata` -> pass.
- `python src/tools/runtime_artifact_cleaner.py metadata` -> pass.
- `python src/smoke_test.py` -> 61/61 pass; MCP lists 37 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` ->
  5/5 smoke suites pass.

Classification: spiral.

- Capability increased: a local agent can now inspect secret-risk surfaces and
  clean generated runtime state through structured tools.
- Uncertainty decreased: cleanup behavior is dry-run-first, allowlisted, and
  backed by Git tracked-file checks.
- Boundary clarified: the audit tool is heuristic and redacted; the cleaner
  does not remove tracked files by default and requires confirmation to mutate.

Current read: Tranche 5 is complete pending final parking verification.
Tranche 6 should add `local_agent_bootstrap` and close the Local Agent
Operations northstar.

---

## 2026-04-30 — Tranche 6 local-agent bootstrap and northstar closeout

- Added `local_agent_bootstrap`, a stdlib-only launch packet generator for a
  local or podded agent.
- The tool aggregates host capabilities, workspace boundaries, command
  profiles, dependency readiness, latest journal entries, tool-manifest sys-ops
  coverage, operating-envelope notes, and constraint-document excerpts.
- Default behavior returns the packet without writing. Optional writes go under
  ignored `.dev-tools/runtime/local_agent_bootstrap/`.
- Registered `local_agent_bootstrap` in `tool_manifest.json` and
  `src/mcp_server.py`.
- Extended smoke coverage so the launch packet is generated in Markdown form
  and MCP lists 38 tools.
- Closed the Local Agent Operations northstar in README, architecture,
  northstars, TODO, AGENT_GUIDE, and WE_ARE_HERE_NOW.
- Runtime journal entry written with `journal_write`:
  `journal_2b64edce7521`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Validation:

- `python -m py_compile src/tools/local_agent_bootstrap.py src/mcp_server.py
  src/smoke_test.py` -> pass.
- `python src/tools/local_agent_bootstrap.py metadata` -> pass.
- `python src/smoke_test.py` -> 62/62 pass; MCP lists 38 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` ->
  5/5 smoke suites pass.

Classification: spiral.

- Capability increased: a local agent can now receive one structured launch
  packet summarizing its operating envelope before it acts.
- Uncertainty decreased: the sys-ops layer has an explicit aggregation surface
  rather than requiring agents to remember the whole tool sequence.
- Boundary clarified: the bootstrap packet is orientation, not authority to
  mutate; optional writes remain in ignored runtime state.

Current read: Local Agent Operations is closed. The next horizon should be
chosen deliberately rather than inferred from this sys-ops plan.

---

## 2026-05-04 — Tranche 7 Safe Text Workspace Operations selected

- Documented Safe Text Workspace Operations as the active post-sys-ops source
  horizon.
- The planned tranche bridges the closed local-agent sys-ops layer and a future
  Ollama-backed local sidecar agent by adding bounded text/file primitives.
- The planned tool set is `text_file_reader`, `text_file_writer`,
  `directory_scaffold`, `text_file_validator`, `file_move_guarded`, and
  `file_delete_guarded`.
- `project_setup` remains the builder-contract scaffold authority; Tranche 7
  should not ask the model to infer or recreate the required setup scaffold.
- Mutating file operations should require explicit confirmation. Move/delete
  should carry a non-empty reason, and delete should quarantine into ignored
  `.dev-tools/runtime/trash/` with receipts rather than permanently removing
  files by default.
- This was a documentation-only parking pass. No tool registration,
  implementation files, or MCP surfaces were changed.
- Runtime journal entry written with `journal_write`:
  `journal_03c3a371dc47`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Validation:

- `git diff --check` -> pass.
- `python src/smoke_test.py` -> 62/62 pass; MCP lists 38 tools.

Classification: spiral.

- Capability direction increased: the next local-agent layer is now explicit
  instead of implied.
- Uncertainty decreased: the missing basic file primitives are named, bounded,
  and sequenced after sys-ops closure.
- Boundary clarified: no raw terminal parity, no dependency installs, no
  replacement of `project_setup`, and no permanent delete by default.

Current read: Tranche 7 is documented and ready for implementation.

---

## 2026-05-04 — Planning runway parked through local sidecar agent

- Added the next two queued phases after Tranche 7 to the continuity packet and
  onboarding surfaces.
- Tranche 8 is now planned as Private Git Workspace Operations. The core idea
  is a sidecar-owned Git checkpoint layer using an ignored private gitdir under
  `.dev-tools/runtime/private_git/` and the chosen project root as worktree.
- The planned Git surface is `git_private_workspace` with guarded `status`,
  `init`, `add`, `commit`, `branch`, `checkout`, `pull`, and `push` actions.
- Private Git should not mutate the user's main project `.git` by default.
  Push and pull require explicit private-remote configuration; mutating actions
  require `confirm: true`.
- Tranche 9 is now planned as Local Sidecar Agent Runtime: an Ollama-backed,
  stdlib-first agent that acts only through allowlisted toolbox tools.
- The planned agent loop is fixed by contract: probe, audit, setup, plan, ask,
  act, verify, checkpoint, and park.
- Qwen coder-family models are the preferred structured JSON/tool-planning
  layer; Qwen human-interface models are the preferred response layer.
- The local agent should use binary or multiple-choice human prompts for
  high-risk or ambiguous decisions and must not receive raw terminal or
  unrestricted filesystem parity.
- Onboarding docs now point humans and agents toward the active Tranche 7,
  queued Tranche 8, and queued Tranche 9 runway.
- Runtime journal entry written with `journal_write`:
  `journal_5fd12e2e1e5b`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Validation:

- `git diff --check` -> pass.
- `python src/smoke_test.py` -> 62/62 pass; MCP lists 38 tools and
  onboarding integrity passes.

Classification: spiral.

- Capability direction increased: the path from basic safe file tools to
  private checkpoints to a local sidecar agent is now explicit.
- Uncertainty decreased: private Git is scoped as agent-owned runtime state,
  not silent control of the user's real repository.
- Boundary clarified: the future agent acts through the guarded toolbox, asks
  before risky steps, and checkpoints through private Git.

Current read: When implementation resumes, complete Tranche 7 first, then
Tranche 8 private Git operations, then Tranche 9 local sidecar agent runtime.

---

## 2026-05-04 — Tranche 7 Safe Text Workspace Operations implementation

- Added shared safe text workspace helpers in `src/lib/text_workspace.py` for
  root-bounded path resolution, `.dev-tools` protection, text/binary checks,
  stdlib validation, tracked-file detection, and quarantine receipts.
- Added `text_file_reader`, a bounded text reader that reports size, line
  count, newline style, encoding, content, and excerpt while rejecting
  outside-root, protected, oversized, and likely binary files.
- Added `text_file_writer`, a confirmed create/overwrite/append tool with
  `overwrite: true` replacement gating, parent creation control, `.dev-tools`
  protection, and optional validation.
- Added `directory_scaffold`, a dry-run-first declarative directory/text-file
  scaffold tool with root-boundary checks, existing-file skip behavior, optional
  validation, and confirmation-gated writes.
- Added `text_file_validator`, a read-only validator for Python, JSON, TOML,
  and basic text-like surfaces using only the Python standard library.
- Added `file_move_guarded`, a confirmed move/rename tool that requires a
  non-empty reason and protects tracked files and `.dev-tools` internals by
  default.
- Added `file_delete_guarded`, a confirmed quarantine-delete tool that moves
  targets into ignored runtime trash and writes receipts instead of permanently
  deleting by default.
- Registered all six tools in `tool_manifest.json` and `src/mcp_server.py`.
- Extended `src/smoke_test.py` with Tranche 7 fixtures covering confirmation
  gates, outside-root rejection, binary rejection, validation failures,
  scaffold dry-run/apply, guarded move, quarantine receipts, and tracked-file
  protection.
- Updated README, agent guide, architecture, northstars, TODO,
  WE_ARE_HERE_NOW, experiential workflow, and onboarding pages so Tranche 7 is
  satisfied and Tranche 8 Private Git Workspace Operations is next.
- Runtime journal entry written with `journal_write`:
  `journal_ce573aec1dd0`.
- Local markdown journal export created under the gitignored
  `_docs/_AppJOURNAL/exports/` runtime area for operator visibility.

Validation:

- `git diff --check` -> pass.
- `python -m py_compile src/lib/text_workspace.py` plus all six new tools,
  `src/mcp_server.py`, and `src/smoke_test.py` -> pass.
- Metadata CLI checks for all six new tools -> pass.
- `python src/smoke_test.py` -> 79/79 pass; MCP lists 44 tools and onboarding
  integrity passes.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` -> 4/5
  suites passed; `_ollama-prompt-lab` timed out waiting for
  `ollama run qwen3.5:2b` after 90 seconds. The toolbox suite and the
  `_app-journal`, `_constraint-registry`, and `_manifold-mcp` package suites
  passed.

Classification: spiral.

- Capability increased: a local agent now has bounded file primitives for
  creating and maintaining text/code project files.
- Uncertainty decreased: smoke fixtures prove the safety contract around
  confirmation, boundaries, validation, tracked files, and quarantine delete.
- Boundary clarified: this tranche adds guarded text/file operations, not raw
  shell access, dependency installs, setup-doctrine replacement, or permanent
  deletion by default.

Current read: Tranche 7 is complete. Tranche 8 should implement
`git_private_workspace` as the sidecar-owned private Git checkpoint layer.

---

## 2026-05-04 — Tranche 8 Private Git Workspace Operations implementation

- Added `git_private_workspace`, a guarded sidecar-owned Git wrapper with
  `status`, `init`, `add`, `commit`, `branch`, `checkout`, `pull`, and `push`
  actions.
- The private Git workspace stores its gitdir under ignored
  `.dev-tools/runtime/private_git/` while using the chosen project root as the
  worktree.
- Mutating actions require `confirm: true`; commits require a non-empty
  message; push/pull require explicit private-remote configuration; `origin`
  is blocked unless explicitly allowed.
- Pathspecs resolve under the chosen project root and reject outside-root
  escapes, `.git/`, `.dev-tools/runtime/`, and risky secret surfaces such as
  `.env`, key, certificate, and credential files.
- Registered `git_private_workspace` in `tool_manifest.json` and
  `src/mcp_server.py`.
- Extended `local_agent_bootstrap` so launch packets include private Git status
  and the operating envelope names private checkpointing.
- Extended `src/smoke_test.py` with Tranche 8 fixtures covering confirmation
  gates, sidecar gitdir initialization, no project-root `.git` creation,
  outside-root rejection, risky path rejection, add/commit, branch/checkout,
  and local-bare-remote push/pull without network.
- Updated README, agent guide, architecture, northstars, TODO,
  WE_ARE_HERE_NOW, and onboarding pages so Tranche 8 is satisfied and Tranche 9
  Local Sidecar Agent Runtime is the active horizon.

Validation:

- `python src/smoke_test.py` -> 92/92 pass; MCP lists 45 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` -> 5/5
  suites passed, including `_ollama-prompt-lab`.

Classification: spiral.

- Capability increased: a future local agent can now save, branch, and sync its
  own checkpoints without taking over the operator's main repository by
  default.
- Uncertainty decreased: smoke fixtures prove the sidecar Git path does not
  create a project-root `.git`, blocks risky pathspecs, and can push/pull
  against an explicit local bare remote.
- Boundary clarified: private Git is an agent checkpoint layer, not raw Git
  terminal parity and not silent use of the user's `origin`.

Current read: Tranche 8 is complete. Tranche 9 should implement the
Ollama-backed local sidecar agent runtime on top of sys-ops, safe text, and
private Git tools.

---

## 2026-05-04 — Tranche 9 Local Sidecar Agent Runtime safe floor

- Added `local_sidecar_agent`, a stdlib-first Ollama-backed local agent floor
  with `status`, `models`, and `run` actions.
- The runtime creates ignored state under `.dev-tools/runtime/local_agent/`
  with sessions, logs, state, runs, outputs, parts, ref, and tools subfolders.
- Added configurable model roles, Ollama base URL, timeout, max tool rounds,
  allowed tools, mutation confirmation, checkpoint confirmation, and deterministic
  mock responses for smoke tests.
- Implemented fenced `tool_call` JSON parsing, schema validation,
  allowlist enforcement, malformed-call feedback, mutation approval stops, and
  result round-tripping.
- The agent floor calls `local_agent_bootstrap`, `workspace_boundary_audit`, and
  `project_setup audit` before model tool execution.
- The runtime routes through existing guarded toolbox tools rather than
  duplicating file, scaffold, journal, or private Git primitives.
- Added touched-file validation, JSONL audit/action logs, turn journaling, and
  optional private Git checkpointing through `git_private_workspace`.
- Registered `local_sidecar_agent` in `tool_manifest.json` and
  `src/mcp_server.py`.
- Extended `src/smoke_test.py` with Tranche 9 fixtures covering runtime layout,
  approval-required stops before unconfirmed mutation, mock-Ollama tool calls,
  safe text writes, validation, journaling, and private Git checkpointing.
- Updated README, agent guide, architecture, northstars, TODO,
  WE_ARE_HERE_NOW, and onboarding pages so Tranche 9 is satisfied as a safe
  floor and future work is framed as agent hardening.

Validation:

- `python -m py_compile src/tools/local_sidecar_agent.py src/mcp_server.py
  src/smoke_test.py` -> pass.
- `python src/smoke_test.py` -> 95/95 pass; MCP lists 46 tools.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` -> 5/5
  suites passed, including `_ollama-prompt-lab`.

Classification: spiral.

- Capability increased: the toolbox can now run a local Ollama-backed agent
  turn that acts only through allowlisted guarded tools.
- Uncertainty decreased: mock-model smoke coverage proves the core loop can
  stop for approval, write through safe text primitives, validate touched files,
  journal state, and checkpoint through private Git.
- Boundary clarified: Tranche 9 is a safe floor, not raw shell parity,
  dependency installation, or a duplicate file/VCS stack.

Current read: Tranche 9 is complete as an initial runtime. The next work should
harden the local sidecar agent with recovery, evidence/claim validation,
disposable run workspaces, richer approval UX, and optional live streaming.

---

## 2026-05-04 — Tranche 10 Local Agent Operator UI prototype

- Added `agent_ui.py`, a stdlib Tkinter desktop prototype for running the local
  sidecar agent and testing individual toolbox tools.
- Added `chat.bat` and `chat.sh` as the friendly root entrypoints, plus
  `agent_ui.bat` and `agent_ui.sh` as explicit operator UI launchers.
- Added `src/lib/operator_ui_support.py` for manifest loading, metadata
  loading, safe in-process tool dispatch, schema-derived default inputs,
  agent payload generation, model dropdown defaults, JSON formatting, and
  privacy-safe path rendering.
- Built the Agent Console with a project picker, Ollama base URL, model
  dropdowns, prompt entry, allowed-tool checklist, timeout/max-round controls,
  confirmation toggles, status, run, and sanitized output.
- Built the Tool Lab with a manifest-backed tool dropdown, schema/summary
  display, editable JSON input, side-effect confirmation gate, and sanitized
  result output.
- Added privacy guardrails so committed docs and normal UI output use
  placeholders such as `<project_root>` and `<toolbox_root>` instead of private
  local machine paths. `LICENSE.md` remains the copyright identity exception.
- Added Tranche 10 smoke coverage for UI helpers and a headless
  `agent_ui.py --self-test` path.
- Updated README, release payload manifest, toolbox manifest, agent guide,
  architecture, northstars, TODO, WE_ARE_HERE_NOW, and onboarding so the new
  human entrypoint is discoverable.

Validation:

- `python agent_ui.py --self-test` -> pass.
- `python -m py_compile agent_ui.py src/lib/operator_ui_support.py` -> pass.
- `python src/smoke_test.py` -> 103/103 pass; MCP lists 46 tools.
- `python src/tools/onboarding_site_check.py run --input-json
  '{"project_root":"."}'` -> pass.
- `python src/tools/smoke_test_runner.py run --input-json
  '{"toolbox_root":".","include_packages":true,"timeout_seconds":60}'` -> 5/5
  suites passed.

Classification: spiral.

- Capability increased: a human can now exercise the local sidecar agent and
  Tool Lab from a desktop UI without hand-writing every JSON payload.
- Uncertainty decreased: model selection, tool dispatch, payload building, and
  privacy sanitization are covered by headless tests.
- Boundary clarified: the UI is a review and control surface over existing
  guarded tools, not a new shell, MCP, or unrestricted filesystem channel.

Current read: Tranche 10 is implemented. The next work should use the operator
UI to harden the local sidecar agent with recovery, evidence/claim validation,
disposable run workspaces, richer approvals, and optional live streaming.

---

## Template for future entries

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
