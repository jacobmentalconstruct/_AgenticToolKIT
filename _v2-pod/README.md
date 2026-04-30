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
├── Dockerfile         # container definition for the pod image
├── .dockerignore      # excludes runtime journal state from the build context
├── entrypoint.sh      # idempotent install + smoke + MCP launch
├── k8s/
│   └── deployment.yaml  # single-replica Deployment, ephemeral default
└── .dev-tools/        # GITIGNORED — installed sidecar, used as agent toolbelt
                       # while working in this folder. Treat as read-only
                       # dependency. Do NOT modify these files; modify the
                       # parent repo's source instead and reinstall.
```

## Build & run

### 1. Refresh the embedded sidecar (any time the parent toolkit changes)

From the parent repo root:

```
python src/tools/sidecar_install.py run --input-json \
  '{"target_project_root": "_v2-pod", "overwrite": true}'
```

This drops a fresh, current copy of the toolkit at `_v2-pod/.dev-tools/`. The
copy is gitignored — only the wrapper artifacts in `_v2-pod/` are tracked.

### 2. Build the image

From inside `_v2-pod/`:

```
docker build -t devtools-pod:v2 .
```

Build context is `_v2-pod/` itself; the Dockerfile copies the embedded
`.dev-tools/` into `/opt/dev-tools` inside the image. The parent repo is not
touched by the build.

### 3. Run a single pod locally (for smoke verification)

```
docker run --rm -it devtools-pod:v2
```

The entrypoint will:
1. Install a fresh sidecar into the (ephemeral) `/workspace` inside the pod.
2. Run `smoke_test.py` against it. Failure aborts the pod immediately.
3. `exec` into `python /workspace/.dev-tools/src/mcp_server.py`.

### 4. Deploy to Kubernetes

```
kubectl apply -f k8s/deployment.yaml
```

To attach an agent to the running pod's MCP stdio:

```
kubectl attach -ti deploy/devtools-pod
```

To scale to N parallel ephemeral agent sandboxes (each with its own fresh
`/workspace`):

```
kubectl scale deploy/devtools-pod --replicas=N
```

## Model decisions

- **Persistence: ephemeral by default.** Each pod's `/workspace` is created
  fresh; agent work disappears on pod death. To persist across restarts,
  uncomment the `volumeMounts` + `volumes` blocks in `k8s/deployment.yaml`
  and provision a PVC named `devtools-workspace`.
- **Project source: mounted at runtime.** The image does not bake a project
  in. The agent works on whatever `/workspace` it's given (empty volume by
  default → fresh install; PVC → persistent project). Project-baked-in
  images are deferred until there's a concrete reason to bake one project
  per image.
- **MCP transport: stdio.** No port exposure. Use `kubectl attach` for
  interactive access, or sidecar an HTTP shim at the Deployment level if you
  need network reachability.
- **Stdlib-only.** No `apt install` and no extra Python packages — same
  discipline as the parent toolkit.

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
