# Active Inference Ontology Manuscript

This directory contains the template-compatible source and generated publication artifacts for the ontology data descriptor. It follows the template project conventions for ordered Markdown sections, labeled equations, cross-referenced figures and tables, `config.yaml`, `preamble`, a bibliography, a claim ledger, and generated manuscript variables. It is part of the [repository documentation index](../README.md); see [`docs/build-and-validation.md`](../build-and-validation.md) for the full validation gate.

## Commands

Run the `manuscript` gate arm, which is the same command set the public workflow runs
(see [`../build-and-validation.md`](../build-and-validation.md)):

```text
./run.sh manuscript        # read-only freshness, render provenance, validate --strict, check
./run.sh render            # render --format all, then check (Pandoc, pandoc-crossref, XeLaTeX, qpdf)
```

The underlying commands are `python3 scripts/manuscript.py` with the subcommands
`generate`, `manifest`, `render --format all`, `validate --strict`, and `check`.

The source sections contain `{{VARIABLE}}` markers. The generator resolves them
into `output/manuscript/` and computes PNG figures in `output/figures/`.
The `active-inference-ontology/manuscript/v2` manifest closes over the expected
inputs and generated outputs, including byte counts, SHA-256 values, and
figure-input digests.

Each successful format render records
`output/<format>/active_inference_ontology.<format>.render.json` with input hashes,
invocation/environment, toolchain identity, and output hash/size. `manifest`
does not create render provenance and rejects absent or stale render records.
A partial render updates only its own format and preserves other formats'
original receipts, including stale records.

Existing unbound publications require an explicitly admitted `render --format all`
in a separate disposable copy; never synthesize receipts from existing output
hashes. `./run.sh manuscript` checks existing evidence without regeneration;
`./run.sh render` renders all formats and then checks.

Local `generate --check` compares figure bytes directly. Set
`MANUSCRIPT_PORTABLE_CHECK=1` only where host rasterization differs. This affects
PNG-byte comparison, not input fingerprints, generated freshness, render
provenance, or output hashes. Preserve existing artifact edits; publication
requires separate integration custody. The root ontology pipeline remains
the canonical content and release gate.

For template repository preflight, set `TEMPLATE_ROOT` to a local checkout of the InstituteOS template and run its manuscript validation command against this directory. The repository itself does not depend on that checkout at runtime.
