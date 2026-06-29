# Active Inference Ontology Documentation

This folder documents the source data, generated export, archive material, and
operational workflows for the Active Inference Ontology repository.

## Documentation Map

| Document | Use it for |
| --- | --- |
| [Source Data Contract](source-data-contract.md) | CSV column meanings, row requirements, and term identity rules. |
| [JSON Export Contract](json-export-contract.md) | Shape of `ontology.json`, term records, graph nodes, and graph edges. |
| [Build and Validation](build-and-validation.md) | How to regenerate and check the machine-readable export. |
| [Curation Workflow](curation-workflow.md) | Review steps for adding, editing, or retiring ontology terms. |
| [Curation Governance](curation-governance.md) | Roles, approval criteria, and release sign-off expectations. |
| [Archive and Provenance](archive-and-provenance.md) | How historical releases are stored and how to preserve lineage. |
| [SUMO Integration](sumo-integration.md) | Scope and handling notes for the Sigma/SUMO mapping material. |
| [SUMO Mapping Contract](sumo-mapping-contract.md) | Durable mapping fields and review statuses for SUMO alignment. |
| [Downstream Integration](downstream-integration.md) | Guidance for tools consuming the CSV, JSON, and derived graph. |
| [Release Workflow](release-workflow.md) | Steps for publishing a new ontology CSV, JSON export, archive snapshot, and release manifest entry. |
| [Version Diff](version-diff.md) | How to compare ontology CSV snapshots across releases. |

## Repository Surfaces

| Path | Role |
| --- | --- |
| [`../Ontology_v5_May_25_2023.csv`](../Ontology_v5_May_25_2023.csv) | Canonical repository source for the current ontology release. |
| [`../ontology.json`](../ontology.json) | Generated JSON export for tools and dashboards. |
| [`../releases.json`](../releases.json) | Machine-readable release manifest for current and archived versions. |
| [`../scripts/build_json.py`](../scripts/build_json.py) | Regenerates and checks `ontology.json`. |
| [`../scripts/diff_releases.py`](../scripts/diff_releases.py) | Compares two ontology CSV releases. |
| [`../Archived versions/`](../Archived%20versions/) | Versioned historical snapshots retained for auditability. |
| [`../SUMO/`](../SUMO/) | Sigma/SUMO setup notes and mapping-support material. |
| [`../SUMO/mapping-template.csv`](../SUMO/mapping-template.csv) | CSV template for reviewed SUMO mappings. |
| [`../TODO.md`](../TODO.md) | Scoped backlog grouped into minor, medium, and major improvements. |

The CSV remains the source of truth. The JSON export is derived and should be
rebuilt with `python3 scripts/build_json.py` whenever the CSV changes.
