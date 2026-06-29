# Version Diff

Use `scripts/diff_releases.py` to compare two ontology CSV snapshots by term
identity and content fields.

## Compare v4 to v5

```bash
python3 scripts/diff_releases.py \
  "Archived versions/v4 (12-12-2022 snapshot)/Ontology _ Definitions, Examples, Connections view.csv" \
  Ontology_v5_May_25_2023.csv
```

For machine-readable output:

```bash
python3 scripts/diff_releases.py \
  "Archived versions/v4 (12-12-2022 snapshot)/Ontology _ Definitions, Examples, Connections view.csv" \
  Ontology_v5_May_25_2023.csv \
  --json > /tmp/ontology-release-diff.json
```

## Report Fields

The report includes:

- old and new source paths;
- old and new term counts;
- added terms;
- removed terms;
- changed terms with the fields that changed;
- rename candidates based on similar removed and added term labels.

The script compares these fields:

- `List`
- `Tag`
- `Proposed Definition 1`
- `Proposed Definition 2`
- `Correct Examples`
- `Incorrect Examples`
- `Connections`

It ignores duplicate term labels after the first occurrence, matching the JSON
builder's term identity behavior.
