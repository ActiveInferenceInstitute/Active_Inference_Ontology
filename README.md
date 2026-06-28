# Active Inference Ontology

A public, controlled vocabulary of Active Inference and Free Energy Principle
concepts — each term with a tag, definitions, examples, and the connections it
declares to other terms.

- **Live version:** <https://coda.io/@active-inference-institute/active-inference-ontology-website>
- **More information:** <https://www.activeinference.org/home>
- **Current release:** v5 (May 25, 2023) — work in progress.

[![DOI](https://zenodo.org/badge/343477486.svg)](https://zenodo.org/badge/latestdoi/343477486)

## Contents

| Path | What it is |
| --- | --- |
| [`Ontology_v5_May_25_2023.csv`](Ontology_v5_May_25_2023.csv) | Canonical source — one row per term. |
| [`ontology.json`](ontology.json) | Machine-readable export (generated from the CSV). |
| [`scripts/build_json.py`](scripts/build_json.py) | Regenerates `ontology.json` from the latest CSV. |
| [`Archived versions/`](Archived%20versions/) | Earlier ontology releases. |
| [`SUMO/`](SUMO/) | Suggested Upper Merged Ontology mapping material. |

## CSV columns

Each row in the source CSV has eight columns:

`List` · `Tag` · `Term` · `Proposed Definition 1` · `Proposed Definition 2` ·
`Correct Examples` · `Incorrect Examples` · `Connections`

`Tag` groups every term under one of eight areas: Action, Agents in the Niche,
Bayesian Statistics, Free Energy, Information, Markov Partitioning, Perception,
and Systems.

## Machine-readable JSON

`ontology.json` is a generated, dependency-free export for tools that should not
have to parse the multi-line quoted CSV. It contains:

- `terms[]` — one object per term (`id`, `term`, `tag`, both definitions,
  examples, counter-examples, connections).
- `graph` — a derived concept graph: `nodes` (one per term, typed by its tag)
  and `edges` (term-to-term references parsed from each term's `Connections`
  field, as `{source, target, relation}`).
- `termCount` / `tagCount` / `edgeCount` / `tags` summary fields.

The current export holds **429 terms** across **8 tags** with **238**
declared connections.

### Regenerate

```bash
python3 scripts/build_json.py          # rebuild ontology.json from the latest CSV
python3 scripts/build_json.py --check  # verify ontology.json is in sync (CI-friendly)
```

The script reads the newest `Ontology_v*.csv` in the repository root, so adding a
future `Ontology_v6_*.csv` and re-running keeps `ontology.json` current. Run
`--check` after editing the CSV to confirm the JSON was regenerated.

## Citing

Please cite via the Zenodo DOI above.
