# BuilderSET Authority Artifacts

This folder stores the packed BuilderSET authority outputs:

- `builderset_authority.sqlite3` — canonical packed authority DB
- `builderset_authority_manifest.json` — human/agent onboarding manifest for
  the current build

The DB preserves both runtime-executable and reference-only content. The live
BuilderSET repo is only needed when rebuilding the artifact from a fresh source
snapshot.
