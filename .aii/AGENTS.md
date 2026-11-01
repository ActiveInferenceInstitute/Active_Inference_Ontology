# Agent guide — .aii/

InstituteOS sidecar for this repository (the reference exemplar). Read [`README.md`](README.md) first.

## For agents
- `config.yaml` is the **single source of truth** for this repo's InstituteOS metadata;
  keep it valid against `aii-sidecar/v1` (`aii_platform.aii_sidecar`).
- Only curated fields belong here — never duplicate GitHub-API facts (stars, size, language).
- `affiliation`: `institute` for Institute-owned work, `ecosystem` for external/affiliated.
- Declare key products in `artifacts[]` (paths are validated to exist) and connections in
  `ecosystem.relations[]` (targets must be `owner/repo`).
- Bump `meta.sidecar_version` + `meta.updated` on any change.
- The sidecar is **standalone** — it must validate and make sense without the parent monorepo.

## Validate / score

The authoritative validator lives in the InstituteOS platform kernel package
(`aii_platform.aii_sidecar`). That environment is private, so the check is not part of the
public GitHub workflow; see `docs/build-and-validation.md`.

```
python -m aii_platform.aii_sidecar.validate <repo>                   # OK / problems
python -m aii_platform.aii_sidecar.validate <repo> --completeness    # + score & gaps
```

The public regression suite keeps a structural check of this sidecar (schema marker,
required sections, existing paths, relation targets). The repository's ontology content and
generated artifacts are checked independently with `python3 scripts/ontology.py validate --strict`.
