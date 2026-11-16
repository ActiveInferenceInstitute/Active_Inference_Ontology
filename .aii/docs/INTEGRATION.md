# InstituteOS integration — Active_Inference_Ontology

## Identity

| Field | Value |
| --- | --- |
| Repository | `ActiveInferenceInstitute/Active_Inference_Ontology` |
| Affiliation | `institute` |
| Category | `ontology` |
| Status | `active` |
| Maturity | `released` |
| Steward | Active Inference Institute |
| Default branch | `main` |
| Current release | v5 |
| License | `CC-BY-4.0` |
| Citation | Active Inference Institute — Active Inference Ontology (concept DOI 10.5281/zenodo.7430332; v5 DOI 10.5281/zenodo.7972289). |

## Federation

| Setting | Value |
| --- | --- |
| Dashboard mode | `repos` |
| Analytics | `true` |
| Dashboard | `true` |
| Sync policy | `pull` |
| Registries | — |
| Tags | ontology, vocabulary, active-inference, free-energy-principle, controlled-vocabulary |

## Ecosystem relations

| Repository | Relation | Note |
| --- | --- | --- |
| `ActiveInferenceInstitute/ActiveInferenceJournal` | `referenced-by` | Journal materials cite Active Inference Ontology terms. |

## Key artifacts

| Path | Kind | Description |
| --- | --- | --- |
| `ontology.source.json` | `source` | Canonical structured ontology source. |
| `ontology.toml` | `doc` | Explicit source |
| `Ontology_v5_May_25_2023.csv` | `export` | Deterministic spreadsheet export of the structured source. |
| `ontology.json` | `export` | Version 2 machine-readable ontology export. |
| `schemas` | `doc` | Machine-readable source |
| `requirements-ci.txt` | `doc` | Pinned validation dependencies for strict CI checks. |
| `requirements-manuscript.txt` | `doc` | Pinned manuscript-generation dependencies. |
| `scripts/ontology.py` | `code` | Build |
| `scripts/manuscript.py` | `code` | Deterministic manuscript generation |
| `tests` | `code` | Ontology and manuscript regression test suite. |
| `site` | `export` | Dependency-free browsable ontology site. |
| `docs/manuscript` | `doc` | Template-compatible manuscript source |
| `docs/manuscript/artifact-manifest.json` | `dataset` | Hashed manuscript artifact manifest. |
| `releases.json` | `dataset` | Hashed release and archive manifest. |
| `SUMO` | `dataset` | Suggested Upper Merged Ontology mapping material. |
| `GNN` | `dataset` | Generated GNN vocabulary bridge and its reviewed declared-label input. |
| `LICENSE` | `doc` | CC-BY-4.0 license. |

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

## Validation

```bash
python -m aii_platform.aii_sidecar.validate <repo> --completeness
python -m aii_platform.aii_sidecar docs <repo> --overwrite
python -m aii_platform.aii_sidecar.run <repo> --list
```

The sidecar is valid when `validate` prints `OK` and reports no missing artifact,
manifest, link, or declared-doc path. Completeness is a curation target, not a
runtime requirement.

## Data boundary

This sidecar carries metadata only. It does not grant execution permission, does not
replace the repository's own documentation, and must not be used to move private
content into a public repository. Task execution is limited to trusted checkouts.
