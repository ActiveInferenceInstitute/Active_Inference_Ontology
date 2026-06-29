# Curation Governance

This process defines how ontology changes move from proposal to release.

## Roles

| Role | Responsibility |
| --- | --- |
| Proposer | Opens or drafts the term change, including motivation and source context. |
| Curator | Checks term scope, definitions, examples, counter-examples, and connections. |
| Domain reviewer | Reviews technical correctness within Active Inference and Free Energy Principle usage. |
| Release steward | Confirms validation, archive, manifest, and release checklist completion. |

One person may hold more than one role for a small maintenance release, but the
domain reviewer should not be the only reviewer of a substantive new term.

## Change Classes

| Class | Examples | Review expectation |
| --- | --- | --- |
| Editorial | Typo fixes, formatting, whitespace cleanup. | Curator review. |
| Clarifying | Definition wording, example cleanup, connection spelling. | Curator plus domain reviewer when meaning changes. |
| Structural | New terms, renamed terms, retired terms, new tags, relation schema changes. | Curator, domain reviewer, and release steward. |
| Release | New root CSV, regenerated JSON, archive snapshot, release manifest update. | Release steward sign-off after validation. |

## Approval Criteria

A change is ready to merge when:

- the term identity and tag are intentional;
- definitions separate broad and narrow meanings when both are present;
- examples and counter-examples clarify use rather than repeating the definition;
- connection text uses canonical term labels where possible;
- lint, JSON freshness, validation report, and relevant release-diff checks pass;
- release metadata and archive notes are updated when release files change.

## Required Checks

```bash
python3 scripts/build_json.py --lint --strict
python3 scripts/build_json.py --check
python3 scripts/build_json.py --report > /tmp/ontology-validation-report.json
```

For release changes, also run:

```bash
python3 scripts/diff_releases.py OLD_RELEASE.csv NEW_RELEASE.csv --json > /tmp/ontology-release-diff.json
```

## Release Sign-Off Record

Each release should record:

- release version;
- source CSV filename;
- generated JSON counts;
- archive folder;
- release manifest entry;
- validation report path or summary;
- release-diff path or summary;
- approving curator;
- approving domain reviewer;
- release steward;
- date.
