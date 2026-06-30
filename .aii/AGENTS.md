# Agent guide — .aii/

InstituteOS sidecar for this repository. Read [`README.md`](README.md) first.

## For agents
- `config.yaml` is the **single source of truth** for this repo's InstituteOS metadata.
  Keep it valid against `aii-sidecar/v1` (`instituteos.platform.aii_sidecar`).
- Do **not** duplicate GitHub-API facts (stars, size, language) here — only curated fields
  (affiliation, category, status, ecosystem links, tags).
- `affiliation`: `institute` for Institute-owned work, `ecosystem` for external/affiliated.
- The sidecar is **standalone** — it must validate and make sense without the parent monorepo.
- Validate with: `python -m instituteos.platform.aii_sidecar.validate <repo>` (or the reader API).
