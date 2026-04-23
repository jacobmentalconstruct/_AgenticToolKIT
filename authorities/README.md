# Packed Authorities

Toolbox-resident codices that are packaged into SQLite artifacts and executed
through managed runtime hydration.

These are not normal vendable packages copied into target projects. They stay
inside `.dev-tools` and let builders/agents operate from a packed authority
instead of a live source tree.

## Current Authority

| Authority | Purpose |
|-----------|---------|
| `_builderset-authority/` | Packed SQLite authority for `AgenticToolboxBuilderSET` with runtime/reference content classes and cache-backed execution |
