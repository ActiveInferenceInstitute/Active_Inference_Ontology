# Active Inference Ontology Manuscript

This directory contains the template-compatible source and generated publication artifacts for the ontology data descriptor. It follows the template project conventions for ordered Markdown sections, labeled equations, cross-referenced figures and tables, `config.yaml`, `preamble`, a bibliography, a claim ledger, and generated manuscript variables.

## Commands

```text
python3 scripts/manuscript.py generate
python3 scripts/manuscript.py validate --strict
python3 scripts/manuscript.py render --format all
python3 scripts/manuscript.py check
```

The source sections contain `{{VARIABLE}}` markers. The generator resolves them into `output/manuscript/`, computes deterministic PNG figures in `output/figures/`, and records hashes in `artifact-manifest.json`. The root ontology pipeline remains the canonical content and release gate.

For template repository preflight, set `TEMPLATE_ROOT` to a local checkout of the InstituteOS template and run its manuscript validation command against this directory. The repository itself does not depend on that checkout at runtime.
