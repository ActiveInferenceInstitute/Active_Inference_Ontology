# GNN conformance

`gnn conformance (pinned)` is defined in `.github/workflows/ontology.yml` and
reads `.github/gnn-pin.json`, which pins
`ActiveInferenceInstitute/Generalized_Notation_Notation` at `v5.0.3`
(`8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`).

The job installs the pinned GNN parser and checks the GNN vocabulary bridge:
the reviewed labels in `GNN/declared-labels.json`, the bridge validator
`scripts/validate_gnn_conformance.py`, and the generated-term freshness check
`scripts/ontology.py gnn-terms --check`. This records vocabulary and pin
conformance, not a claim that the repository contains a generative model.
