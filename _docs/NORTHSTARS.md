# Northstars

_Last updated: 2026-04-29._

This file records the higher-level capability direction for `.dev-tools`.

It is not the active task list. Use [`TODO.md`](C:/Users/jacob/Documents/_AppDesign/_LivePROJECTS/.dev-tools/_docs/TODO.md) for bounded backlog work.

---

## Northstar Direction

- Keep `.dev-tools` legible, vendable, and project-agnostic.
- Give human developers and agents a shared toolbox with explicit trust boundaries.
- Reduce reliance on external host-only agent powers by growing more of the needed capabilities into toolbox-usable surfaces.

---

## Needed Capability Parity

These are notable capabilities currently available through Codex-hosted tooling that we should progressively mirror with toolbox tools or packages that agents can use more directly inside `.dev-tools` and vendored project contexts.

- Shell / terminal execution parity
  Goal: agent-usable tools for safe command execution, output capture, and environment-aware fallback behavior.
- File patching parity
  Goal: toolbox-native patch/apply flows for reliable structured edits.
- Parallel local tool use parity
  Goal: orchestration helpers that let agents run multiple safe local inspections in one pass.
- Web browsing / search / open parity
  Goal: research and fetch tools that can retrieve and inspect web resources when appropriate.
- Image generation / editing parity
  Goal: visual asset generation and transformation surfaces agents can invoke deliberately.
- Local image viewing parity
  Goal: tooling for reading or inspecting local screenshots and visual artifacts.
- Terminal output inspection parity
  Goal: agent-readable access to recent terminal state and command output.
- Planning tracker parity
  Goal: a structured planning/update surface for long-running work.
- Automation / recurring task parity
  Goal: tooling for scheduled checks, follow-ups, and recurring agent work.
- MCP resource discovery / read parity
  Goal: toolbox-visible discovery and reading of MCP resource surfaces.
- Sub-agent / delegation parity
  Goal: bounded delegation or worker-orchestration surfaces for agent teamwork.
- Node REPL / JavaScript execution parity
  Goal: an agent-usable JavaScript execution surface parallel to the Python-oriented tooling already present.

---

## Notes

- Not every Codex-hosted capability should be cloned literally.
- The northstar is capability coverage, not perfect interface mimicry.
- New parity tools should remain portable, explicit, and safe within the toolbox trust model.
- First parity win: `repo_search` now gives agents a project-local search surface
  with an `rg` fast path and native fallback for Windows-safe inspection.
