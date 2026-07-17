# Release Workflow

The content release remains v5 until domain curators approve new ontology content.
Schema and artifact changes are released through the versioned v2 contracts.

## Prepare and validate

1. Edit `ontology.source.json` using stable IDs and explicit metadata.
2. Run the strict source validator:

```bash
python3 -m pip install -r requirements-ci.txt
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py schema-check
```

3. Regenerate all checked-in artifacts:

```bash
python3 scripts/ontology.py build
python3 scripts/ontology.py export-csv
python3 scripts/ontology.py site
```

4. Review the quality report and source diff:

```bash
python3 scripts/ontology.py report > /tmp/ontology-validation-report.json
python3 scripts/ontology.py diff OLD_SOURCE.json ontology.source.json > /tmp/ontology-release-diff.json
```

## Update release metadata

Update `ontology.toml` when the content release changes. Then run:

```bash
python3 scripts/ontology.py sync-manifest
python3 scripts/ontology.py validate --strict
```

`sync-manifest` records SHA-256 hashes for every current and historical artifact,
including the published source, export, and manifest schemas. The manifest also
records schema identifiers and a validation summary for each release.
Do not edit historical files; add a new release entry and archive folder instead.

## Final sign-off

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ontology.py build --check
python3 scripts/ontology.py export-csv --check
python3 scripts/ontology.py site --check
python3 scripts/ontology.py validate --strict
```

Review the source, generated artifacts, manifest, archive additions, report, and
release diff before tagging the content release.
