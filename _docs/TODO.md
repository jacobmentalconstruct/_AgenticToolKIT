# Project Backlog

_Last updated: 2026-05-04._

---

## Current footing

- `.dev-tools` is active as the main universal toolbox.
- The offline onboarding microsite is now in place as the human-first entry.
- This backlog is now joined by `WE_ARE_HERE_NOW.md`, `NORTHSTARS.md`, and the
  tranche closeout regimen in `PARKING_WORKFLOW.md`.
- The release spine now includes a full sidecar install path, project setup
  orchestration, and an onboarding-site integrity check.
- The prototype northstars are collapsed into current release truth; deferred
  expansion is intentionally out of scope for this release candidate.
- The local-agent sys-ops northstar is closed. The active post-sys-ops source
  horizon is Safe Text Workspace Operations: bounded text/file primitives for a
  desktop-first local agent.

---

## Current state

**Tranche 7 selected: Safe Text Workspace Operations.**

Tranche 6 closed the local-agent sys-ops northstar. Tranche 7 is now the active
source-shaped horizon: safe text workspace primitives that let a local agent
read, create, scaffold, validate, move, and quarantine-delete text project
files under a user-chosen project root.

`project_setup` remains the builder-contract scaffold authority. Tranche 7
should not ask an agent to infer the required setup scaffold; it should provide
bounded file primitives that operate after the project root and setup doctrine
are known.

### Active tasks

- [ ] Add `text_file_reader`.
- [ ] Add `text_file_writer`.
- [ ] Add `directory_scaffold`.
- [ ] Add `text_file_validator`.
- [ ] Add `file_move_guarded`.
- [ ] Add `file_delete_guarded`.
- [ ] Register the new tools in `tool_manifest.json` and `src/mcp_server.py`.
- [ ] Extend `src/smoke_test.py` with temp-fixture coverage for read, write,
      scaffold, validate, guarded move, and quarantine delete behavior.
- [ ] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [ ] Write a Tranche 7 journal entry and export the journal for operator
      visibility.
- [ ] Run final verification and commit the implementation tranche.

### Tranche 7 tool contract

- `text_file_reader`: bounded text reads under `project_root`; report size,
  line count, newline style, and content/excerpt while rejecting outside-root,
  binary, or oversized files unless explicitly bounded.
- `text_file_writer`: create, overwrite, or append text payloads with
  `confirm: true`; require `overwrite: true` for replacement; support
  `create_dirs: true`; block `.dev-tools/` internals by default.
- `directory_scaffold`: apply a declarative directory/file manifest; dry-run by
  default; require `confirm: true` to write; keep every entry under the project
  root; skip existing files unless `overwrite: true`.
- `text_file_validator`: validate text surfaces without third-party
  dependencies: Python via `ast.parse`, JSON via `json.loads`, TOML via
  `tomllib`, and basic readability/size/null-byte checks for markdown, text,
  shell, batch, CSS, HTML, and YAML-like files.
- `file_move_guarded`: move or rename files/directories under the project root
  with `confirm: true` plus a non-empty `reason`; refuse overwrites unless
  explicitly enabled; protect `.dev-tools/` and tracked files by default.
- `file_delete_guarded`: quarantine instead of permanently deleting by moving
  targets to ignored `.dev-tools/runtime/trash/`; require `confirm: true` plus
  a non-empty `reason`; write a receipt with original path, timestamp, reason,
  actor, and tracked status.

### Tranche 7 non-goals

- [ ] Do not introduce raw arbitrary command execution.
- [ ] Do not install dependencies.
- [ ] Do not replace `project_setup` as the builder-contract scaffold authority.
- [ ] Do not permanently delete files by default.
- [ ] Do not mutate `.dev-tools/` internals unless a future tool explicitly
      supports that maintenance mode.

### Previous source tranche (parked)

- [x] Add `local_agent_bootstrap`.
- [x] Aggregate host probe, boundary audit, command profile, dependency check,
      latest journal entries, and relevant constraints.
- [x] Emit JSON or Markdown launch packet without writing by default.
- [x] Optional writes go only to ignored runtime/exports.
- [x] Mark Local Agent Operations satisfied in `NORTHSTARS.md`.
- [x] Move completed sys-ops items out of active TODO.
- [x] Append final `DEV_LOG` closeout with validation and `spiral` classification.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [x] Add `secret_surface_audit`.
- [x] Detect obvious committed secrets and risky `.env` exposure.
- [x] Redact discovered values in output.
- [x] Add `runtime_artifact_cleaner`.
- [x] Default cleanup to dry-run and restrict deletion to allowlisted generated artifacts.
- [x] Protect tracked files unless explicitly allowlisted and confirmed.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [x] Add `docker_ops` with `status`, `build`, `run_smoke`, `logs`, `tag`, and `push`.
- [x] Keep Docker contexts under the project root.
- [x] Require explicit confirmation for Docker `tag` and `push`.
- [x] Add `k8s_ops` with `context`, `validate`, `dry_run`, `apply`, `status`, `logs`, and `attach_instructions`.
- [x] Require explicit confirmation for live Kubernetes `apply`.
- [x] Use `_v2-pod/` for build/run and manifest validation fixtures.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [x] Add `dev_server_manager`.
- [x] Allow only command IDs emitted by `project_command_profile`.
- [x] Track launched processes in gitignored runtime state.
- [x] Write logs under ignored runtime/log paths.
- [x] Add smoke-test fixture coverage for start/status/tail/stop/health.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [x] Add `dependency_env_check`.
- [x] Extend `project_command_profile` with command metadata needed by
      `dev_server_manager`, `docker_ops`, and `k8s_ops`.
- [x] Add smoke-test fixture coverage proving readiness checks do not install
      dependencies or mutate the project.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [x] Add `host_capability_probe`.
- [x] Add `workspace_boundary_audit`.
- [x] Add `project_command_profile`.
- [x] Add `process_port_inspector`.
- [x] Register all four tools in `tool_manifest.json` and `src/mcp_server.py`.
- [x] Add smoke-test coverage and confirm MCP lists all 31 tools.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.

### Operational container follow-up

- [x] Verify headless install path works without a display server. The
      existing `src/tools/sidecar_install.py` uses `standard_main` and
      accepts `python sidecar_install.py run --input-json '{...}'`. No new
      `--headless` flag on `install.py` was needed; `install.py` stays
      GUI-only and `sidecar_install.py` is the canonical CLI surface.
- [x] Draft `_v2-pod/Dockerfile` (Python 3.11-slim base, COPY embedded
      sidecar into `/opt/dev-tools/`, entrypoint installs into `/workspace`).
- [x] Draft `_v2-pod/entrypoint.sh` (idempotent install + smoke + MCP launch).
- [x] Draft `_v2-pod/.dockerignore` (skip runtime journal state and pyc).
- [x] Draft `_v2-pod/k8s/deployment.yaml` — single-replica Deployment with
      ephemeral default and a commented PVC opt-in path.
- [x] Document model decisions in `_v2-pod/README.md`:
      - **Persistence:** ephemeral default; PVC opt-in via the commented
        block in the Deployment manifest.
      - **Project source:** project mounted at runtime as `/workspace`
        (defaults to empty volume → fresh install). Project-baked-in is
        deferred until there's a concrete reason to bake one project per
        image.
- [x] Verify `docker build` from `_v2-pod/` succeeds. Image
      `devtools-pod:v2` builds clean (~10s, stdlib-only).
- [x] Verify the resulting image runs end-to-end: entrypoint installs
      sidecar into `/workspace`, smoke test passes 39/39, MCP server
      enumerates 27 tools and launches.
- [x] Validate `k8s/deployment.yaml` parses as valid YAML with the
      expected Deployment shape (kind=Deployment, replicas=1,
      image=devtools-pod:v2).
- [ ] Run `kubectl apply -f _v2-pod/k8s/deployment.yaml` against a real
      cluster (kind/minikube/Docker Desktop k8s) and confirm the pod
      reaches Ready and `kubectl attach` reaches the MCP server. Pending
      a running cluster — `kubectl version --client` works, but no
      cluster API was reachable at validation time.
- [ ] Push `devtools-pod:v2` to a registry (Docker Hub or GHCR) so the
      image can be pulled by clusters other than the build host. Image
      reference in `k8s/deployment.yaml` will need updating from
      `devtools-pod:v2` to e.g. `ghcr.io/jacobmentalconstruct/devtools-pod:v2`
      at that point.

### Explicit non-goals for this tranche

- [x] Do not add raw unrestricted terminal parity.
- [ ] Do not install dependencies or apply Kubernetes resources.
- [ ] Do not introduce third-party Python dependencies.

### Previous tranche (parked)

- [x] Strangler finalization — root identity collapsed to single-purpose
      installer; `src/launch_ui.py`, `src/ui/`, `run-ui.*` purged.
- [x] Privacy hardening — `.gitignore` extended; tracked content audited.
- [x] Park doctrine gaps closed — Validation + Classification added to the
      strangler DEV_LOG entry; container tranche opened in this file.

---

## Near-term follow-up

- [x] Run final release-candidate verification after reference material purge.
- [x] Commit the clean release-candidate state.

---

## Longer-horizon work

- [x] Build a repo-safe search fallback tool for Windows environments that detects `rg` permission/app-bundle failures and cleanly falls back to native search instead of triggering awkward security-bypass behavior or brittle manual recovery.
- [x] Shape the local-agent sys-ops layer as the next post-RC northstar:
      `host_capability_probe`, `workspace_boundary_audit`,
      `project_command_profile`, `process_port_inspector`, and then
      dev-server/Docker/Kubernetes wrappers.
- [x] Implement Tranche 1: read-only host/workspace/command/process
      introspection tools.
- [x] Implement Tranche 2: dependency readiness and command-profile IDs.
- [x] Implement Tranche 3: guarded dev-server management.
- [x] Implement Tranche 4: Docker and Kubernetes operation wrappers.
- [x] Implement Tranche 5: secret audit and runtime artifact cleanup.
- [x] Implement Tranche 6: local-agent bootstrap and sys-ops northstar closeout.

---

## Known technical debt

- [x] Toolbox-level deferred ideas are tracked in the docs-first continuity packet for this prototype.
- [x] The toolbox continuity packet is sufficient for release-candidate handoff.
- [x] The installed sidecar flow no longer carries old reference bundles by default.
- [x] Transitional authority artifacts are no longer part of the active release shape.

---

## Compliance checklist

- [x] `_docs/ARCHITECTURE.md` exists and reflects current truth
- [x] `_docs/WE_ARE_HERE_NOW.md` is current
- [x] `_docs/builder_constraint_contract.md` exists
- [x] `_docs/DEV_LOG.md` is being appended meaningfully
- [x] `_docs/_journalDB/` and `_docs/_AppJOURNAL/` exist as gitignored runtime surfaces (generated on demand by `journal_init`; not part of the shipped source state)
