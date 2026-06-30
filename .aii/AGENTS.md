# Agent guide — .aii/

InstituteOS sidecar for this repository (the reference exemplar). Read [`README.md`](README.md) first.

## For agents
- `config.yaml` is the **single source of truth** for this repo's InstituteOS metadata;
  keep it valid against `aii-sidecar/v1` (`instituteos.platform.aii_sidecar`).
- Only curated fields belong here — never duplicate GitHub-API facts (stars, size, language).
- `affiliation`: `institute` for Institute-owned work, `ecosystem` for external/affiliated.
- Declare key products in `artifacts[]` (paths are validated to exist) and connections in
  `ecosystem.relations[]` (targets must be `owner/repo`).
- Bump `meta.sidecar_version` + `meta.updated` on any change.
- The sidecar is **standalone** — it must validate and make sense without the parent monorepo.

## Validate / score
```
python -m instituteos.platform.aii_sidecar.validate <repo>          # OK / problems
python -m instituteos.platform.aii_sidecar.validate <repo> --completeness   # + score & gaps
```
This sidecar meets the 100% completeness standard (`python -m instituteos.platform.aii_sidecar doctor <repo>`).
