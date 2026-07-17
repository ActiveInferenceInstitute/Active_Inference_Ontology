# Introduction {#sec:introduction}

Active inference is used across neuroscience, cognitive science, biology, and theoretical approaches to adaptive agency. Its vocabulary spans mathematical constructs, modeling practices, empirical descriptors, and explanatory terms. A shared ontology can make those terms discoverable and comparable, but only if its records preserve provenance and distinguish documented content from later interpretation. The present repository provides such an artifact for the Active Inference Institute community.

The central contribution is a release process rather than a claim that the vocabulary is complete or universally settled. The current content is the May 25, 2023 release, represented without unsourced semantic rewriting. Its spreadsheet lineage is retained, while a structured source document becomes the sole editable model. Each term has a stable opaque identifier, a display label, aliases, curation status, list membership, optional tag, structured definitions and examples, raw connection prose, and explicit relation records. This separation is aligned with ontology-engineering practice: identifiers provide continuity while labels and descriptions remain revisable [@gruber1993; @studer1998].

The publication artifact addresses three practical questions. First, how can a historical terms list become a machine-readable graph without silently strengthening its semantics? Second, how can generated JSON, CSV, site, manuscript, and archive metadata be checked as one release? Third, how can a reader reproduce the reported counts and inspect the source evidence? The answers are formalized in [@sec:methods] and evaluated in [@sec:results].

The pipeline reports the current release as 429 terms, 238 explicit relations, and 8 populated tags. These counts describe the release artifact, not a measurement of the scientific validity or conceptual sufficiency of active inference. The distinction matters because ontology quality includes scope, coverage, consistency, and fitness for use, while automated validation can only establish the properties expressed by its contract.

The manuscript makes four contributions:

1. an explicit source model with stable term identity and typed graph edges;
2. deterministic export, site, manuscript, and release-manifest generation;
3. fail-closed structural, schema, freshness, and integrity validation; and
4. a transparent account of coverage, gaps, historical provenance, and future curation boundaries.
