# _v2-pod — Kubernetes-wrapped `.dev-tools` v2 build workspace

This folder is an **isolated build space** for wrapping the parked root
`.dev-tools` prototype into a Kubernetes-friendly container image.

## Why this folder exists

The strangler tranche left the root toolbox parked as a clean single-purpose
prototype. To package it as a pod-friendly container without disturbing that
parked state, all v2 work happens inside this folder.

When v2 is ready, the user may move this folder out of the parent repo and
graduate it to its own v2.0 release. Until then it lives here as a
self-contained sandbox.

## Layout

```
_v2-pod/
├── README.md          # this file
├── .dev-tools/        # GITIGNORED — installed sidecar, used as agent toolbelt
│                      # while working in this folder. Treat as read-only
│                      # dependency. Do NOT modify these files; modify the
│                      # parent repo's source instead and reinstall.
├── Dockerfile         # (pending) container definition for the pod image
└── k8s/               # (pending) Kubernetes manifests
    └── deployment.yaml
```

## Working rules

1. **Do not edit the parent repo's source from inside this folder.** The
   parent root is parked. If you need to change toolkit source, park this
   tranche, edit at root, then restart this tranche.
2. **`_v2-pod/.dev-tools/` is gitignored.** It is just a fresh install of the
   parent repo's current toolkit. Reinstall it any time by re-running the
   parent's `install.py --target _v2-pod` (once headless mode lands), or
   manually via `python ../src/tools/sidecar_install.py` from this folder.
3. **Track only the wrapper artifacts** — Dockerfile, k8s manifests,
   pod-specific scripts, and any documentation. The toolkit itself stays in
   the parent.
4. **Stdlib only.** Match the parent's discipline — no new Python
   dependencies in the pod image beyond what the toolkit already needs.

## Current tranche tasks

See `../_docs/TODO.md` "Current tranche" for the live task list.

The first concrete move is adding a `--headless --target <path>` CLI mode to
the parent's `install.py` so the Dockerfile RUN step can install the sidecar
without a display server.

## How to use the installed sidecar

The installed `.dev-tools/` inside this folder is the agent's toolbelt while
working here. From this folder:

```
python .dev-tools/src/mcp_server.py        # MCP surface for an agent
python .dev-tools/src/smoke_test.py        # verify the install
python .dev-tools/src/tools/repo_search.py run --input-json '{...}'
```

If the sidecar drifts from the parent (e.g., parent gets a fix), reinstall
this folder's copy.
