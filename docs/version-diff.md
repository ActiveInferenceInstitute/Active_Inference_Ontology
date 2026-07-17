# Version Diff

Compare two v2 structured sources by explicit stable ID:

```bash
python3 scripts/ontology.py diff OLD_SOURCE.json NEW_SOURCE.json
```

The JSON report identifies added IDs, removed IDs, label and case-only changes,
aliases, lists, tags, statuses, metadata, and relations in separate categories,
while retaining the aggregate changed-field list.
Malformed sources, duplicate identities, and invalid relation targets fail before a
diff is emitted. Case-only label changes are reported as renames and term changes.

Historical spreadsheet snapshots remain provenance material. They must first be
reviewed and deliberately imported into a v2 source before being compared.
