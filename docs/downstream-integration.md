# Downstream Integration

Consumers should import the version 2 JSON export and verify its schema before use.

## JSON import

```python
import json
from pathlib import Path

data = json.loads(Path("ontology.json").read_text(encoding="utf-8"))
if data["schemaVersion"] != "2.0":
    raise ValueError("unsupported ontology export schema")

terms = {term["id"]: term for term in data["terms"]}
nodes = {node["id"] for node in data["graph"]["nodes"]}
if data["counts"]["terms"] != len(terms):
    raise ValueError("term count does not match terms")
if data["counts"]["terms"] != len(nodes):
    raise ValueError("node count does not match terms")
for edge in data["graph"]["edges"]:
    if edge["source"] not in nodes or edge["target"] not in nodes:
        raise ValueError("relation references a missing node")
```

## JavaScript import

```javascript
const data = await fetch("../ontology.json").then((response) => response.json());
if (data.schemaVersion !== "2.0") throw new Error("unsupported ontology export schema");

const nodes = new Set(data.graph.nodes.map((node) => node.id));
if (data.counts.terms !== data.terms.length) throw new Error("term count mismatch");
if (data.graph.edges.some((edge) => !nodes.has(edge.source) || !nodes.has(edge.target))) {
  throw new Error("relation endpoint mismatch");
}
```

Use `terms[].id` for joins, `terms[].term` for display, `aliases` for lookup, and
`terms[].status` for lifecycle filtering. Tags are nullable for historical material.
The `mentions` relation type records an exact textual reference and must not be
treated as a stronger semantic assertion.

The CSV is a generated spreadsheet export. Consumers needing stable machine imports
should use the JSON export and the schemas under `../schemas/`.

## GNN vocabulary bridge

[`GNN/act_inf_ontology_terms.json`](../GNN/act_inf_ontology_terms.json) is the generated
bridge to the GNN pipeline's `ActInfOntologyAnnotation` vocabulary (Step 10 ontology
processing). It is derived from the canonical source and export and is checked for
freshness by `validate`; it is an integration surface, not a release artifact, so it is
not listed in the release manifest.

| Field | Meaning |
| --- | --- |
| `release` | Content release metadata, copied from the source. |
| `source`, `export` | The source and export paths plus the SHA-256 digests the document was generated from. |
| `matchRule` | The deterministic rule used to resolve the declared GNN labels. |
| `terms` | Every canonical ontology label mapped to `id`, `status`, `tag`, and primary `description`. Join on `id`. |
| `declared` | The labels declared by GNN's bundled vocabulary (pinned in [`GNN/declared-labels.json`](../GNN/declared-labels.json)) with `status`, `match`, `id`, and `ontologyTerm`. |

Declared-label resolution status:

- `resolved` — exactly one ontology label (or alias) normalizes to the same key under
  the documented rule. The mapping target is the ontology stable `id`.
- `unresolved` — no counterpart exists in the current release. `id` stays `null`; the
  label requires ontology curation or a GNN-side migration and is never guessed.

### Freshness and pinning

```bash
python3 scripts/ontology.py gnn-terms
python3 scripts/ontology.py gnn-terms --check
```

A consumer pin is the ontology repository commit plus the SHA-256 of
`GNN/act_inf_ontology_terms.json`. The document records the source and export digests
it was generated from, so a consumer can verify the projection as well as the file.
GNN should pin both its copy of the bridge and the ontology revision and fail its own
freshness check when the ontology side has moved, mirroring the repository's
companion-pin freshness pattern.

This repository's conformance gate is the `gnn-conformance` job (display name
`gnn conformance (pinned)`), which runs `./run.sh gnn`. It installs the GNN revision
`8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1` (`v5.0.3`) recorded in
[`.github/gnn-pin.json`](../.github/gnn-pin.json) under schema `gnn-importer-pin/v1`,
then verifies the pinned parser's bundled vocabulary bytes and term set against
`GNN/declared-labels.json` and the generated bridge; [`../.github/GNN.md`](../.github/GNN.md)
records exactly what the job parses.

### Declared `obo:` values are not identifiers

The audited GNN vocabulary declares OBO-style `uri` values such as `obo:ACTO_000001`
and `obo:TEMP_000016`. No `ACTO` ontology exists in the OBO Foundry registry, the
Bioregistry, or OLS, and `http://purl.obolibrary.org/obo/ACTO_000001` does not resolve.
Those values are local placeholders recorded in
[`GNN/declared-labels.json`](../GNN/declared-labels.json) for audit only. This bridge
maps labels to stable `term-*` IDs and never adopts a declared placeholder as an
identifier.

