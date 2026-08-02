# Contributing to the Active Inference Ontology

Thank you for contributing. The repository publishes a controlled vocabulary of
Active Inference and Free Energy Principle concepts as a reproducible data and
software artifact (see [`README.md`](README.md)).

## Where to start

- Read [`README.md`](README.md) for the repository surfaces and the CLI.
- Browse the [documentation index](docs/README.md); it maps every document to
  the question it answers.
- For curation topics, read [`docs/curation-workflow.md`](docs/curation-workflow.md)
  and [`docs/curation-governance.md`](docs/curation-governance.md) first.

## What is editable

- `ontology.source.json` is the only editable ontology surface. It is the
  canonical source for every generated artifact.
- `ontology.toml` configures paths, release metadata, and validation policy.
- Markdown under `docs/` (including `docs/manuscript/`) is hand-edited prose.
- Scripts under `scripts/` and tests under `tests/` are regular Python code.

Generated artifacts — `ontology.json`, `Ontology_v5_May_25_2023.csv`,
`site/index.html`, `releases.json` (after `sync-manifest`), and everything
under `docs/manuscript/output/` — are written by the pipeline. Do not edit
them by hand; regenerate them with the commands below.

## Making a change

1. Open an issue for semantic or curation changes so the review roles in
   [`docs/curation-governance.md`](docs/curation-governance.md) can weigh in
   before a proposal becomes a diff.
2. Edit the source or docs directly for mechanical fixes (typos, broken
   links, stale prose, small refactors).
3. Run the acceptance gates below.
4. Open a pull request against `main` and summarize what changed and why.

## Curation rules

- Assign every term a stable opaque `id` (`term-...`) and preserve it when a
  label changes; put the former label in `aliases` for discovery.
- Only exact, word-boundary occurrences of canonical labels become `mentions`
  relations. Do not hand-add `mentions`; stronger relation types require
  explicit curator review and provenance.
- Retire terms with `deprecated`, `merged`, or `retired` status rather than
  deleting published records.
- Historical files under `Archived versions/` are immutable source evidence;
  never rewrite them. Add a new snapshot folder for new releases.

## Code and manuscript rules

- `scripts/ontology.py` and `scripts/manuscript.py` are Python 3.11+ with no
  runtime dependency beyond the pinned `requirements-ci.txt` and
  `requirements-manuscript.txt` files. Keep it that way.
- Follow the repository's style (ruff-compatible); keep changes focused.
- The manuscript is generated from the ontology source and manifest. See
  [`docs/manuscript/README.md`](docs/manuscript/README.md) and
  [`docs/manuscript/SYNTAX.md`](docs/manuscript/SYNTAX.md) before touching
  manuscript sections. Never edit `docs/manuscript/output/` by hand.
- The repository intentionally has no root `TODO.md` (a regression test
  enforces this). Track scoped, deferred work in the hyphenated
  `TO-DO.md` worklog instead.

## Acceptance gates

Run from the repository root with the pinned dependencies installed:

```bash
python3 -m pip install -r requirements-ci.txt -r requirements-manuscript.txt
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py schema-check
python3 scripts/ontology.py build --check
python3 scripts/ontology.py export-csv --check
python3 scripts/ontology.py site --check
python3 -m unittest discover -s tests -v
MANUSCRIPT_PORTABLE_CHECK=1 python3 scripts/manuscript.py validate --strict
MANUSCRIPT_PORTABLE_CHECK=1 python3 scripts/manuscript.py check
```

`MANUSCRIPT_PORTABLE_CHECK=1` skips only the raw figure-byte comparison on
hosts whose matplotlib rasterization differs from the CI toolchain; all other
integrity checks stay enforced (see
[`docs/build-and-validation.md`](docs/build-and-validation.md)). CI runs the
same gates on every push, with the manuscript figures checked byte-exactly.

## Release changes

Content releases and release metadata require the full release process in
[`docs/release-workflow.md`](docs/release-workflow.md): update
`ontology.toml`, regenerate artifacts, run `sync-manifest`, review the report
and diff, and confirm the archive and manifest state.

## License and attribution

The repository is licensed under CC BY 4.0 (see [`LICENSE`](LICENSE)). For
citation, use the Zenodo DOI in [`CITATION.cff`](CITATION.cff) together with
the content release, source filename, and repository commit or tag.
