# JSON Export Contract

`ontology.json` uses schema `active-inference-ontology/export/v2` and is generated
from `ontology.source.json`.

## Top-level fields

| Field | Meaning |
| --- | --- |
| `schema` | Export schema identifier. |
| `schemaVersion` | `2.0`. |
| `release` | Content release metadata. |
| `source` | Source path, schema, and SHA-256 hash. |
| `counts` | Term, tag, and graph-edge counts. |
| `tags` | Sorted non-null tag values. |
| `terms` | Structured term records. |
| `graph` | Term nodes and typed relation edges. |

Counts are generated and must not be edited manually. The source and export schemas
are available in `../schemas/`, and the release manifest is validated by
`../schemas/manifest-v2.json`.

## Graph

Nodes contain `id`, `label`, nullable `tag`, and `status`. Edges contain `source`,
`target`, and one configured relation type. Every edge endpoint must correspond to
a node. `mentions` describes an exact canonical-label mention in preserved source
prose; it does not assert a domain-semantic relationship.

Consumers should join on `id`, display `term`, and treat additional fields as part
of the versioned v2 contract. See [`migration-v2.md`](migration-v2.md) for the
changes from the previous export.
