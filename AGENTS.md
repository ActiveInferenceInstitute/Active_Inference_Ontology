# Agent guide — Active Inference Ontology

Orientation for AI agents and automation working in this repository.

## Ground truth

- `ontology.source.json` (schema `active-inference-ontology/source/v2`) is the
  only editable ontology surface; `ontology.toml` configures paths, release
  metadata, and validation policy.
- `ontology.json`, `Ontology_v5_May_25_2023.csv`, `site/index.html`,
  `releases.json`, `GNN/act_inf_ontology_terms.json`, and everything under
  `docs/manuscript/output/` are generated. Regenerate them with the CLI;
  never edit them by hand. `GNN/declared-labels.json` is reviewed input, not
  generated.
- `Archived versions/` is immutable historical evidence — never rewrite it.
- Every claim about counts, edges, tags, or hashes should be verified by
  running the CLI (or reading the manifest), not copied from prose.

## Reading order

1. `README.md` — surfaces, CLI, source model.
2. `docs/README.md` — the documentation hub (one row per topic); `docs/documentation-index.md`
   is the flat index of every long-lived document.
3. `.aii/README.md` and `.aii/AGENTS.md` — InstituteOS sidecar metadata.
4. `docs/manuscript/README.md` + `docs/manuscript/SYNTAX.md` — manuscript
   conventions (plus `docs/manuscript/AGENTS.md`).

## Commands (from the repository root)

`run.sh` is the only definition of the gate commands; the public workflow calls the
same arms.

```bash
./run.sh deps        # one locked install
./run.sh fast        # inner loop: source/export/manifest/sidecar contracts
./run.sh all         # every arm the public workflow runs
./run.sh docs        # documentation links, anchors, index, generated numbers
```

For a single CLI invocation:

```bash
python3 scripts/ontology.py validate --strict   # full source/artifact gate
python3 scripts/ontology.py report              # quality + integrity report
python3 scripts/ontology.py gnn-terms --check   # GNN vocabulary bridge freshness
python3 scripts/ontology.py diff OLD.json NEW.json
python3 scripts/manuscript.py validate --strict
python3 -m unittest discover -s tests -v   # regression suite
```

The full acceptance gate is documented in `CONTRIBUTING.md` and
`docs/build-and-validation.md`; measured arm wall time is generated into
`docs/_generated/gate.md` by `./run.sh bench`. On hosts whose
matplotlib rasterization differs from the committed figures, run manuscript
checks with `MANUSCRIPT_PORTABLE_CHECK=1` (figure bytes only; all other
integrity checks stay enforced); CI regenerates the figures in its own
toolchain and compares every other artifact byte-exactly.

## Conventions

- Conventional commits (`docs:`, `fix:`, `chore:`, `feat:`); multiple
  logical commits preferred over one large commit.
- The scoped worklog is `TO-DO.md` (hyphenated). A root `TODO.md` must not
  exist — a regression test enforces that.
- All prose must stay public-safe: no local paths, personal tooling,
  credentials, or internal workflow details.
- Do not commit generated artifacts as a side effect of unrelated changes;
  regenerate and commit them only when their inputs changed.
