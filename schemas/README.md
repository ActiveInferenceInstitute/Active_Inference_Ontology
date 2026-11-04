# Published JSON Schemas

`schema-check` and the regression suite validate the live documents against
these three schemas. They are read by exact filename; the validator does not
enumerate the directory.

- `source-v2.json` — schema `active-inference-ontology/source/v2` for
  `ontology.source.json`: stable IDs, labels and aliases, status/list/tag,
  definitions, examples, provenance, and typed relations.
- `export-v2.json` — schema `active-inference-ontology/export/v2` for the
  generated `ontology.json`: release metadata, counts, tags, term records, and
  graph nodes and edges.
- `manifest-v2.json` — schema `active-inference-ontology/releases/v2` for
  `releases.json`: release ordering, artifact paths and kinds, dates, and
  SHA-256 hashes.

The contract validator is pinned to `jsonschema==4.26.0` in
[`../requirements-ci.txt`](../requirements-ci.txt). The data contracts are
documented in [`../docs/source-data-contract.md`](../docs/source-data-contract.md)
and [`../docs/json-export-contract.md`](../docs/json-export-contract.md).

Changing a schema is a paired change: update the validator and test
expectations in `scripts/ontology.py` and `tests/test_ontology.py`, regenerate
the affected artifacts, then run `python3 scripts/ontology.py validate --strict`
and `schema-check`.
