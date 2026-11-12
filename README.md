# Active Inference Ontology

A controlled vocabulary of Active Inference and Free Energy Principle concepts.
The v5 content release contains 429 terms; the repository publishes it through a
version 2 structured source, deterministic exports, explicit stable identities,
and typed relation records.

- **Content release:** v5 (May 25, 2023)
- **Source contract:** `active-inference-ontology/source/v2`
- **Export contract:** `active-inference-ontology/export/v2`
- **Live website:** <https://coda.io/@active-inference-institute/active-inference-ontology-website>
- **Institute information:** <https://www.activeinference.org/home>
- **Citation:** [10.5281/zenodo.7430332](https://doi.org/10.5281/zenodo.7430332) (Zenodo concept DOI; see [`CITATION.cff`](CITATION.cff))

## Documentation

- [`docs/README.md`](docs/README.md) — index of the repository documentation (source and export contracts, curation, releases, integration).
- [`TO-DO.md`](TO-DO.md) — scoped worklog of completed and deferred review items.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to propose changes and the acceptance gates.
- [`AGENTS.md`](AGENTS.md) — orientation for AI agents and automation.
- [`.aii/README.md`](.aii/README.md) — InstituteOS sidecar metadata for this repository.

## Repository surfaces

| Path | Role |
| --- | --- |
| [`ontology.source.json`](ontology.source.json) | Canonical structured source with stable IDs, metadata, and relations. |
| [`ontology.json`](ontology.json) | Generated version 2 machine-readable export. |
| [`Ontology_v5_May_25_2023.csv`](Ontology_v5_May_25_2023.csv) | Generated spreadsheet export. |
| [`ontology.toml`](ontology.toml) | Explicit paths, release metadata, and validation policy. |
| [`run.sh`](run.sh) | Gate entry point; its arms are the commands the public workflow runs. |
| [`scripts/ontology.py`](scripts/ontology.py) | Build, validation, reporting, diff, export, and site CLI. |
| [`scripts/manuscript.py`](scripts/manuscript.py) | Generate, validate, render, and hash the publication manuscript. |
| [`scripts/check_docs.py`](scripts/check_docs.py) | Documentation links, anchors, and index coverage gate. |
| [`scripts/validate_gnn_conformance.py`](scripts/validate_gnn_conformance.py) | Pinned-GNN parser conformance check (`.github/gnn-pin.json`). |
| [`scripts/report_gate.py`](scripts/report_gate.py) | Measures the gate arms and writes `docs/_generated/gate.md`. |
| [`schemas/`](schemas/) | Machine-readable source, export, and release-manifest schemas. |
| [`site/index.html`](site/index.html) | Generated dependency-free browsing surface. |
| [`docs/manuscript/`](docs/manuscript/) | Template-compatible manuscript source and rendered publication artifacts. |
| [`docs/documentation-index.md`](docs/documentation-index.md) | Flat index of every long-lived document. |
| [`docs/_generated/gate.md`](docs/_generated/gate.md) | Generated measured gate numbers (run `./run.sh bench`). |
| [`releases.json`](releases.json) | Hashed current and historical release manifest. |
| [`docs/`](docs/) | Source, export, migration, curation, release, and integration documentation. |
| [`Archived versions/`](Archived%20versions/README.md) | Immutable historical source evidence (indexed by the folder guide). |
| [`SUMO/`](SUMO/) | SUMO mapping-support material. |
| [`GNN/`](GNN/) | Generated GNN vocabulary bridge and its reviewed declared-label input. |
| [`TO-DO.md`](TO-DO.md) | Scoped review worklog (completed and deferred items). |
| [`CITATION.cff`](CITATION.cff) | Machine-readable citation metadata. |
| [`.aii/`](.aii/) | InstituteOS sidecar metadata and integration notes. |
| [`LICENSE`](LICENSE) | CC BY 4.0 license text. |

Repositories that consume the notation follow the [GNN downstream adoption
guide](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation/blob/main/docs/gnn/integration/downstream_adoption.md).

## CLI

Builds and ordinary structural checks use only Python 3.11+. The strict contract
gate additionally uses the pinned dependency in `requirements-ci.txt`.

[`run.sh`](run.sh) is the gate entry point; its arms are the exact commands the public
workflow runs, and [`docs/build-and-validation.md`](docs/build-and-validation.md)
documents them. From the repository root:

```bash
./run.sh             # no arm: the fast inner-loop selection
./run.sh deps        # one locked install
./run.sh all         # every arm the public workflow runs
```

The arms call the two CLIs directly:

```bash
python3 scripts/ontology.py build
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py schema-check
python3 scripts/ontology.py report
python3 scripts/ontology.py build --check
python3 scripts/ontology.py export-csv --check
python3 scripts/ontology.py site --check
python3 scripts/ontology.py gnn-terms --check
python3 scripts/ontology.py diff OLD_SOURCE.json NEW_SOURCE.json
python3 scripts/ontology.py audit-csv INPUT.csv
python3 scripts/manuscript.py generate
python3 scripts/manuscript.py validate --strict
python3 scripts/manuscript.py render --format all
python3 scripts/manuscript.py check
```

`build`, `export-csv`, `site`, and `gnn-terms` write deterministic artifacts
atomically. `validate` checks source integrity, generated freshness (including the
GNN vocabulary bridge), relation targets, release metadata, archive hashes, and
current-release counts. `validate --strict` also
validates the source, export, and release manifest against their published JSON
Schemas. `report` exposes quality gaps without presenting incomplete historical
metadata as complete. `audit-csv` reports duplicate labels, generated-ID collisions,
and malformed rows without producing a source document.

The manuscript pipeline derives all reported metrics, tables, figures, and provenance
from the canonical source and release manifest. It renders PDF, HTML, DOCX, and EPUB
outputs with Pandoc and records their hashes in
[`docs/manuscript/artifact-manifest.json`](docs/manuscript/artifact-manifest.json).

## Source model

Each term has an explicit stable opaque `id`, display label, aliases, publication status,
list, nullable tag, structured definitions/examples, preserved connection prose,
and relations. Existing free-text references were migrated only as `mentions`; no
stronger semantic relation is inferred automatically.

Initial migration IDs are derived from labels, but subsequent label changes retain
the curated ID and are reported by `diff`. The CSV remains available for spreadsheet workflows, but it is generated from the
structured source and must not be edited independently. See
[`docs/migration-v2.md`](docs/migration-v2.md) before consuming the new export.

## Curation and releases

Read [`docs/curation-workflow.md`](docs/curation-workflow.md), then run the strict
validator and review the generated report before changing release metadata. Historical
files are immutable and are checked by hash, not rewritten.

For citation, include the Zenodo DOI (concept DOI 10.5281/zenodo.7430332),
content release, source filename, and repository commit or tag.

## License

The repository and its content releases are licensed under the
[Creative Commons Attribution 4.0 International License](LICENSE) (CC BY 4.0).
