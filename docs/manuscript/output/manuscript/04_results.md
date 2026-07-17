# Results {#sec:results}

## Release profile

The generated profile is shown in [@tbl:profile]. The source contains 429 terms, distributed as Core=64, Entailed=73, Supplement=292. All current terms have status `published`; the status field remains explicit so later releases can record draft, deprecated, merged, or retired records without changing the export shape.

| Measure | Value |
|---|---:|
| Terms | 429 |
| Explicit relations | 238 |
| Distinct tags | 8 |
| Core terms | 64 |
| Entailed terms | 73 |
| Supplement terms | 292 |
| Published terms | 429 |

: Profile of the current ontology release. {#tbl:profile}


[@fig:composition] visualizes the list distribution. The largest list is Supplement, while Core and Entailed provide smaller curated subsets. The distribution is descriptive of this release and should not be interpreted as a ranking of scientific importance.

![Terms grouped by curation list in the current release.](../figures/term_composition.png){#fig:composition width=82%}

## Graph structure

The graph contains 238 edges. [@tbl:relations] and [@fig:relations] show that every current edge has type `mentions`. This result is expected from the conservative migration rule: free-text connections are preserved as auditable references without automatic semantic strengthening.

| Relation type | Edges |
|---|---:|
| mentions | 238 |

: Explicit relation types in the current graph. {#tbl:relations}


![Distribution of explicit relation types.](../figures/relation_structure.png){#fig:relations width=82%}

## Metadata coverage

The source preserves historical sparsity rather than fabricating values. [@tbl:completeness] reports populated and missing fields. Core terms satisfy the configured required metadata contract, while blank optional metadata in Entailed and Supplement records remains visible in the report. This distinction prevents structural completeness from being confused with content completeness.

| Field | Present | Missing | Coverage |
|---|---:|---:|---:|
| Tag | 74 | 355 | 17.2% |
| Primary definition | 90 | 339 | 21.0% |
| Correct example | 70 | 359 | 16.3% |
| Incorrect example | 70 | 359 | 16.3% |
| Connection text | 40 | 389 | 9.3% |

: Field coverage in the source record model. {#tbl:completeness}


![Coverage of optional and required descriptive fields.](../figures/metadata_completeness.png){#fig:metadata width=88%}

## Release and artifact integrity

The manifest records the release lineage in [@tbl:releases] and current artifact paths and hashes in [@tbl:artifacts]. The historical sequence is retained as v1 through v5, with v5 as the current structured release. [@fig:release] shows the sequence; [@fig:validation] summarizes the current release gates.

| Release | Label | Date | State |
|---|---|---|---|
| v1 | Terms list candidate | not recorded | archived |
| v2 | T2.D1.L1.E1 | not recorded | archived |
| v3 | Version 3 | not recorded | archived |
| v4 | 12-12-2022 snapshot | 2022-12-12 | archived |
| v5 | May 25, 2023 | 2023-05-25 | current |

: Release lineage recorded by the manifest. {#tbl:releases}


| Kind | Path | SHA-256 prefix |
|---|---|---|
| source | `ontology.source.json` | `82fc5b03b311…` |
| spreadsheet-export | `Ontology_v5_May_25_2023.csv` | `f6d3648f7961…` |
| export | `ontology.json` | `a2c8371264e9…` |
| site | `site/index.html` | `0256e585a904…` |
| schema | `schemas/source-v2.json` | `6c6bf6235c49…` |
| schema | `schemas/export-v2.json` | `f6591a1a5c9c…` |
| schema | `schemas/manifest-v2.json` | `5797225849a5…` |

: Current-release artifact closure. {#tbl:artifacts}


![Historical release sequence and current validation boundary.](../figures/release_history.png){#fig:release width=88%}

![Validation gates applied to the current generated release.](../figures/validation_integrity.png){#fig:validation width=88%}
