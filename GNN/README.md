# GNN vocabulary bridge

This directory holds the bridge between this ontology and the
[GNN pipeline](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation)
`ActInfOntologyAnnotation` vocabulary used by its Step 10 ontology processing.

| Path | Role |
| --- | --- |
| [`declared-labels.json`](declared-labels.json) | Reviewed input: the 64 labels declared by GNN's bundled vocabulary file at the pinned revision, with the exact source provenance and the `obo:` values GNN declares for audit. |
| [`act_inf_ontology_terms.json`](act_inf_ontology_terms.json) | Generated bridge (schema `active-inference-ontology/gnn-terms/v1`): every canonical ontology label projected to its stable ID, plus the resolution status of each declared GNN label. |

Regenerate or verify from the repository root:

```bash
python3 scripts/ontology.py gnn-terms
python3 scripts/ontology.py gnn-terms --check
```

`validate` fails when the generated bridge is stale, so the artifact cannot drift
from the canonical source. The declared GNN labels resolve by normalized label
equality only (casefold, drop characters outside `[a-z0-9]`); labels with no
counterpart stay `unresolved` with a null target. No identifier is guessed, and
GNN's non-resolving `obo:ACTO_*` / `obo:TEMP_*` placeholders are never adopted as
identifiers. The consumer contract is in
[`docs/downstream-integration.md`](../docs/downstream-integration.md).
