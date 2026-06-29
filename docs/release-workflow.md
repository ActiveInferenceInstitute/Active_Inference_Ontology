# Release Workflow

Use this workflow when publishing a new ontology source snapshot.

## 1. Prepare the Source

1. Add the new root-level CSV using the naming pattern
   `Ontology_v<version>_<date-or-label>.csv`.
2. Keep the previous release files in place.
3. Update rows with canonical term names in `Connections` where possible.
4. Run lint before generating:

```bash
python3 scripts/build_json.py --lint --strict
```

## 2. Rebuild the Export

```bash
python3 scripts/build_json.py
python3 scripts/build_json.py --check
```

The script reads the newest `Ontology_v*.csv`, so confirm the intended file is
selected in the `source` field of `ontology.json`.

## 3. Review the Validation Report

```bash
python3 scripts/build_json.py --report > ontology-validation-report.json
```

Review:

- CSV lint errors and warnings;
- term, tag, and edge counts;
- connection rows that did not resolve to ontology term ids;
- suggested canonical-term matches for unresolved connection text.

The validation report is a review artifact. It does not need to be committed
unless a release process explicitly chooses to retain it.

## 4. Update Release Metadata

Update `releases.json` with:

- version;
- label;
- date when known;
- status;
- source files;
- generated files;
- counts for the current release;
- notes about source provenance and known limitations.

## 5. Compare Release Changes

Run a release diff against the prior CSV snapshot:

```bash
python3 scripts/diff_releases.py OLD_RELEASE.csv NEW_RELEASE.csv
python3 scripts/diff_releases.py OLD_RELEASE.csv NEW_RELEASE.csv --json > /tmp/ontology-release-diff.json
```

Review added, removed, changed, and likely renamed terms before publishing.

## 6. Archive the Prior Snapshot

Create a folder under `Archived versions/` using this pattern:

```text
Archived versions/v<version> (YYYY-MM-DD snapshot)/
```

Add a `README.md` in the archive folder that records source date, source files,
and notable differences from the prior version.

## 7. Final Checks

Run:

```bash
python3 scripts/build_json.py --lint --strict
python3 scripts/build_json.py --check
python3 scripts/build_json.py --report > /tmp/ontology-validation-report.json
python3 scripts/diff_releases.py OLD_RELEASE.csv NEW_RELEASE.csv --json > /tmp/ontology-release-diff.json
```

Then review diffs for:

- root CSV changes;
- regenerated `ontology.json`;
- `releases.json`;
- archive folder additions;
- documentation changes.
