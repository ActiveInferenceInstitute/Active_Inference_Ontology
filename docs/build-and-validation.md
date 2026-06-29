# Build and Validation

The repository has one build script:

```bash
python3 scripts/build_json.py
```

It finds the newest `Ontology_v*.csv` file in the repository root and writes
`ontology.json`.

## Lint Mode

Use lint mode to validate the source CSV contract before generating:

```bash
python3 scripts/build_json.py --lint
python3 scripts/build_json.py --lint --strict
```

Lint checks:

- required headers;
- empty `Term` values;
- duplicate term labels after case-insensitive normalization;
- unexpected tag names.

`--strict` makes warnings fail as well as errors.

## Check Mode

Use check mode before committing ontology data changes:

```bash
python3 scripts/build_json.py --check
```

Expected clean output:

```text
ontology.json is up to date (<term-count> terms, <edge-count> edges).
```

If the file is stale, rebuild it:

```bash
python3 scripts/build_json.py
python3 scripts/build_json.py --check
```

## Report Mode

Use report mode for review artifacts and release checks:

```bash
python3 scripts/build_json.py --report > ontology-validation-report.json
```

The report includes lint results, counts, and rows whose `Connections` text did
not resolve to any known ontology term id.

## Build Inputs

The script reads only:

- the newest root-level `Ontology_v*.csv`

The script writes only:

- `ontology.json`

Historical files under `Archived versions/` and files under `SUMO/` are not
read by the builder.

## Validation Coverage

Current validation confirms that:

- a source CSV exists;
- required CSV headers are present;
- term labels are non-empty and unique after case-insensitive normalization;
- duplicate terms are collapsed case-insensitively;
- `ontology.json` matches the current builder output in `--check` mode;
- graph nodes and edges can be derived from the CSV.

Current validation does not yet confirm that:

- definitions are complete;
- examples and counter-examples follow a style guide;
- every connection mentions canonical term labels;
- graph edges use typed relationships;
- archived release metadata is complete.

Those gaps are captured in the root [`TODO.md`](../TODO.md).

## Recommended Pre-Commit Check

For documentation-only changes:

```bash
python3 scripts/build_json.py --lint --strict
python3 scripts/build_json.py --check
```

For source data changes:

```bash
python3 scripts/build_json.py --lint --strict
python3 scripts/build_json.py
python3 scripts/build_json.py --check
python3 scripts/build_json.py --report > /tmp/ontology-validation-report.json
```
