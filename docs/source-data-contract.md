# Source Data Contract

The canonical source is `ontology.source.json`, schema
`active-inference-ontology/source/v2`. Paths and policy are configured in
[`../ontology.toml`](../ontology.toml).

## Release

`release.version`, `release.label`, and ISO `release.date` identify the content
release. The release version must match `ontology.toml` and `releases.json`.

## Term fields

Each `terms[]` record contains:

| Field | Meaning |
| --- | --- |
| `id` | Explicit stable opaque identifier matching the `term-...` syntax. It is assigned during initial migration and does not change when a display label is renamed. |
| `term` | Canonical display label. |
| `aliases` | Alternate labels, unique across all labels and aliases. |
| `status` | `published`, `draft`, `deprecated`, `merged`, or `retired`. |
| `list` | `Core`, `Entailed`, or `Supplement`. |
| `tag` | One of the configured tags, or `null` where historical material is untagged. |
| `definitions` | `primary` and `secondary` text values. |
| `examples` | `correct` and `incorrect` text values. |
| `connectionsText` | Preserved free-text connection notes, or `null`. |
| `relations` | Explicit target IDs and relation types. |
| `provenance` | Original source filename and row for the v5 migration. |

Core terms require a tag, primary definition, and correct example. Entailed and
Supplement terms may retain missing historical fields; the report counts those
gaps rather than silently presenting the source as complete.

## Identity and relation policy

Display labels and IDs are separate fields. A label rename is valid when the ID is
retained; aliases can preserve a previous label when that is useful for discovery.
The diff command reports both ordinary and case-only label changes by ID.

The migration creates only `mentions` relations when a canonical label appears in
`connectionsText`. Stronger types—`related`, `inverse`, `prerequisite`, `part_of`,
`broader`, `narrower`, `contrasts`, and `causes`—require explicit curation.
Every target must resolve to an existing stable ID and self-relations are rejected.

## Spreadsheet export

`Ontology_v5_May_25_2023.csv` retains the original eight columns for spreadsheet
users. It is generated from the structured source with normalized whitespace and
must be refreshed with `python3 scripts/ontology.py export-csv`.
