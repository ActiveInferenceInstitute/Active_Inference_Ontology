# Build and Validation

The toolchain is `scripts/ontology.py` and is configured by `ontology.toml`.
Build, export, and ordinary structural validation require Python 3.11+. The
strict contract gate uses the exact dependency pinned in `requirements-ci.txt`.

```bash
python3 -m pip install -r requirements-ci.txt
python3 scripts/ontology.py build
python3 scripts/ontology.py export-csv
python3 scripts/ontology.py site
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py schema-check
python3 scripts/ontology.py report
python3 scripts/ontology.py audit-csv INPUT.csv
python3 scripts/manuscript.py generate
python3 scripts/manuscript.py render --format all
python3 scripts/manuscript.py validate --strict
python3 scripts/manuscript.py check
```

## Validation coverage

Strict validation checks:

- source and export schema identifiers;
- source, export, and release-manifest JSON Schema validation;
- required release metadata and configured version;
- unique explicit IDs, labels, and aliases;
- allowed lists, tags, statuses, and relation types;
- required Core metadata;
- relation targets, duplicate relations, and self-relations;
- deterministic JSON, CSV, and site freshness;
- release paths, schema versions, counts, and SHA-256 hashes for current and archived artifacts.

The manifest validator also rejects duplicate release versions, non-numeric release
ordering, unsafe paths, duplicate artifacts, unknown artifact kinds, invalid dates,
and incomplete current-release metadata.

The quality report separately records historical missing tags, definitions, examples,
and connection text. Those values are visible data quality facts, not validation passes.

## Acceptance gates

```bash
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py schema-check
python3 scripts/ontology.py build --check
python3 scripts/ontology.py export-csv --check
python3 scripts/ontology.py site --check
python3 -m unittest discover -s tests -v
```

`build`, `export-csv`, and `site` write through temporary files followed by atomic
replacement. The `--check` forms are read-only and fail when a generated artifact is
missing or stale.

## Manuscript publication gate

The manuscript source under `docs/manuscript/` follows the template project conventions:
ordered sections, generated variables, labeled equations, a figure registry, a claim
ledger, and a validated bibliography. `scripts/manuscript.py` derives all reported
metrics from the ontology release, renders four formats with Pandoc and
`pandoc-crossref`, normalizes publication identifiers for reproducible bytes, and
records output hashes in `docs/manuscript/artifact-manifest.json`. Install
`requirements-manuscript.txt` plus Pandoc, `pandoc-crossref`, XeLaTeX, and qpdf for
the complete local rendering gate.
