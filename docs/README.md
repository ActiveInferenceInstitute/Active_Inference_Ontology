# Active Inference Ontology Documentation

This documentation describes the v2 source contract, generated exports, release
integrity checks, curation process, historical archives, and integration surfaces.

| Document | Use it for |
| --- | --- |
| [Documentation Index](documentation-index.md) | Flat index of every long-lived document in the repository. |
| [Agent Guide](AGENTS.md) | Agent reading order, concept graph, and conventions for this directory. |
| [Source Data Contract](source-data-contract.md) | Structured source fields and validation policy. |
| [JSON Export Contract](json-export-contract.md) | Version 2 export and graph shape. |
| [Migration v2](migration-v2.md) | Breaking changes and consumer migration. |
| [Build and Validation](build-and-validation.md) | CLI, gate arms (`./run.sh`), acceptance gates, and private checks. |
| [Measured Gate Numbers](_generated/gate.md) | Generated: arm wall time, regression-test and source-term counts. |
| [Curation Workflow](curation-workflow.md) | Editing source terms and relations. |
| [Curation Governance](curation-governance.md) | Review roles and release sign-off. |
| [Future Curation](future-curation-relations.md) | Proposal for typed relations and alias-aware mention extraction (not implemented). |
| [Archive and Provenance](archive-and-provenance.md) | Immutable historical material and hashes. |
| [SUMO Integration](sumo-integration.md) | SUMO support scope. |
| [SUMO Mapping Contract](sumo-mapping-contract.md) | Mapping fields and review states. |
| [Downstream Integration](downstream-integration.md) | Importing JSON, CSV, and schemas, and the GNN vocabulary bridge contract. |
| [Release Workflow](release-workflow.md) | Publishing a content release. |
| [Version Diff](version-diff.md) | Comparing structured source releases by stable ID. |
| [Manuscript](manuscript/README.md) | Template-compatible manuscript source, generation, rendering, and integrity checks. |

The canonical source is [`../ontology.source.json`](../ontology.source.json). The
CSV, JSON, and site are generated artifacts and are checked for freshness by the
`ontology` gate arm (`./run.sh ontology`); the same arm validates the published
source, export, and release-manifest schemas.

The publication manuscript is generated from the same source and manifest. The
`manuscript` gate arm (`./run.sh manuscript`) regenerates the resolved sections and
checks them against the committed bytes; the `render` arm
(`./run.sh render`) produces PDF, HTML, DOCX, and EPUB outputs and requires Pandoc,
`pandoc-crossref`, XeLaTeX, and qpdf.
