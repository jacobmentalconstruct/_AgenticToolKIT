#!/usr/bin/env bash
#
# Pod entrypoint for the .dev-tools v2 image.
#
# Behavior:
#   1. If /workspace has no .dev-tools sidecar, install one from the toolkit
#      copy at /opt/dev-tools using the headless sidecar_install CLI.
#   2. Run the smoke test against the installed sidecar so a broken pod
#      reports unhealthy instead of accepting agent traffic silently.
#   3. exec into the MCP server so PID 1 is the actual workload.
#
# Idempotent: existing /workspace/.dev-tools (e.g., from a PVC) is left alone.

set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
TOOLKIT_SRC="${TOOLKIT_SRC:-/opt/dev-tools}"

if [ ! -d "$WORKSPACE/.dev-tools" ]; then
  echo "[entrypoint] Installing .dev-tools sidecar into $WORKSPACE..."
  python "$TOOLKIT_SRC/src/tools/sidecar_install.py" run --input-json \
    "{\"target_project_root\": \"$WORKSPACE\", \"source_toolbox_root\": \"$TOOLKIT_SRC\", \"overwrite\": true}" \
    > /tmp/sidecar_install.log
  echo "[entrypoint] Sidecar install complete."
else
  echo "[entrypoint] Existing .dev-tools sidecar found at $WORKSPACE/.dev-tools — leaving as-is."
fi

echo "[entrypoint] Running smoke test..."
if ! python "$WORKSPACE/.dev-tools/src/smoke_test.py" > /tmp/smoke.log 2>&1; then
  echo "[entrypoint] Smoke test FAILED. Last 40 lines of /tmp/smoke.log:"
  tail -40 /tmp/smoke.log
  exit 1
fi
echo "[entrypoint] Smoke test passed."

echo "[entrypoint] Launching MCP server..."
exec python "$WORKSPACE/.dev-tools/src/mcp_server.py"
