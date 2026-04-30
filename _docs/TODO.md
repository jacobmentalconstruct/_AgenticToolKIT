# Project Backlog

_Last updated: 2026-04-29._

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

---

## Current tranche

**Container packaging — Kubernetes-wrapped v2 in `_v2-pod/`.**

The previous tranche (release-candidate cleanup + strangler finalization) is
parked. All current work happens inside the isolated `_v2-pod/` workspace so
the parked root prototype is not disturbed.

### Active tasks

- [ ] Add `--headless --target <path>` CLI mode to `install.py` so it can run
      without a display server (required for `docker build` RUN steps).
- [ ] Draft `_v2-pod/Dockerfile` (Python 3.11-slim base, COPY toolbox into
      `/opt/dev-tools/`, run headless install against `/workspace`).
- [ ] Draft `_v2-pod/k8s/deployment.yaml` — single-replica Deployment first;
      worry about parallel replicas only after one pod runs cleanly.
- [ ] Decide and document: ephemeral pod vs PVC-mounted `/workspace` for
      journal/output persistence.
- [ ] Decide and document: project-baked-in vs project-mounted-at-runtime
      pod model. Pick one for v2; defer the other.
- [ ] Verify `docker build` succeeds locally from `_v2-pod/` and the
      resulting image runs `mcp_server.py` end-to-end.

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
