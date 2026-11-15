# .aii — InstituteOS sidecar

This folder is the committed InstituteOS sidecar for **`ActiveInferenceInstitute/Active_Inference_Ontology`**.
It records curated institutional metadata that the GitHub
API cannot provide — identity, category, maturity, ecosystem relations, key artifacts,
provenance, and portable tasks — so InstituteOS can federate a unified view across
Institute repositories without touching this project's own content. The schema is
`aii-sidecar/v1`.

## Contents

| File | Purpose |
| --- | --- |
| [`config.yaml`](config.yaml) | Machine-readable metadata; the single source of truth. |
| [`readiness.json`](readiness.json) | Declared tier, baseline commit, and waivers for the AII readiness standard. |
| [`docs/`](docs/README.md) | Sidecar documents: the [`README.md`](docs/README.md) · [`AGENTS.md`](docs/AGENTS.md) folder guides, and [`INTEGRATION.md`](docs/INTEGRATION.md) — how this repository is federated, validated, and operated through InstituteOS. |
| [`README.md`](README.md) · [`AGENTS.md`](AGENTS.md) | Human and agent guidance for this folder. |

## Repository profile

| Field | Value |
| --- | --- |
| Repository | `ActiveInferenceInstitute/Active_Inference_Ontology` |
| Category | `ontology` |
| Status | `active` |
| Maturity | `released` |
| License | `CC-BY-4.0` |
| Default branch | `main` |
| Homepage | https://www.activeinference.org/home |
| Tags | `ontology`, `vocabulary`, `active-inference`, `free-energy-principle`, `controlled-vocabulary` |

## Capabilities

- structured-source
- csv-export
- json-export
- typed-relations
- release-integrity
- static-site
- manuscript-publication
- sumo-mapping
- gnn-vocabulary-bridge

## Portable tasks

| Task | Command | Working directory | Description |
| --- | --- | --- | --- |
| `validate` | `python3 scripts/ontology.py validate --strict` | `.` | Verify source, generated artifacts, release hashes, and contracts. |
| `test` | `python3 -m unittest discover -s tests -v` | `.` | Run the dependency-free regression suite. |
| `build` | `python3 scripts/ontology.py build` | `.` | Regenerate the version 2 JSON export. |
| `lint` | `./run.sh lint` | `.` | Static analysis with the repository's pinned ruff policy. |
| `docs` | `./run.sh docs` | `.` | Check documentation links, anchors, index coverage, and generated gate numbers. |
| `schema-check` | `python3 scripts/ontology.py schema-check` | `.` | Validate live documents against the published JSON Schemas. |
| `audit-csv` | `python3 scripts/ontology.py audit-csv Ontology_v5_May_25_2023.csv` | `.` | Report CSV shape, duplicate-label, and generated-ID diagnostics. |
| `report` | `python3 scripts/ontology.py report` | `.` | Print quality, integrity, and release validation results. |
| `site` | `python3 scripts/ontology.py site` | `.` | Regenerate the dependency-free browsable site. |
| `gnn-terms` | `python3 scripts/ontology.py gnn-terms` | `.` | Regenerate the GNN vocabulary bridge from the canonical source. |
| `manuscript-generate` | `python3 scripts/manuscript.py generate` | `.` | Generate manuscript variables, figures, tables, and resolved sections. |
| `manuscript-validate` | `python3 scripts/manuscript.py validate --strict` | `.` | Validate manuscript structure, references, figures, hashes, and rendered outputs. |
| `manuscript-render` | `python3 scripts/manuscript.py render --format all` | `.` | Render PDF, HTML, DOCX, and EPUB publication artifacts. |
| `manuscript-check` | `python3 scripts/manuscript.py check` | `.` | Verify manuscript freshness and publication manifest integrity. |

## Links

- **coda:** https://coda.io/@active-inference-institute/active-inference-ontology-website
- **docs:** docs/README.md
- **website:** https://www.activeinference.org/home

## Validate

The authoritative validator ships in the private `aii-platform` kernel:

```bash
python -m aii_platform.aii_sidecar.validate <repo> --completeness
python -m aii_platform.aii_sidecar docs <repo> --overwrite
python -m aii_platform.aii_sidecar.run <repo> --list
```

If the private environment is unavailable, review `config.yaml` as plain YAML and
check that every declared path exists in the repository.
