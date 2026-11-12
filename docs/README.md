# Active Inference Ontology Documentation

This documentation describes the v2 source contract, generated exports, release
integrity checks, curation process, historical archives, and integration surfaces.

| Document | Use it for |
| --- | --- |
| [Agent Guide](AGENTS.md) | Agent reading order, concept graph, and conventions for this directory. |
| [Source Data Contract](source-data-contract.md) | Structured source fields and validation policy. |
| [JSON Export Contract](json-export-contract.md) | Version 2 export and graph shape. |
| [Migration v2](migration-v2.md) | Breaking changes and consumer migration. |
| [Build and Validation](build-and-validation.md) | CLI commands and acceptance gates. |
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
| [Manuscript: Abstract](manuscript/00_abstract.md) | Abstract section of the generated manuscript. |
| [Manuscript: Introduction](manuscript/01_introduction.md) | Introduction section. |
| [Manuscript: Related Work](manuscript/02_related_work.md) | Related-work section. |
| [Manuscript: Methods](manuscript/03_methods.md) | Methods section. |
| [Manuscript: Results](manuscript/04_results.md) | Results section. |
| [Manuscript: Discussion](manuscript/05_discussion.md) | Discussion section. |
| [Manuscript: Conclusion](manuscript/06_conclusion.md) | Conclusion section. |
| [Manuscript: Reproducibility](manuscript/07_reproducibility.md) | Reproducibility section. |
| [Manuscript: References](manuscript/99_references.md) | References section. |
| [Manuscript Syntax](manuscript/SYNTAX.md) | Section, equation, figure, table, and citation conventions. |
| [Manuscript Preamble](manuscript/preamble.md) | Rendering preamble companion to `preamble.tex`. |

The canonical source is [`../ontology.source.json`](../ontology.source.json). The
CSV, JSON, and site are generated artifacts and are checked for freshness by
`python3 ../scripts/ontology.py validate --strict`; the same gate validates the
published source, export, and release-manifest schemas.

The publication manuscript is generated from the same source and manifest. Run
`python3 ../scripts/manuscript.py render --format all` to create PDF, HTML, DOCX,
and EPUB outputs, then run `python3 ../scripts/manuscript.py validate --strict`.
