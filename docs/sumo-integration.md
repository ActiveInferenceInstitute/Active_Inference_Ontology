# SUMO Integration

The `SUMO/` folder contains material for working with Sigma and the Suggested
Upper Merged Ontology environment.

## Files

| File | Role |
| --- | --- |
| `SUMO/READ_ME_SigmaVM.txt` | Operational notes for obtaining or creating the Sigma VM and starting Sigma services. |
| `SUMO/SigmaVM_Full_History.txt` | Command history for building the Sigma VM environment from a base Ubuntu server. |

## Scope

The SUMO material is supporting infrastructure. It is not currently consumed by
`scripts/build_json.py`, and it does not define the canonical term list used for
`ontology.json`.

Use the SUMO folder for:

- ontology alignment experiments;
- reproducing a Sigma/SUMO working environment;
- documenting mapping decisions between Active Inference terms and upper
  ontology concepts.

Use [SUMO Mapping Contract](sumo-mapping-contract.md) and
[`SUMO/mapping-template.csv`](../SUMO/mapping-template.csv) for durable
mapping work.

Do not use the SUMO folder as a substitute source of truth for term definitions
unless a release process explicitly promotes mapped terms back into the root CSV.

## Handling Notes

- Keep VM credentials or access instructions out of public issue threads unless
  they are intentionally public.
- Prefer adding mapping tables or notes as plain text, CSV, TSV, or Markdown so
  they can be reviewed in diffs.
- If a generated mapping artifact is added, document the source command and
  input files beside it.

## Mapping Contract

A durable SUMO mapping defines:

- Active Inference term id;
- canonical term label;
- SUMO concept id or IRI;
- mapping relation such as exact, broad, narrow, or related;
- reviewer;
- review date;
- confidence or status.
