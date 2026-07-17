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
