# Discussion {#sec:discussion}

The release makes a useful boundary visible: the ontology is a curated vocabulary artifact with executable integrity guarantees, not a claim that every term or relation has been formally resolved. Stable identifiers and explicit statuses support longitudinal curation. Structured definitions and examples permit downstream applications to distinguish missing data from intentionally nullable fields. Raw connection prose remains available alongside the typed graph, which lets reviewers inspect how each migrated edge was produced.

The strict pipeline also changes what “reproducible” means for a vocabulary. A reader can reproduce the JSON, CSV, site, figures, tables, and manuscript from the source and pinned configuration. Hashes identify the exact inputs and outputs. The result is stronger than a static download, but it remains bounded by the source content and by the predicates implemented in the validators. Schema validity does not establish conceptual truth, and a passed freshness check does not certify semantic adequacy.

## Limitations

The primary limitation is temporal: the current content is a May 2023 snapshot. The repository records historical v1–v4 material but does not reinterpret those archives under the v2 source schema. The current release has {{MISSING_TAG}} terms without tags, {{MISSING_PRIMARY_DEFINITION}} without primary definitions, {{MISSING_CORRECT_EXAMPLE}} without correct examples, {{MISSING_INCORRECT_EXAMPLE}} without incorrect examples, and {{MISSING_CONNECTIONS}} without connection text. These are measured source properties, not silently repaired values.

The second limitation is semantic. The migration creates only `mentions` relations from textual references. It does not infer `broader`, `narrower`, `causes`, `part_of`, `inverse`, `prerequisite`, `contrasts`, or `related` edges. Future curation can add those relations with explicit review, provenance, and regression tests.

The third limitation is representational. The source schema is intentionally compact and does not yet provide multilingual labels, formal axioms, external concept identifiers, or a complete SKOS/OWL serialization. Those are extension points rather than hidden assumptions. The current design favors transparent preservation and deterministic publication while the conceptual model matures.
