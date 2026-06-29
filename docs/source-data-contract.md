# Source Data Contract

The canonical ontology source is the latest `Ontology_v*.csv` file in the
repository root. As of this repository state, that file is
`Ontology_v5_May_25_2023.csv`.

## Required Columns

| Column | Required | Meaning |
| --- | --- | --- |
| `List` | Yes | Release or working-list grouping, such as `Core`. |
| `Tag` | Yes | High-level conceptual area for the term. |
| `Term` | Yes | Human-readable concept label and primary identity key. |
| `Proposed Definition 1` | Recommended | Broad or primary definition. |
| `Proposed Definition 2` | Optional | Narrow, technical, or alternate definition. |
| `Correct Examples` | Recommended | Examples that illustrate valid use of the term. |
| `Incorrect Examples` | Recommended | Counter-examples or misuse cases. |
| `Connections` | Recommended | Free-text references to related ontology terms. |

## Tag Set

The current export contains eight tags:

- `Action`
- `Agents in the Niche`
- `Bayesian Statistics`
- `Free Energy`
- `Information`
- `Markov Partitioning`
- `Perception`
- `Systems`

New tags should be introduced deliberately because each tag becomes a graph node
type in the JSON export and may be used by downstream filters.

## Row Rules

- Every row must have a non-empty `Term`.
- Terms are treated as unique case-insensitively by the JSON builder.
- Duplicate terms after case normalization are skipped after the first
  occurrence.
- Multi-line CSV fields are allowed, but downstream export normalizes repeated
  whitespace to single spaces.
- Keep examples and counter-examples in plain prose unless a downstream parser
  contract is added.

## Term Identity

`scripts/build_json.py` derives each term id from the normalized term label:

```text
term-<lowercase-term-with-non-alphanumeric-runs-replaced-by-hyphens>
```

For example, `Bayesian Inference` becomes `term-bayesian-inference`.

Renaming a term changes its derived id and can break downstream links. Prefer
adding an alias or migration note before renaming terms that external tools may
already consume.

## Connections Field

The `Connections` field is free text. During JSON export, the builder searches
that field for exact case-insensitive term-name mentions and creates graph edges
between the source term and each referenced term.

This means connection text should use the canonical term spelling whenever
possible. Abbreviations, aliases, or partial names are not guaranteed to become
edges.
