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

**Container packaging — Kubernetes-wrapped v2 in `_v2-pod/`.**

The previous tranche (release-candidate cleanup + strangler finalization) is
parked. All current work happens inside the isolated `_v2-pod/` workspace so
the parked root prototype is not disturbed.

### Active tasks

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

- [ ] Do not modify the root prototype while v2 work is live. If a real
      bug surfaces in root, park v2, fix root, restart v2.
- [ ] Do not introduce new third-party Python dependencies — stdlib only,
      same as the parked root.
- [ ] Do not productionize Kubernetes (RBAC, secrets, ingress, monitoring)
      in this tranche. Goal is a working pod, not a hardened deployment.
- [ ] Do not rewrite the toolkit. v2 is a wrapper around the parked v1, not
      a re-architecture.

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
- [ ] Implement Tranche 1: read-only host/workspace/command/process
      introspection tools.
- [ ] Implement Tranche 2: dependency readiness and command-profile IDs.
- [ ] Implement Tranche 3: guarded dev-server management.
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
