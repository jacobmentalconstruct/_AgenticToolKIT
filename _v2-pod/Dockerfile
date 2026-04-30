# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/jacobmentalconstruct/_AgenticToolKIT"
LABEL org.opencontainers.image.description=".dev-tools agentic toolkit, packaged for Kubernetes pod use"
LABEL org.opencontainers.image.licenses="Source-Available-Reference"

# Toolkit canonical copy lives at /opt/dev-tools.
#
# The .dev-tools/ directory in the build context comes from running
# `python ../src/tools/sidecar_install.py run --input-json '{"target_project_root": "_v2-pod"}'`
# at the parent repo root. It is deliberately COPY-ed (not bind-mounted) so the
# resulting image is self-contained and the pod has no runtime dependency on
# host files.
COPY .dev-tools /opt/dev-tools

# /workspace is the project the agent works on inside the pod. Empty by default
# (ephemeral pod model); PVC-mountable at deploy time for persistent state.
WORKDIR /workspace

# Idempotent entrypoint: installs a fresh sidecar into /workspace if missing,
# runs the smoke test, then launches the MCP server. Headless throughout —
# stdlib only, no display server, no extra apt packages.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# MCP defaults to stdio. Don't expose ports here; route attachment through
# `kubectl attach` or a sidecar HTTP shim at the manifest level.
ENTRYPOINT ["/entrypoint.sh"]
