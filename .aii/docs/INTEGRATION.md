# InstituteOS integration — Active Inference Ontology

How this repository participates in the Active Inference Institute / InstituteOS ecosystem.
This file is InstituteOS-specific and lives in the sidecar, not in the repo's own `docs/`.

## Role

The **canonical controlled vocabulary** for Active Inference / FEP concepts. Downstream
Institute work (the Journal, courses, the website, analyses) references ontology terms by
tag. The sidecar declares this with `ecosystem.relations` (`referenced-by` the Journal).

## Products InstituteOS consumes

- `ontology.json` — the machine-readable export (term → tag, definitions, connections).
- `releases.json` — release manifest (current `v5`; archived versions under `Archived versions/`).
- `Ontology_v5_May_25_2023.csv` — the human-curated source of truth.

These are declared as `artifacts` in `config.yaml`; the validator confirms each path exists.

## Completeness

This sidecar meets the **100% completeness standard** (`doctor` → `standard met: True`).
It is **fully modular**: the core `config.yaml` deep-merges `config.d/ecosystem.yaml`,
`config.d/artifacts.yaml`, and `config.d/tasks.yaml`. Licensed `CC-BY-4.0` (auto-detected
from `LICENSE`).

## Maintaining this sidecar

- Keep `config.yaml` valid: `python -m instituteos.platform.aii_sidecar.validate <repo>`.
- Bump `meta.sidecar_version` + `meta.updated` when you change sidecar content.
- The sidecar is standalone — it must make sense in this repo without the InstituteOS monorepo.
