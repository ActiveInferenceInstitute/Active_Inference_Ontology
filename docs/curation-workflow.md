# Curation Workflow

The structured source is the only editable ontology surface.

## Add or edit a term

1. Add or edit a record in `ontology.source.json`.
2. Assign a unique stable `id`; preserve it when changing a label.
3. Put alternate labels in `aliases` and choose an allowed `status`, `list`, and `tag`.
4. For Core terms, provide a tag, primary definition, and correct example.
5. Preserve free-text context in `connectionsText`.
6. Add only relations whose targets and types are explicit and reviewable.
7. Regenerate and validate:

```bash
python3 scripts/ontology.py build
python3 scripts/ontology.py export-csv
python3 scripts/ontology.py site
python3 scripts/ontology.py validate --strict
```

## Rename, retire, or merge

- Keep the existing `id` when a label changes.
- Add the former label to `aliases` when downstream lookup should continue to work.
- Use `deprecated`, `merged`, or `retired` status rather than deleting a published term.
- Record the replacement relationship explicitly when a merger has been reviewed.

## Review checklist

- Are IDs, labels, and aliases unique?
- Are required Core fields present?
- Do all relation targets exist and avoid self-relations?
- Is a relation type supported by explicit evidence?
- Does the quality report make remaining historical gaps visible?
- Do all generated artifacts and manifest hashes validate?
