# Release Workflow

The content release remains v5 until domain curators approve new ontology content.
Schema and artifact changes are released through the versioned v2 contracts.

## Prepare and validate

1. Edit `ontology.source.json` using stable IDs and approved metadata.
2. Before generation, make `release.version`, `release.label`, and `release.date`
   agree in `ontology.toml`, the source, and the current `releases.json` entry.
3. In an already prepared environment, regenerate the complete release closure,
   then validate it:

```bash
python3 scripts/ontology.py build
python3 scripts/ontology.py export-csv
python3 scripts/ontology.py site
python3 scripts/ontology.py gnn-terms
python3 scripts/ontology.py sync-manifest
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py schema-check
```

4. Review the quality report and source diff:

```bash
python3 scripts/ontology.py report > /tmp/ontology-validation-report.json
python3 scripts/ontology.py diff OLD_SOURCE.json ontology.source.json > /tmp/ontology-release-diff.json
```

## Update release metadata

Update release metadata together before the generation sequence above.
`sync-manifest` verifies every archived artifact against its existing digest
and updates only current-release hashes and counts, including the published
source, export, and schemas. It never rebaselines altered archived evidence.
Historical files and their recorded hashes remain immutable; an approved new
content release needs its own release entry and archive folder.

## Final sign-off

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ontology.py build --check
python3 scripts/ontology.py export-csv --check
python3 scripts/ontology.py site --check
python3 scripts/ontology.py gnn-terms --check
python3 scripts/ontology.py validate --strict
```

Review the source, generated artifacts, manifest, archive additions, report, and
release diff before tagging the content release.
