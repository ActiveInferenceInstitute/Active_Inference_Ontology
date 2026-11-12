# InstituteOS integration — Active Inference Ontology

How this repository participates in the Active Inference Institute / InstituteOS ecosystem.
This file is InstituteOS-specific and lives in the sidecar, not in the repo's own `docs/`.

## Role

The **canonical controlled vocabulary** for Active Inference / FEP concepts. Downstream
Institute work (the Journal, courses, the website, analyses) references ontology terms by
tag. The sidecar declares this with `ecosystem.relations` (`referenced-by` the Journal).

## Products InstituteOS consumes

- `ontology.source.json` — the structured source with stable ids and explicit metadata.
- `ontology.json` — the version 2 machine-readable export.
- `releases.json` — the hashed release manifest, including archived versions.
- `site/index.html` — the generated dependency-free browser surface.
- `GNN/` — the generated bridge to the GNN pipeline's `ActInfOntologyAnnotation`
  vocabulary and its reviewed declared-label input.
- `docs/manuscript/` — the template-compatible manuscript source and generated publication artifacts.

These are declared as artifacts in the modular sidecar; the sidecar validator confirms the
integration paths exist. That validator ships in the private platform kernel package, so it
runs outside public CI, where a dependency-free structural check covers the same paths. The
ontology CLI separately validates content and generated artifact freshness.

## Completeness

The sidecar is modular: the core `config.yaml` deep-merges four fragments —
`config.d/ecosystem.yaml` (related repositories and links), `config.d/artifacts.yaml`
(key products), `config.d/docs.yaml` (documentation index and `meta.updated`), and
`config.d/tasks.yaml` (runnable tasks). Its structural completeness is
checked by InstituteOS; ontology content and generated-artifact freshness are checked by
`python3 scripts/ontology.py validate --strict`; manuscript structure and rendered-output
integrity are checked by `python3 scripts/manuscript.py validate --strict`. Licensed
`CC-BY-4.0`.

## Maintaining this sidecar

- Keep `config.yaml` valid: `python -m aii_platform.aii_sidecar.validate <repo>`.
- Bump `meta.sidecar_version` + `meta.updated` when you change sidecar content.
- The sidecar is standalone — it must make sense in this repo without the InstituteOS monorepo.
