# Build and Validation

The toolchain is `scripts/ontology.py` and is configured by `ontology.toml`.
Build, export, and ordinary structural validation require Python 3.11+. The
strict contract gate uses the exact dependency pinned in `requirements-ci.txt`.

```bash
python3 -m pip install -r requirements-ci.txt
python3 scripts/ontology.py build
python3 scripts/ontology.py export-csv
python3 scripts/ontology.py site
python3 scripts/ontology.py gnn-terms
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
- deterministic JSON, CSV, site, and GNN vocabulary bridge freshness;
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
python3 scripts/ontology.py gnn-terms --check
python3 -m unittest discover -s tests -v
```

The separate `gnn conformance (pinned)` CI job installs the GNN revision in
[`.github/gnn-pin.json`](../.github/gnn-pin.json), verifies its vocabulary bytes
against `GNN/declared-labels.json`, and runs
`python3 scripts/validate_gnn_conformance.py` before the bridge freshness check.
That job is the parser-facing half of the vocabulary contract; it fails closed
when the pin, the parser, and the generated bridge disagree.

`build`, `export-csv`, `site`, and `gnn-terms` write through temporary files
followed by atomic replacement. The `--check` forms are read-only and fail when a
generated artifact is missing or stale.

## Manuscript publication gate

The manuscript source under `docs/manuscript/` follows the template project conventions:
ordered sections, generated variables, labeled equations, a figure registry, a claim
ledger, and a validated bibliography. `scripts/manuscript.py` derives all reported
metrics from the ontology release, renders four formats with Pandoc and
`pandoc-crossref`, normalizes publication identifiers for reproducible bytes, and
records output hashes in `docs/manuscript/artifact-manifest.json`. The manuscript
manifest validates its complete input/output closure, paths, hashes, byte counts,
derived counts, and figure-input digests. Install
`requirements-manuscript.txt` plus Pandoc, `pandoc-crossref`, XeLaTeX, and qpdf for
the complete local rendering gate.

### Figure byte checks and host portability

`generate --check` verifies figure **bytes** against the committed PNGs, and matplotlib
rasterization (font hinting and anti-aliasing) is host-dependent: regenerating the six
figures with the pinned toolchain (`matplotlib==3.10.3`) reproduces neither the committed
bytes on an off-CI host nor those on the CI runner. The committed PNGs stay the published
assets, and the byte comparison is scoped per host instead of being asserted globally.

- On a host whose rasterization differs, set `MANUSCRIPT_PORTABLE_CHECK=1`. Only the raw
  PNG byte comparison is skipped; the registry input digests, generated-variable
  freshness, and manifest hashes stay enforced. The committed figure assets keep a
  structural check in the regression suite (valid PNG, expected canvas size).
- In CI, the `manuscript` job regenerates the publication artifacts in its own toolchain
  (`generate`, then `manifest`) and then requires byte-identity for every artifact that is
  not rasterized: `git diff --exit-code -- docs/manuscript` excluding `output/figures/**`
  and the manifest that hashes those figures. Structure, references, the claim ledger, and
  all hashes are then validated against the freshly generated set.

See [`docs/manuscript/README.md`](manuscript/README.md).

## Private and manual checks

`.aii/` (the InstituteOS sidecar) is validated by the `aii_platform.aii_sidecar` validator,
which ships in a private kernel package and cannot be installed from public
infrastructure. It is therefore not part of the public workflow. Run it wherever that
environment and its credentials exist (maintainer host or a credentialed workflow):

```bash
python -m aii_platform.aii_sidecar.validate <repo>           # OK / problems
python -m aii_platform.aii_sidecar.validate <repo> --scan    # every sidecar under a tree
python -m aii_platform.aii_sidecar.run <repo> --list         # declared portable tasks
```

The public regression suite carries a dependency-free structural check of `.aii/` instead:
the schema marker, required sections, existing artifact and documentation paths, and
`owner/repo` relation targets.
