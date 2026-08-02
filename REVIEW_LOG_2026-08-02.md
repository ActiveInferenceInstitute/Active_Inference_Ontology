# Review Log — 2026-08-02 (docs-deep pass)

Fleet-parallel mega-deep documentation review of
`ActiveInferenceInstitute/Active_Inference_Ontology`. Scope: documentation
improvement, refactor, and hardening only — no ontology content changes.

## Phase 0 — Preflight

- `git fetch origin` + fast-forward pull onto `main` (default branch, verified
  via `git symbolic-ref --short refs/remotes/origin/HEAD`): **up to date**.
- Starting state: branch `main`, HEAD `47bcd6e`
  (`feat: complete deferred review items — portable manuscript tests,
  conservative-relation pin, curation proposal`); working tree clean.
- Inventory:
  - Root: `README.md`, `TO-DO.md` (scoped worklog), `LICENSE` (CC BY 4.0),
    `ontology.toml`, `ontology.source.json` / `ontology.json` /
    `Ontology_v5_May_25_2023.csv` / `releases.json`, `requirements-*.txt`,
    `schemas/` (3 JSON Schemas), `scripts/` (2 CLIs), `tests/` (2 suites),
    `site/index.html`, `Archived versions/` (v1–v4), `SUMO/`, `.aii/` sidecar,
    `.github/workflows/ontology.yml`.
  - Docs: `docs/README.md` index + 13 topic docs + `docs/manuscript/`
    (9 source sections, generated `output/`, config, bibliography, claim ledger,
    manifest); `.aii/README.md`, `.aii/AGENTS.md`, `.aii/docs/INTEGRATION.md`.
- Documentation volume: ~1,165 lines of Markdown across 46 `.md` files.

## Phase 1 — Mega-deep review: key findings

Severity counts: **Minor 4 · Medium 5 · Major 1** (the docs-surface completion
itself; no pre-existing major defect found).

- Minor — `docs/README.md` index omitted `future-curation-relations.md`.
- Minor — `.aii/README.md` task inventory listed 5 of 11 declared tasks.
- Minor — README citation pointed at the GitHub badge endpoint rather than a DOI.
- Minor — generated `output/manuscript/{99_references.md,combined.md}` carried a
  dead relative link to `references.bib` (inherited from the source section).
- Medium — missing root surfaces: `CONTRIBUTING.md`, `SECURITY.md`, `AGENTS.md`,
  `CITATION.cff`.
- Medium — `docs/manuscript/README.md` had no back-link to the docs index or the
  build-and-validation gate.
- Reviewed and found accurate (no change): all CLI commands in README/docs match
  the argparse parsers; counts (429 terms / 238 relations / 8 tags / Core 64 /
  Entailed 73 / Supplement 292) match the live report, variables, and manifest;
  the SUMO mapping template header matches `docs/sumo-mapping-contract.md`;
  `config.yaml.example` is in sync with `config.yaml` (modulo the deliberate
  date placeholder); archived-version READMEs match their folders.
- False positive (no action): an apparent duplicate `jsonschema==4.24.0` pin was
  an artifact of concatenating the two `requirements-*.txt` files in one shell
  command; each file is intentionally self-contained.

## Phase 3 — Verification runs (real results, Python 3.14 venv in /tmp)

- `ontology.py validate --strict` → **passed: 429 terms, 238 relations, 8 tags**.
- `ontology.py schema-check`, `build --check`, `export-csv --check`,
  `site --check`, `report` → **passed**.
- `manuscript.py validate --strict` and `check` (with `MANUSCRIPT_PORTABLE_CHECK=1`,
  the documented off-CI contract) → **passed: 9 sections, 6 figures, 4 rendered
  formats**. Without the flag, the figure-byte check correctly reports the
  documented environmental staleness (host rasterization ≠ CI canonical).
- `unittest discover -s tests` → **35 tests, OK (0 failures, 0 skipped)**.
- `ruff check scripts tests` → **All checks passed**; mypy: only the known
  third-party type-metadata notes (`matplotlib`, `yaml`, `jsonschema`); no new
  source errors. `ruff format` was not applied repo-wide (pre-existing
  deviations outside the touched lines; would be churn).
- Heavy rendering (Pandoc / XeLaTeX / qpdf) was **not** run; committed rendered
  artifacts are verified via the manuscript manifest, which validates hashes,
  byte counts, and closure for all four formats.

## Phase 4 — Implementation summary (commits on `main`)

| Commit | Content |
| --- | --- |
| `9e38592` | `docs: re-root bibliography link in generated manuscript sections` |
| `f77a26b` | `docs: complete the repository documentation surface` (README, docs index, manuscript README, sidecar README) |
| `0579c73` | `docs: add contributor, security, agent, and citation surfaces` (CONTRIBUTING, SECURITY, AGENTS, CITATION.cff) |
| (latest) | `docs: record 2026-08-02 docs-deep review pass` (TO-DO.md worklog; this log) |

Files changed (this pass): `scripts/manuscript.py`,
`docs/manuscript/output/manuscript/{99_references.md,combined.md}`,
`docs/manuscript/artifact-manifest.json`, `README.md`, `docs/README.md`,
`docs/manuscript/README.md`, `.aii/README.md`, and new `CONTRIBUTING.md`,
`SECURITY.md`, `AGENTS.md`, `CITATION.cff`, `TO-DO.md` (updated),
`REVIEW_LOG_2026-08-02.md`.

Post-push state: `git status` clean; `main` up to date with `origin/main`.
