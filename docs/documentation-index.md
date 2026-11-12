# Documentation index

Flat index of the repository's long-lived documents. [`README.md`](README.md) is the
hub (one row per question); this page is the complete list, and the `docs` gate arm
(`./run.sh docs` → [`../scripts/check_docs.py`](../scripts/check_docs.py)) fails when a
document under `docs/` is missing here or when any relative link or anchor does not
resolve.

## Repository surfaces

- [`README.md`](README.md) — documentation hub: one row per question.
- [`documentation-index.md`](documentation-index.md) — this flat index.
- [`../README.md`](../README.md) — what the repository is, surfaces table, CLI.
- [`../AGENTS.md`](../AGENTS.md) — orientation for AI agents and automation.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — editable surfaces, curation rules, gate arms.
- [`../TO-DO.md`](../TO-DO.md) — scoped worklog of completed and deferred review items.
- [`../SECURITY.md`](../SECURITY.md) — security scope and reporting path.
- [`../.aii/README.md`](../.aii/README.md) — InstituteOS sidecar metadata and task map.
- [`../.github/GNN.md`](../.github/GNN.md) — the GNN conformance job, its pin, and what it parses.
- [`../run.sh`](../run.sh) — the gate entry point (arms documented in [`build-and-validation.md`](build-and-validation.md)).
- [`../LICENSE`](../LICENSE) — CC BY 4.0.
- [`../CITATION.cff`](../CITATION.cff) — machine-readable citation metadata.

## Contracts and data model

- [`source-data-contract.md`](source-data-contract.md) — structured source fields and validation policy.
- [`json-export-contract.md`](json-export-contract.md) — version 2 export and graph shape.
- [`migration-v2.md`](migration-v2.md) — breaking changes and consumer migration.
- [`version-diff.md`](version-diff.md) — comparing structured source releases by stable ID.

## Gates, releases, and provenance

- [`build-and-validation.md`](build-and-validation.md) — CLI, gate arms, artifact checks, manuscript gate, private checks.
- [`release-workflow.md`](release-workflow.md) — publishing a content release.
- [`archive-and-provenance.md`](archive-and-provenance.md) — immutable historical material and hashes.
- [`_generated/gate.md`](_generated/gate.md) — generated: measured arm wall time, test and term counts.

## Curation

- [`curation-workflow.md`](curation-workflow.md) — editing source terms and relations.
- [`curation-governance.md`](curation-governance.md) — review roles and release sign-off.
- [`future-curation-relations.md`](future-curation-relations.md) — typed-relation and alias-aware mention proposal (not implemented).

## Integration

- [`downstream-integration.md`](downstream-integration.md) — importing JSON, CSV, and schemas, and the GNN vocabulary bridge contract.
- [`sumo-integration.md`](sumo-integration.md) — SUMO support scope.
- [`sumo-mapping-contract.md`](sumo-mapping-contract.md) — mapping fields and review states.

## Publication

- [`manuscript/README.md`](manuscript/README.md) — manuscript source, generation, rendering, and integrity checks (entry point for the ordered section set below `manuscript/`).

## Agent and generated documentation

- [`AGENTS.md`](AGENTS.md) — reading order, concept graph, and conventions for this directory.
- [`_generated/README.md`](_generated/README.md) — folder policy for generated documents.
