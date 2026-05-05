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
- The local-agent sys-ops northstar, Safe Text Workspace Operations, Private
  Git Workspace Operations, and the Tranche 9 local sidecar agent safe floor
  are closed. The active source horizon is now hardening the local agent:
  richer recovery, evidence checks, run workspaces, and human UX polish.

---

## Current state

**Tranche 9 complete as a safe floor. Next: harden the local sidecar agent.**

Tranche 9 implemented `local_sidecar_agent`: a stdlib-first, Ollama-backed
runtime that bootstraps project context, routes model-produced tool calls
through an allowlisted catalog, validates schemas, stops before unconfirmed
mutations, writes ignored runtime session/audit state, validates touched files,
journals turns, and checkpoints through `git_private_workspace`.

`project_setup` remains the builder-contract scaffold authority. The local
agent floor deliberately avoids raw terminal or unrestricted filesystem parity;
future work should harden the agent loop rather than widen authority.

### Active tasks

- [ ] Add richer recovery-pattern detection and a recovery model role.
- [ ] Add evidence pass and filesystem-claim guardrails for final summaries.
- [ ] Add disposable run-workspace support for future verification tools.
- [ ] Expand human decision UX beyond booleans into named multiple-choice
      approvals.
- [ ] Add optional interactive/streaming CLI mode for long-running live Ollama
      turns.
- [ ] Evaluate whether any dependency-install or CLI-in-sandbox features belong
      in a later, separate tranche; keep them out of the default agent floor.
- [ ] Keep docs and smoke coverage aligned as the agent hardens.

### Previous source tranche (parked): Tranche 9 Local Sidecar Agent Runtime

- [x] Add a stdlib-first local sidecar agent entrypoint.
- [x] Use Ollama over localhost HTTP with configurable model names, endpoint,
      and timeouts.
- [x] Prefer Qwen coder-family models for structured JSON/tool-call planning
      and Qwen human-interface models for user-facing responses.
- [x] Load `local_agent_bootstrap` before planning.
- [x] Use only allowlisted toolbox tools; do not expose raw shell execution.
- [x] Resolve all paths under the chosen `project_root`.
- [x] Use a fixed floor loop: bootstrap, boundary audit, setup audit, model
      turn, guarded tool execution, validation, checkpoint, journal.
- [x] Validate model-produced tool calls against schemas before execution.
- [x] Stop for approval before unconfirmed mutating tools.
- [x] Store session state under ignored `.dev-tools/runtime/local_agent/`.
- [x] Add mock-Ollama and temp-project smoke coverage proving the agent can
      call safe text tools, validate output, checkpoint through private Git,
      and stop for human approval when required.
- [x] Update README, agent guide, architecture, northstars, TODO, onboarding,
      and dev log.
- [x] Write/export the Tranche 9 journal entry and commit the tranche.

### Previous source tranche (parked): Tranche 8 Private Git Workspace Operations

- [x] Add `git_private_workspace`.
- [x] Support `status`, `init`, `add`, `commit`, `branch`, `checkout`, `pull`,
      and `push`.
- [x] Store the private gitdir under ignored
      `.dev-tools/runtime/private_git/` and use the chosen `project_root` as
      the worktree.
- [x] Refuse to operate outside `project_root`.
- [x] Exclude `.git/`, `.dev-tools/runtime/`, obvious caches, and risky secret
      surfaces by default.
- [x] Require `confirm: true` for every mutating action.
- [x] Require a non-empty commit message for commits.
- [x] Require explicit private-remote configuration before push or pull.
- [x] Block `remote_name=origin` unless explicitly allowed.
- [x] Add temp-fixture smoke coverage proving private init/add/commit/branch
      does not create or mutate a project-root `.git`.
- [x] Add local-bare-remote smoke coverage for push/pull without network.
- [x] Register the tool in `tool_manifest.json` and `src/mcp_server.py`.
- [x] Extend `local_agent_bootstrap` to include private Git status in launch
      packets.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [x] Write a Tranche 8 journal entry and export the journal for operator
      visibility.
- [x] Run final verification and commit the implementation tranche.

### Previous source tranche (parked): Tranche 7 Safe Text Workspace Operations

- [x] Add `text_file_reader`.
- [x] Add `text_file_writer`.
- [x] Add `directory_scaffold`.
- [x] Add `text_file_validator`.
- [x] Add `file_move_guarded`.
- [x] Add `file_delete_guarded`.
- [x] Register the new tools in `tool_manifest.json` and `src/mcp_server.py`.
- [x] Extend `src/smoke_test.py` with temp-fixture coverage for read, write,
      scaffold, validate, guarded move, and quarantine delete behavior.
- [x] Update README, agent guide, architecture, northstars, TODO, and dev log.
- [x] Write a Tranche 7 journal entry and export the journal for operator
      visibility.
- [x] Run final verification and commit the implementation tranche.

### Tranche 7 tool contract (satisfied)

- [x] `text_file_reader`: bounded text reads under `project_root`; report size,
  line count, newline style, and content/excerpt while rejecting outside-root,
  binary, or oversized files unless explicitly bounded.
- [x] `text_file_writer`: create, overwrite, or append text payloads with
  `confirm: true`; require `overwrite: true` for replacement; support
  `create_dirs: true`; block `.dev-tools/` internals by default.
- [x] `directory_scaffold`: apply a declarative directory/file manifest; dry-run by
  default; require `confirm: true` to write; keep every entry under the project
  root; skip existing files unless `overwrite: true`.
- [x] `text_file_validator`: validate text surfaces without third-party
  dependencies: Python via `ast.parse`, JSON via `json.loads`, TOML via
  `tomllib`, and basic readability/size/null-byte checks for markdown, text,
  shell, batch, CSS, HTML, and YAML-like files.
- [x] `file_move_guarded`: move or rename files/directories under the project root
  with `confirm: true` plus a non-empty `reason`; refuse overwrites unless
  explicitly enabled; protect `.dev-tools/` and tracked files by default.
- [x] `file_delete_guarded`: quarantine instead of permanently deleting by moving
  targets to ignored `.dev-tools/runtime/trash/`; require `confirm: true` plus
  a non-empty `reason`; write a receipt with original path, timestamp, reason,
  actor, and tracked status.

### Tranche 7 non-goals (preserved)

- [x] Do not introduce raw arbitrary command execution.
- [x] Do not install dependencies.
- [x] Do not replace `project_setup` as the builder-contract scaffold authority.
- [x] Do not permanently delete files by default.
- [x] Do not mutate `.dev-tools/` internals unless a future tool explicitly
      supports that maintenance mode.

### Tranche 8 tool contract: Private Git Workspace Operations

Purpose: give the sidecar agent a private Git checkpoint layer before it becomes
autonomous. The agent should be able to save, branch, push, and pull its own
work without casually mutating the user's main project `.git`.

Satisfied tool surface:

- [x] Add `git_private_workspace`.
- [x] Support `status`, `init`, `add`, `commit`, `branch`, `checkout`, `pull`,
      and `push`.
- [x] Store the private gitdir under ignored
      `.dev-tools/runtime/private_git/` and use the chosen `project_root` as
      the worktree.
- [x] Refuse to operate outside `project_root`.
- [x] Exclude `.git/`, `.dev-tools/runtime/`, obvious caches, and risky secret
      surfaces by default.
- [x] Require `confirm: true` for every mutating action.
- [x] Require a non-empty commit message for commits.
- [x] Require explicit private-remote configuration before push or pull.
- [x] Never push to the user's existing `origin` unless a future maintenance
      mode explicitly opts into that behavior.
- [x] Add temp-fixture smoke coverage proving private init/add/commit/branch
      does not create or mutate a project-root `.git`.
- [x] Add local-bare-remote smoke coverage for push/pull without network.
- [x] Update README, agent guide, architecture, northstars, TODO, onboarding,
      and dev log.
- [x] Write/export the Tranche 8 journal entry and commit the tranche.

### Satisfied Tranche 9: Local Sidecar Agent Runtime

Purpose: implement the first local desktop sidecar agent after it has the
operating envelope, safe file primitives, and private Git checkpoints it needs.

Implemented safe floor:

- [x] Add a stdlib-first local agent entrypoint, `local_sidecar_agent`,
      runnable from the installed sidecar.
- [x] Use Ollama over localhost HTTP; default models should be configurable,
      with Qwen coder-family models favored for structured JSON/tool planning
      and Qwen human-interface models favored for user-facing responses.
- [x] Load `local_agent_bootstrap` before planning.
- [x] Use only allowlisted toolbox tools; do not expose raw terminal execution.
- [x] Resolve all project paths under the chosen `project_root`.
- [x] Use a fixed scaffolded loop so the model does not infer the builder
      contract: bootstrap, audit, setup, plan, act, verify, checkpoint, park.
- [x] Validate model-produced tool calls against schemas before execution.
- [x] Use approval-required status for high-risk steps and ambiguous decisions.
- [x] Require human confirmation before mutating tools, private Git push/pull,
      delete/quarantine, dev-server lifecycle changes, Docker/Kubernetes
      side effects, or broad cleanup.
- [x] Store session state under ignored `.dev-tools/runtime/local_agent/`.
- [x] Add mock-Ollama and temp-project smoke coverage proving the agent can
      plan, call safe text tools, validate output, checkpoint through private
      Git, and stop for human approval when required.
- [x] Update README, agent guide, architecture, northstars, TODO, onboarding,
      and dev log.
- [x] Write/export the Tranche 9 journal entry and commit the tranche.

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
- [x] Implement Tranche 7: safe text workspace operations.
- [x] Implement Tranche 8: private Git workspace operations.
- [x] Implement Tranche 9: local sidecar agent runtime.

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
