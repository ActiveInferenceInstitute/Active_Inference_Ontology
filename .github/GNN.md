# GNN conformance

The conformance gate is the workflow job with key `gnn-conformance` and display name
`gnn conformance (pinned)` in [`.github/workflows/ontology.yml`](workflows/ontology.yml).
Its single step runs `./run.sh gnn`, the arm defined in [`../run.sh`](../run.sh); run the
same command locally.

## Pin

The canonical pin is [`.github/gnn-pin.json`](gnn-pin.json) with schema
`gnn-importer-pin/v1`:

| Field | Value |
| --- | --- |
| `repository` | `ActiveInferenceInstitute/Generalized_Notation_Notation` |
| `revision` | `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1` |
| `tag` | `v5.0.3` |
| `recorded` | `2026-11-12` |

The arm installs the parser-side dependency file (`requirements-gnn.txt`), then uses
`gnn.importers.read_pin` to obtain the revision for
`validate_gnn_conformance.py --install`. After materialization it calls the shared
reader directly:

```bash
python -m gnn.importers check --repo . --require-pointer \
    --workflow .github/workflows/ontology.yml --job gnn-conformance
```

Pin normalization and pin/pointer/specification validation belong to that upstream
module, not a local copy. This follows the
[GNN–FEP workflow contract](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation/blob/main/docs/workflows/gnn-fep.md).

### Migration blocker

The revision above predates `gnn.importers`, so its installed package cannot run
either `read_pin` or the reader command. A fresh environment also cannot use
`read_pin` to bootstrap its own installation. This migration therefore remains
unmergeable until the upstream reader is available under the member's pin and the
contract defines how an empty environment obtains it. No alternate reader,
unpinned fallback, or duplicate revision is introduced here.

## What the job parses

1. [`gnn-pin.json`](gnn-pin.json), [this pointer](GNN.md), and any `*.gnn.md`
   specifications: `gnn.importers check` owns their validation. The ontology carries
   a vocabulary bridge rather than a generative-model specification.
2. [`../GNN/declared-labels.json`](../GNN/declared-labels.json): the recorded `source`
   provenance (`repository`, `commit`, `release`, vocabulary `sha256`) and the reviewed
   label set.
3. The pinned parser package itself (`gnn`): its `__version__` must equal the pin's tag
   without the `v`, its bundled `ontology/act_inf_ontology_terms.json` bytes must match the
   recorded digest, and its term set must equal the reviewed labels exactly.
4. [`../GNN/act_inf_ontology_terms.json`](../GNN/act_inf_ontology_terms.json): the
   generated bridge must declare exactly those labels, each either `resolved` to a
   `term-…` identifier or `unresolved` with no identifier.

The step that follows is `python3 scripts/ontology.py gnn-terms --check`, which proves the
committed bridge is still the deterministic projection of the canonical source. This
records vocabulary and pin conformance, not a claim that the repository contains a
generative model.

## Workflow environment

The jobs use pinned `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1)
and `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` (v7.1.0). This
repository does not use the shared
`ActiveInferenceInstitute/.github/.github/actions/setup-python-uv@7159e67315330aac8e414aebae0ad1e999a41448`
composite action: its dependencies stay in the pinned `requirements-*.txt` files, which the
arms install with `python -m pip`, so a local run and a hosted run resolve the same pins.
