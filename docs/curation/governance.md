# Curation Governance

## Roles

| Role | Responsibility |
| --- | --- |
| Proposer | Prepares a source change with motivation and evidence. |
| Curator | Checks identity, metadata, definitions, examples, and relations. |
| Domain reviewer | Checks technical meaning and relation semantics. |
| Release steward | Confirms tests, generated artifacts, hashes, archives, and sign-off. |

## Approval criteria

A change is ready to merge when:

- source schema validation passes;
- Core completeness requirements pass;
- relation targets and types are valid;
- generated JSON, CSV, and site are current;
- release manifest paths, counts, and hashes are current;
- the report and structured diff have been reviewed;
- domain claims have evidence when semantics change.

## Required checks

```bash
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py report > /tmp/ontology-validation-report.json
python3 -m unittest discover -s tests -v
```

Content releases additionally require a v2 source diff, archive review, manifest
update, and approval by the curator, domain reviewer, and release steward.
