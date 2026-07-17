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
- **Citation:** [Zenodo concept DOI](https://zenodo.org/badge/latestdoi/343477486)

## Repository surfaces

| Path | Role |
| --- | --- |
| [`ontology.source.json`](ontology.source.json) | Canonical structured source with stable IDs, metadata, and relations. |
| [`ontology.json`](ontology.json) | Generated version 2 machine-readable export. |
| [`Ontology_v5_May_25_2023.csv`](Ontology_v5_May_25_2023.csv) | Generated spreadsheet export. |
| [`ontology.toml`](ontology.toml) | Explicit paths, release metadata, and validation policy. |
| [`scripts/ontology.py`](scripts/ontology.py) | Build, validation, reporting, diff, export, and site CLI. |
| [`scripts/manuscript.py`](scripts/manuscript.py) | Generate, validate, render, and hash the publication manuscript. |
| [`schemas/`](schemas/) | Machine-readable source, export, and release-manifest schemas. |
| [`site/index.html`](site/index.html) | Generated dependency-free browsing surface. |
| [`docs/manuscript/`](docs/manuscript/) | Template-compatible manuscript source and rendered publication artifacts. |
| [`releases.json`](releases.json) | Hashed current and historical release manifest. |
| [`docs/`](docs/) | Source, export, migration, curation, release, and integration documentation. |
| [`Archived versions/`](Archived%20versions/) | Immutable historical source evidence. |
| [`SUMO/`](SUMO/) | SUMO mapping-support material. |

## CLI

Builds and ordinary structural checks use only Python 3.11+. The strict contract
gate additionally uses the pinned dependency in `requirements-ci.txt`. Run from
the repository root:

```bash
python3 -m pip install -r requirements-ci.txt
python3 scripts/ontology.py build
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py schema-check
python3 scripts/ontology.py report
python3 scripts/ontology.py build --check
python3 scripts/ontology.py export-csv --check
python3 scripts/ontology.py site --check
python3 scripts/ontology.py diff OLD_SOURCE.json NEW_SOURCE.json
python3 scripts/ontology.py audit-csv INPUT.csv
python3 scripts/manuscript.py generate
python3 scripts/manuscript.py validate --strict
python3 scripts/manuscript.py render --format all
python3 scripts/manuscript.py check
```

`build`, `export-csv`, and `site` write deterministic artifacts atomically.
`validate` checks source integrity, generated freshness, relation targets, release
metadata, archive hashes, and current-release counts. `validate --strict` also
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

For citation, include the Zenodo DOI, content release, source filename, and repository
commit or tag.
