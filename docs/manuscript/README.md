# Active Inference Ontology Manuscript

This directory contains the template-compatible source and generated publication artifacts for the ontology data descriptor. It follows the template project conventions for ordered Markdown sections, labeled equations, cross-referenced figures and tables, `config.yaml`, `preamble`, a bibliography, a claim ledger, and generated manuscript variables. It is part of the [repository documentation index](../README.md); see [`docs/build-and-validation.md`](../build-and-validation.md) for the full validation gate.

## Commands

```text
python3 scripts/manuscript.py generate
python3 scripts/manuscript.py validate --strict
python3 scripts/manuscript.py render --format all
python3 scripts/manuscript.py check
```

The source sections contain `{{VARIABLE}}` markers. The generator resolves them into `output/manuscript/`, computes deterministic PNG figures in `output/figures/`, and records hashes in `artifact-manifest.json`. The manifest is closed over the expected inputs and generated outputs, including byte counts and SHA-256 values. Each figure registry entry also records a digest of the source values used to generate that figure.

Local `generate --check` compares figure bytes directly. The committed PNGs are not
reproducible with the pinned toolchain on other hosts, so set
`MANUSCRIPT_PORTABLE_CHECK=1` where rasterized font bytes differ; the registry input
digests, generated-artifact freshness checks, manifest hashes, and a structural
figure-asset check remain enforced. The manuscript job regenerates the artifacts in the CI
toolchain and then requires byte-identity for every non-rasterized artifact. The root
ontology pipeline remains the canonical content and release gate.

For template repository preflight, set `TEMPLATE_ROOT` to a local checkout of the InstituteOS template and run its manuscript validation command against this directory. The repository itself does not depend on that checkout at runtime.
