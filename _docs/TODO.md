# Project Backlog

_Last updated: 2026-04-30._

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
- The active post-RC source horizon is local-agent sys-ops tooling: safe,
  structured host/project operations for a desktop-first agent.

---

## Current tranche

**Tranche 4 — Docker and Kubernetes operation wrappers.**

Tranche 3 is implemented and in the parking path. The next source tranche
should add `docker_ops` and `k8s_ops`, using `_v2-pod/` as the primary fixture
and preserving explicit confirmation for side effects such as push, tag, and
live Kubernetes apply.

### Active tasks

- [ ] Add `docker_ops` with `status`, `build`, `run_smoke`, `logs`, `tag`, and `push`.
- [ ] Keep Docker contexts under the project root.
- [ ] Require explicit confirmation for Docker `tag` and `push`.
- [ ] Add `k8s_ops` with `context`, `validate`, `dry_run`, `apply`, `status`, `logs`, and `attach_instructions`.
- [ ] Require explicit confirmation for live Kubernetes `apply`.
- [ ] Use `_v2-pod/` for build/run and manifest validation fixtures.
- [ ] Update README, agent guide, architecture, northstars, TODO, and dev log.

### Previous source tranche (parked)

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
- [ ] Implement Tranche 4: Docker and Kubernetes operation wrappers.
- [ ] Implement Tranche 5: secret audit and runtime artifact cleanup.
- [ ] Implement Tranche 6: local-agent bootstrap and sys-ops northstar closeout.

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
