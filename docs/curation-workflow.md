# Curation Workflow

This workflow keeps ontology edits reviewable while preserving the generated
JSON contract.

## Add a Term

1. Add a new row to the latest root-level `Ontology_v*.csv`.
2. Choose an existing `Tag` unless a new conceptual area is intentional.
3. Write at least one definition and one correct example.
4. Add counter-examples when the term is commonly confused with neighboring
   concepts.
5. Use canonical term names in `Connections` so graph edges are generated.
6. Rebuild and check the JSON export:

```bash
python3 scripts/build_json.py
python3 scripts/build_json.py --check
```

## Edit a Term

1. Prefer improving definitions, examples, and connections without changing the
   `Term` label.
2. If the term label must change, note that its generated `id` will change.
3. Update connection text in other rows if the renamed term is referenced there.
4. Rebuild `ontology.json`.

## Retire or Replace a Term

The current CSV contract has no explicit status column. Until that exists:

- avoid deleting terms that downstream tools may consume;
- use the definition or examples to clarify deprecated usage only when needed;
- record planned status-field work in `TODO.md`;
- preserve removed historical content through a versioned archived release.

## Review Checklist

- Does the term belong to one of the eight current tags?
- Are broad and narrow meanings separated when both are present?
- Are examples domain-specific rather than generic dictionary examples?
- Do counter-examples explain common misuse?
- Are connection mentions spelled as canonical ontology terms?
- Does `python3 scripts/build_json.py --check` pass after regeneration?

## Release Handoff

Before publishing a new release, capture:

- source CSV filename;
- generated `ontology.json` counts;
- summary of added, changed, and removed terms;
- known limitations in relation extraction or curation coverage;
- archive snapshot location.
