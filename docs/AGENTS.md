# Agent guide — docs/ (Active Inference Ontology)

## Overview

This directory holds the repository's documentation hub: the v2 source contract,
generated-export contract, curation workflow and governance, release and archive
provenance, SUMO integration scope, downstream integration, and the
template-compatible publication manuscript. It is indexed by
[`README.md`](README.md) and surfaces in the root [`README.md`](../README.md)
and [`AGENTS.md`](../AGENTS.md).

## Reading order (cold start)

1. [`../AGENTS.md`](../AGENTS.md) — what this repo is, ground truth, commands.
2. [`README.md`](README.md) — the documentation index (one row per topic).
3. [`../ontology.source.json`](../ontology.source.json) is the only editable
   ontology surface. `ontology.json`, the CSV, `site/index.html`, and
   `releases.json` are generated — never edit them by hand.
4. Task-specific: curation → [`curation-workflow.md`](curation-workflow.md) +
   [`curation-governance.md`](curation-governance.md); releases →
   [`release-workflow.md`](release-workflow.md); consumers →
   [`downstream-integration.md`](downstream-integration.md); manuscript →
   [`manuscript/README.md`](manuscript/README.md).

## Concept graph (how the abstraction tower links)

- **Source → exports:** [`source-data-contract.md`](source-data-contract.md)
  defines the structured source fields; [`json-export-contract.md`](json-export-contract.md)
  defines the export graph shape consumers see; [`migration-v2.md`](migration-v2.md)
  maps breaking changes for existing consumers.
- **Editing → release:** [`curation-workflow.md`](curation-workflow.md) is the
  per-term editing procedure; [`curation-governance.md`](curation-governance.md)
  defines review roles and sign-off; [`release-workflow.md`](release-workflow.md)
  publishes a content release; [`version-diff.md`](version-diff.md) compares
  releases by stable ID.
- **Integrity:** [`build-and-validation.md`](build-and-validation.md) lists every
  CLI command and gate; [`archive-and-provenance.md`](archive-and-provenance.md)
  covers the immutable historical evidence and its hashes.
- **Supporting mappings:** [`sumo-integration.md`](sumo-integration.md) and
  [`sumo-mapping-contract.md`](sumo-mapping-contract.md) scope the SUMO support;
  [`downstream-integration.md`](downstream-integration.md) shows how to import
  JSON, CSV, and schemas.
- **Open frontier:** [`future-curation-relations.md`](future-curation-relations.md)
  records the not-yet-implemented typed-relations proposal — treat it as design,
  not current behavior.

## Conventions

- Every doc here is public-safe prose; no local paths or personal tooling.
- Cross-references use relative paths with descriptive link text.
- Claims about counts, edges, tags, or hashes must be verified via the CLI
  (`python3 ../scripts/ontology.py report` / `validate --strict`), never copied
  from prose.
