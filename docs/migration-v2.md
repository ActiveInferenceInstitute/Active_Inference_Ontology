# Migration to Export Schema v2

The v2 export is intentionally versioned and is not wire-compatible with the
previous generated JSON.

## Changes

- `schema` is now `active-inference-ontology/export/v2` and `schemaVersion` is `2.0`.
- Counts are grouped under `counts.terms`, `counts.tags`, and `counts.edges`.
- Term identity is explicit and stable in `terms[].id`.
- `definition` and `definition2` are now `definitions.primary` and
  `definitions.secondary`.
- `examples` and `counterExamples` are grouped under `examples.correct` and
  `examples.incorrect`.
- `tag` may be `null` for historical untagged material.
- `status`, `aliases`, `connectionsText`, and explicit `relations` are present.
- Graph nodes no longer use the ambiguous `Other` type; they expose nullable `tag`.
- Graph edges carry the relation type from the source relation record.

Initial migration IDs are derived from normalized labels. After curation, IDs are
stable opaque identities: a display-label rename does not change the ID. The diff
command reports additions, removals, label and case-only renames, alias/list/tag/status
changes, metadata changes, and relation changes.

## Consumer migration

1. Require `schemaVersion == "2.0"`.
2. Replace top-level `termCount`, `tagCount`, and `edgeCount` reads with `counts.*`.
3. Read definitions and examples from their nested objects.
4. Use explicit IDs for joins and retain aliases for display/search lookup.
5. Treat `mentions` as textual evidence, not as a semantic relation.
6. Handle nullable tags and statuses explicitly.

The source and export contracts are machine-readable under `schemas/`.

For historical CSV diagnostics without writing a source document, run:

```bash
python3 scripts/ontology.py audit-csv INPUT.csv
```
