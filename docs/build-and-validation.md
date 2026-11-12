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

## Gate entry point and arms

[`../run.sh`](../run.sh) is the single gate entry point. Each arm runs the exact
command the public workflow runs, so `.github/workflows/ontology.yml` calls arms
instead of restating commands and there is no second copy to drift. With no arm
(`./run.sh`), it runs `fast` — the default is the cheap inner-loop selection, not the
full gate.

```bash
./run.sh deps         # one locked install (requirements-manuscript.txt includes -r requirements-ci.txt)
./run.sh lint         # ruff, policy in ruff.toml
./run.sh ontology     # validate --strict, schema-check, build/export-csv/site --check, report, diff
./run.sh fast         # regression subset without the publication layer (inner loop)
./run.sh full         # python -m unittest discover -s tests -v
./run.sh docs         # scripts/check_docs.py: relative links, anchors, index coverage, gate report freshness
./run.sh manuscript   # generate, manifest, byte-identity diff, validate --strict, check
./run.sh render       # render PDF/HTML/DOCX/EPUB (Pandoc, pandoc-crossref, XeLaTeX, qpdf)
./run.sh gnn          # pinned GNN parser conformance (installs the pin; needs network)
./run.sh bench        # measure every arm and regenerate docs/_generated/gate.md
./run.sh all          # every arm the public workflow runs
```

| Arm | Public job | Needs |
| --- | --- | --- |
| `deps` | `gate` | network on a cold environment |
| `lint`, `ontology`, `full`, `docs`, `manuscript` | `gate` | `requirements-manuscript.txt` |
| `gnn` | `gnn-conformance` | `requirements-gnn.txt` plus network for the pinned parser |
| `render` | manual | the full Pandoc/XeLaTeX/qpdf toolchain |
| `fast` | local inner loop | `requirements-ci.txt`, `PyYAML` |

Two selections are deliberate. `fast` runs `tests/test_ontology.py` and
`tests/test_sidecar.py`: the source, export, manifest, and sidecar contracts without
figure rasterization or rendering. `full` runs the whole suite, which the `full` arm is
the only definition of. The arms are individually runnable and composable
(`./run.sh lint docs`), so a focused change does not pay for unrelated arms.

Wall time per arm on this host is recorded in the generated
[`_generated/gate.md`](_generated/gate.md); regenerate it with `./run.sh bench` after
changing an arm. Prose does not carry gate timings.

Interpreter selection: `PYTHON=/path/to/python ./run.sh …` overrides; otherwise the
arm uses `.venv/bin/python` when present, then `python3` from `PATH`. A local `.venv`
is ignored by Git and excluded from the lexical-hygiene scan, so `./run.sh deps` inside
the checkout is safe.

### Dependency pins

- `requirements-ci.txt` — gate dependencies: the JSON Schema validator and `ruff`.
- `requirements-manuscript.txt` — publication layer; it includes `-r requirements-ci.txt`
  so the two files never pin the same package twice and one install satisfies the
  `gate` job.
- `requirements-gnn.txt` — parser-side dependency for the `gnn` arm only.

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

`./run.sh all` is the acceptance gate; the individual arms are listed above. It is the
same set the public workflow runs, so a green local run and a green workflow run mean the
same thing.

The separate `gnn conformance (pinned)` CI job runs `./run.sh gnn`. Its bootstrap
read extracts only the raw repository and revision from
[`.github/gnn-pin.json`](../.github/gnn-pin.json) to install the exact commit.
The installed `gnn.importers.read_pin` then owns pin normalization in
`scripts/validate_gnn_conformance.py`, which checks vocabulary bytes and labels
against `GNN/declared-labels.json` and the generated bridge. The arm tests the
bootstrap pair against `read_pin` and calls the canonical checker:

```bash
python -m gnn.importers check --repo . --require-pointer \
    --workflow .github/workflows/ontology.yml --job gnn-conformance
```

The shared reader owns pin normalization and pin/pointer/specification validation;
the member retains its vocabulary checks and `gnn-terms --check`. The adopted
release is `v5.1.0` at `75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf`, replacing
`v5.0.3` at `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`.
The pin, job key, and tested bootstrap exception are recorded in
[`.github/GNN.md`](../.github/GNN.md).

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
the complete local rendering gate (`./run.sh render`).

### Figure byte checks and host portability

`generate --check` verifies figure **bytes** against the committed PNGs, and matplotlib
rasterization (font hinting and anti-aliasing) is host-dependent: regenerating the six
figures with the pinned toolchain (`matplotlib==3.11.2`) reproduces neither the committed
bytes on every host nor those on the CI runner. The committed PNGs stay the published
assets, and the byte comparison is scoped per host instead of being asserted globally.

- On a host whose rasterization differs, set `MANUSCRIPT_PORTABLE_CHECK=1`
  (`MANUSCRIPT_PORTABLE_CHECK=1 ./run.sh full`). Only the raw PNG byte comparison is
  skipped; the registry input digests, generated-variable freshness, and manifest
  hashes stay enforced. The committed figure assets keep a structural check in the
  regression suite (valid PNG, expected canvas size).
- The `manuscript` arm regenerates the publication artifacts in the current toolchain
  (`generate`, then `manifest`) and then requires byte-identity for every artifact the
  generator owns that is not rasterized:
  `git diff --exit-code -- docs/manuscript/data/manuscript_variables.json
  docs/manuscript/output/manuscript docs/manuscript/output/figures/figure_registry.json`.
  Figure PNGs are excluded because their bytes are host-dependent, and
  `artifact-manifest.json` is excluded because it hashes those figures. Structure,
  references, the claim ledger, and all hashes are then validated against the freshly
  generated set. The arm writes figures in place, so `git diff
  docs/manuscript/output/figures` after a local run shows rasterized differences, not a
  failure; restore them with `git checkout -- docs/manuscript/output/figures` (and the
  manifest) when they are not part of the change.

See [`docs/manuscript/README.md`](manuscript/README.md).

## Documentation gate

`./run.sh docs` runs [`../scripts/check_docs.py`](../scripts/check_docs.py), which is the
repository's documentation check (there is no third-party documentation linter here). It
verifies three things:

- every relative link and image target in tracked Markdown resolves, with exact filename
  case, so a tree that passes on a case-insensitive host still passes on Linux CI;
- every in-repository fragment (`path#anchor`) matches a heading slug or an explicit
  `{#id}`/`<a id=…>` anchor in the target;
- [`documentation-index.md`](documentation-index.md) lists every long-lived document under
  `docs/` (the ordered manuscript section set is indexed by its own hub page).

`Archived versions/` is immutable historical evidence and is excluded: its links cannot be
repaired without rewriting the archive. The same arm also runs
`scripts/report_gate.py --check`, which fails when [`_generated/gate.md`](_generated/gate.md)
no longer matches the arm list or the measured test/document counts.

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
