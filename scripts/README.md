# Ontology and manuscript toolchain

Two Python entry points, both requiring Python 3.11 or newer. The CI workflow
[`.github/workflows/ontology.yml`](../.github/workflows/ontology.yml) runs their
acceptance commands.

## `ontology.py`

Configured by `ontology.toml` at the repository root. Subcommands:

- `build` / `build --check` — generate `ontology.json` from
  `ontology.source.json`; `--check` fails when the committed artifact is stale.
- `validate --strict` — source, export, and release-manifest contract checks,
  using `jsonschema==4.26.0` from `requirements-ci.txt`.
- `schema-check` — validate the live documents against `schemas/*.json`.
- `export-csv` / `export-csv --check` — refresh or verify
  `Ontology_v5_May_25_2023.csv`.
- `site` / `site --check` — build or verify the browsable `site/`.
- `gnn-terms` / `gnn-terms --check` — build or verify the GNN vocabulary bridge
  under `GNN/`.
- `report` — print the quality and validation report as JSON.
- `diff OLD NEW` — report release differences by stable ID.
- `audit-csv INPUT.csv` — audit an external spreadsheet export without importing
  it.

Writes are atomic (a temporary file followed by replacement); the `--check`
forms are read-only. See
[`../docs/build-and-validation.md`](../docs/build-and-validation.md) for the
full acceptance sequence.

## `manuscript.py`

Generates, validates, renders, and checks the manuscript under
`docs/manuscript`. Subcommands: `generate`, `manifest`,
`render --format`, `validate --strict`, and `check`. CI regenerates the
publication artifacts and then requires byte-identity for every
rasterizer-independent artifact.

The modules have no local test files; the regression suite lives in
[`../tests/`](../tests/).
