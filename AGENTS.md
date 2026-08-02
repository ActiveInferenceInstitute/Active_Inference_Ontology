# Agent guide — Active Inference Ontology

Orientation for AI agents and automation working in this repository.

## Ground truth

- `ontology.source.json` (schema `active-inference-ontology/source/v2`) is the
  only editable ontology surface; `ontology.toml` configures paths, release
  metadata, and validation policy.
- `ontology.json`, `Ontology_v5_May_25_2023.csv`, `site/index.html`,
  `releases.json`, and everything under `docs/manuscript/output/` are
  generated. Regenerate them with the CLI; never edit them by hand.
- `Archived versions/` is immutable historical evidence — never rewrite it.
- Every claim about counts, edges, tags, or hashes should be verified by
  running the CLI (or reading the manifest), not copied from prose.

## Reading order

1. `README.md` — surfaces, CLI, source model.
2. `docs/README.md` — the documentation index (one row per topic).
3. `.aii/README.md` and `.aii/AGENTS.md` — InstituteOS sidecar metadata.
4. `docs/manuscript/README.md` + `docs/manuscript/SYNTAX.md` — manuscript
   conventions (plus `docs/manuscript/AGENTS.md`).

## Commands (from the repository root)

```bash
python3 scripts/ontology.py validate --strict   # full source/artifact gate
python3 scripts/ontology.py report              # quality + integrity report
python3 scripts/ontology.py diff OLD.json NEW.json
python3 scripts/manuscript.py validate --strict
```

The full acceptance gate is documented in `CONTRIBUTING.md`. On hosts whose
matplotlib rasterization differs from CI, run manuscript checks with
`MANUSCRIPT_PORTABLE_CHECK=1` (figure bytes only; all other integrity checks
stay enforced).

## Conventions

- Conventional commits (`docs:`, `fix:`, `chore:`, `feat:`); multiple
  logical commits preferred over one large commit.
- The scoped worklog is `TO-DO.md` (hyphenated). A root `TODO.md` must not
  exist — a regression test enforces that.
- All prose must stay public-safe: no local paths, personal tooling,
  credentials, or internal workflow details.
- Do not commit generated artifacts as a side effect of unrelated changes;
  regenerate and commit them only when their inputs changed.
