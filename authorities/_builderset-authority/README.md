# _builderset-authority

Packed BuilderSET authority that turns the live `AgenticToolboxBuilderSET`
codex into a toolbox-resident SQLite artifact plus managed runtime cache.

## What It Contains

- `artifacts/builderset_authority.sqlite3` — the packed authority DB
- `artifacts/builderset_authority_manifest.json` — on-disk onboarding manifest
- runtime-executable content for BuilderSET MCP/UI/catalog surfaces
- reference-only content for docs, smoke tests, finals, archives, outputs, and
  other codex material that should stay queryable/exportable without default
  hydration

## Primary Tool Surface

The authority is operated from builder tools in `src/tools/`:

- `builderset_authority_build`
- `builderset_authority_manifest`
- `builderset_authority_query`
- `builderset_authority_prepare_runtime`
- `builderset_authority_export`
- `builderset_authority_launch`

## Runtime Model

- The live BuilderSET repo is treated as an upstream build source only.
- The packed DB is the portable authority artifact.
- Runtime files hydrate on demand into `.dev-tools/runtime/_builderset-authority/<build_id>/`.
- Reference-only files remain in SQLite until queried or exported.

## Typical Use

```powershell
python src/tools/builderset_authority_build.py run --input-json "{}"
python src/tools/builderset_authority_prepare_runtime.py run --input-json "{}"
python src/tools/builderset_authority_launch.py run --input-json "{\"surface\":\"mcp\",\"action\":\"probe\"}"
```
