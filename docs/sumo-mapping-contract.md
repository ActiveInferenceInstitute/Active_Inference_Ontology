# SUMO Mapping Contract

Use this contract for durable mappings between Active Inference Ontology terms
and Suggested Upper Merged Ontology concepts.

## Mapping Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `term_id` | Yes | Active Inference Ontology term id, such as `term-accuracy`. |
| `term` | Yes | Canonical ontology term label. |
| `sumo_id` | Yes | SUMO concept id or IRI. |
| `sumo_label` | Recommended | Human-readable SUMO label. |
| `mapping_relation` | Yes | One of `exact`, `broad`, `narrow`, `related`, `candidate`, or `rejected`. |
| `confidence` | Recommended | Decimal from `0` to `1`, or a controlled label if numeric scoring is not available. |
| `review_status` | Yes | One of `draft`, `reviewed`, `accepted`, `rejected`, or `superseded`. |
| `reviewer` | Recommended | Person or group responsible for the mapping judgment. |
| `review_date` | Recommended | ISO date for the latest review. |
| `evidence` | Recommended | Short source note, citation, or rationale. |
| `notes` | Optional | Additional mapping notes. |

## Relation Semantics

| Relation | Use when |
| --- | --- |
| `exact` | The Active Inference term and SUMO concept can be used interchangeably in the mapped context. |
| `broad` | The SUMO concept is broader than the Active Inference term. |
| `narrow` | The SUMO concept is narrower than the Active Inference term. |
| `related` | The concepts are meaningfully connected but not hierarchical or exact. |
| `candidate` | The mapping is plausible but not reviewed. |
| `rejected` | A proposed mapping was reviewed and should not be used. |

## Template

Use [`../SUMO/mapping-template.csv`](../SUMO/mapping-template.csv) for new
mapping work.

## Review Rules

- Map against stable ontology term ids from `ontology.json`.
- Keep rejected mappings when they prevent repeated false-positive proposals.
- Update `review_status`, `reviewer`, and `review_date` whenever a mapping is
  promoted or rejected.
- Do not promote SUMO mappings back into the canonical CSV without the curation
  governance process.
