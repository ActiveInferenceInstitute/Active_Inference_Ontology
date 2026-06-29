# Downstream Integration

Downstream tools should choose the source surface that matches their needs.

## Use the CSV When

- curating terms;
- reviewing definitions and examples;
- preserving spreadsheet-compatible workflows;
- comparing historical source releases.

The CSV is the source of truth, but consumers must handle quoted multi-line
fields and whitespace variation.

## Use `ontology.json` When

- building dashboards;
- indexing terms for search;
- loading the ontology into static websites;
- traversing derived term connections;
- avoiding CSV parsing in browser or lightweight environments.

The JSON export is generated and should not be edited directly.

## Use `graph` When

- visualizing concept neighborhoods;
- finding connected terms;
- building preliminary knowledge-graph views;
- checking whether `Connections` text resolves to canonical terms.

Current graph edges are untyped `connects` edges. Consumers that need stronger
semantics should layer their own interpretation or wait for a typed relation
contract.

## Integration Stability

Stable enough for consumers:

- `terms[].id`
- `terms[].term`
- `terms[].tag`
- `terms[].definition`
- `graph.nodes[].id`
- `graph.edges[].source`
- `graph.edges[].target`

Potentially changing:

- additional term metadata;
- explicit aliases;
- review status;
- typed relations;
- release manifests;
- archive exports.

## Suggested Consumer Checks

Consumers should fail fast when:

- `termCount` does not match `terms.length`;
- `graph.nodes.length` does not match `termCount`;
- an edge source or target id is absent from `graph.nodes`;
- the `source` field references an unexpected CSV file;
- required tags are missing.

These checks catch stale or partially generated ontology exports before they
reach user-facing interfaces.

## Minimal Python Consumer Check

```python
import json
from pathlib import Path

data = json.loads(Path("ontology.json").read_text(encoding="utf-8"))

terms = data["terms"]
nodes = {node["id"] for node in data["graph"]["nodes"]}
edges = data["graph"]["edges"]

assert data["termCount"] == len(terms)
assert len(nodes) == data["termCount"]

missing = [
    edge
    for edge in edges
    if edge["source"] not in nodes or edge["target"] not in nodes
]
if missing:
    raise ValueError(f"{len(missing)} graph edges reference missing nodes")
```

Use this kind of check at the boundary where a downstream application imports a
new ontology release.

## Minimal JavaScript Consumer Check

```javascript
import { readFile } from "node:fs/promises";

const data = JSON.parse(await readFile("ontology.json", "utf8"));

const terms = data.terms;
const nodes = new Set(data.graph.nodes.map((node) => node.id));
const missing = data.graph.edges.filter(
  (edge) => !nodes.has(edge.source) || !nodes.has(edge.target),
);

if (data.termCount !== terms.length) {
  throw new Error("termCount does not match terms.length");
}
if (nodes.size !== data.termCount) {
  throw new Error("graph node count does not match termCount");
}
if (missing.length > 0) {
  throw new Error(`${missing.length} graph edges reference missing nodes`);
}
```

Run this check in import scripts, build steps, or dashboard tests before using a
new ontology export in a user-facing surface.
