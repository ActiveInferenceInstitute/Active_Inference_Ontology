# Abstract {#sec:abstract}

This article describes the publication-grade data and software pipeline for the Active Inference Ontology. The release contains 429 terms and 238 explicit typed relations across the Core, Entailed, and Supplement lists. The ontology preserves the source prose while making identity, aliases, status, metadata, relations, provenance, schemas, and generated exports explicit. A deterministic command-line pipeline validates the source, produces JSON and CSV artifacts, builds a dependency-free browser, and records release hashes. A template-compatible manuscript layer derives its tables, figures, metrics, and provenance from the same release boundary. This design separates semantic curation from mechanical transformation: existing free-text connections are represented as `mentions`, while stronger relation types remain available for future reviewed curation. The resulting artifact supports machine reuse, human inspection, reproducible regeneration, and explicit quality reporting. We present the source model, graph and integrity formalism, implementation, release results, limitations, and reproducibility procedure. The current release is v5 (May 25, 2023), with source SHA-256 `82fc5b03b3110e9dd9f74049d7ea0e578e05541a3cdeb0c6c24eaa0f99a9be0f`.

**Keywords:** active inference; ontology engineering; knowledge representation; reproducible data; provenance; JSON Schema; software publication


# Introduction {#sec:introduction}

Active inference is used across neuroscience, cognitive science, biology, and theoretical approaches to adaptive agency. Its vocabulary spans mathematical constructs, modeling practices, empirical descriptors, and explanatory terms. A shared ontology can make those terms discoverable and comparable, but only if its records preserve provenance and distinguish documented content from later interpretation. The present repository provides such an artifact for the Active Inference Institute community.

The central contribution is a release process rather than a claim that the vocabulary is complete or universally settled. The current content is the May 25, 2023 release, represented without unsourced semantic rewriting. Its spreadsheet lineage is retained, while a structured source document becomes the sole editable model. Each term has a stable opaque identifier, a display label, aliases, curation status, list membership, optional tag, structured definitions and examples, raw connection prose, and explicit relation records. This separation is aligned with ontology-engineering practice: identifiers provide continuity while labels and descriptions remain revisable [@gruber1993; @studer1998].

The publication artifact addresses three practical questions. First, how can a historical terms list become a machine-readable graph without silently strengthening its semantics? Second, how can generated JSON, CSV, site, manuscript, and archive metadata be checked as one release? Third, how can a reader reproduce the reported counts and inspect the source evidence? The answers are formalized in [@sec:methods] and evaluated in [@sec:results].

The pipeline reports the current release as 429 terms, 238 explicit relations, and 8 populated tags. These counts describe the release artifact, not a measurement of the scientific validity or conceptual sufficiency of active inference. The distinction matters because ontology quality includes scope, coverage, consistency, and fitness for use, while automated validation can only establish the properties expressed by its contract.

The manuscript makes four contributions:

1. an explicit source model with stable term identity and typed graph edges;
2. deterministic export, site, manuscript, and release-manifest generation;
3. fail-closed structural, schema, freshness, and integrity validation; and
4. a transparent account of coverage, gaps, historical provenance, and future curation boundaries.


# Related Work {#sec:related-work}

Ontology engineering treats a vocabulary as an artifact whose conceptual commitments, identifiers, documentation, and maintenance process must be made explicit. Gruber's account of portable ontology specifications emphasizes shared conceptualization and explicit specification [@gruber1993]. Studer, Benjamins, and Fensel similarly frame ontology engineering as a knowledge-engineering activity involving conceptualization, formalization, and maintenance [@studer1998]. The present artifact adopts the maintenance implication: labels may change while stable identifiers preserve continuity, and relation semantics must be curated rather than inferred from incidental text matches.

The release is compatible with the distinction between controlled vocabulary and richer ontology. SKOS provides a standard model for concepts, labels, notes, and semantic relations [@skos2009]. This repository uses a deliberately smaller, domain-specific source contract: it records explicit term records and typed relations while retaining raw connection text. That choice makes the current migration auditable and leaves room for later mappings to SKOS, OWL, or other formal representation systems. The current relation graph should therefore be read as a curation record, not as a completed logical theory.

The scientific domain motivates the vocabulary but does not determine the pipeline. Free-energy and active-inference scholarship provides the conceptual context for terms concerning prediction, action, perception, learning, and adaptive regulation [@friston2010; @parr2022]. This manuscript does not adjudicate competing interpretations of those concepts. It documents how a community vocabulary is represented, validated, and released so that future conceptual work can cite a stable artifact.

Reproducibility literature places unique identifiers, explicit data transformations, version control, and executable workflows at the center of trustworthy computational work [@peng2011; @wilson2017; @sandve2013]. FAIR principles further emphasize that data should be findable, accessible, interoperable, and reusable [@wilkinson2016]. The pipeline operationalizes these principles through a canonical source, deterministic generators, machine-readable schemas, SHA-256 manifests, an executable validation suite, and a browser artifact that exposes provenance to readers.

Finally, W3C PROV-DM provides a general vocabulary for describing entities, activities, and agents in provenance records [@prov2013]. The present manifest is narrower: it records source and generated-file hashes, release metadata, and validation summaries. It is intentionally sufficient for this repository's release boundary and can be mapped to a richer provenance model in a future integration.


# Methods {#sec:methods}

## Source model

Let the ontology release be the tuple

$$
\mathcal{O} = (T, R, M, P)
$$ {#eq:ontology-model}

where $T$ is the finite set of term records, $R$ is the set of typed relation records, $M$ is release and schema metadata, and $P$ is the provenance and integrity record. A term record $t \in T$ contains an opaque identifier, a display label, aliases, status, list, nullable tag, structured definitions, structured examples, raw connection text, and outgoing relations. The source document at `ontology.source.json` is the only editable representation. The CSV, JSON export, browser, and manuscript are derived artifacts.

The identity rule is explicit:

$$
\operatorname{id}(t) = i_t, \qquad i_t \in \mathcal{I}, \qquad \operatorname{label}(t) \in \mathcal{L}
$$ {#eq:term-identity}

where the identifier set $\mathcal{I}$ is validated independently from the label set $\mathcal{L}$. A label rename therefore preserves identity when $i_t$ is unchanged. Labels and aliases are unique case-insensitively across the release. Initial migration identifiers were derived from labels only because no earlier stable identifier field existed; subsequent curation must retain the assigned identifier.

## Relation graph and migration

The graph exported to `ontology.json` is

$$
G = (V, E), \qquad V = \{i_t : t \in T\}, \qquad E \subseteq V \times \mathcal{R} \times V
$$ {#eq:typed-graph}

where $\mathcal{R}$ is the configured relation vocabulary. The current release uses only `mentions` edges. During migration, a connection string is searched for exact case-insensitive occurrences of other display labels; each occurrence produces one explicit `mentions` edge after duplicate suppression. No stronger relation is inferred from the text. Self-relations, unknown targets, duplicate edges, invalid identifiers, and unsupported relation types fail validation.

![Canonical source, validation, export, and publication flow.](../figures/pipeline_provenance.png){#fig:pipeline width=92%}

## Deterministic generation and validation

The generator is a pure transformation of the configured source and release metadata:

$$
\operatorname{artifact}_k = F_k(\mathcal{O}, C), \qquad H_k = \operatorname{SHA256}(\operatorname{bytes}(\operatorname{artifact}_k))
$$ {#eq:deterministic-generation}

where $C$ is `ontology.toml`, $F_k$ is the generator for artifact $k$, and $H_k$ is recorded in the release manifest. JSON keys and graph edges are sorted, CSV rows follow source order, and figures use fixed data, styles, dimensions, and metadata. Atomic writes prevent partially written text artifacts from becoming release state.

Validation is expressed as a conjunction of configured predicates:

$$
\operatorname{Valid}(\mathcal{O}, C) = \bigwedge_{p \in \Pi_C} p(\mathcal{O}, C)
$$ {#eq:validation-predicate}

The predicate set includes JSON shape, required fields, enumerations, identifier and target validity, cross-record uniqueness, source/export equality, CSV and site freshness, manifest paths and hashes, numeric release order, and strict JSON Schema validation with the pinned `jsonschema` dependency [@jsonschema2020]. Core terms require tags, primary definitions, and correct examples; permitted gaps remain reportable for Entailed and Supplement terms.

## Release integrity

For every listed artifact, the manifest must close the path and hash relation:

$$
\operatorname{ManifestOK}(a) \Longleftrightarrow \operatorname{exists}(a.path) \land \operatorname{SHA256}(a.path) = a.sha256
$$ {#eq:manifest-integrity}

The current release includes the source, CSV, JSON export, site, three schemas, and validation summary. Historical releases remain immutable archive evidence; their metadata is explicitly marked as not evaluated where the current v2 contract cannot be retroactively established.


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


# Discussion {#sec:discussion}

The release makes a useful boundary visible: the ontology is a curated vocabulary artifact with executable integrity guarantees, not a claim that every term or relation has been formally resolved. Stable identifiers and explicit statuses support longitudinal curation. Structured definitions and examples permit downstream applications to distinguish missing data from intentionally nullable fields. Raw connection prose remains available alongside the typed graph, which lets reviewers inspect how each migrated edge was produced.

The strict pipeline also changes what “reproducible” means for a vocabulary. A reader can reproduce the JSON, CSV, site, figures, tables, and manuscript from the source and pinned configuration. Hashes identify the exact inputs and outputs. The result is stronger than a static download, but it remains bounded by the source content and by the predicates implemented in the validators. Schema validity does not establish conceptual truth, and a passed freshness check does not certify semantic adequacy.

## Limitations

The primary limitation is temporal: the current content is a May 2023 snapshot. The repository records historical v1–v4 material but does not reinterpret those archives under the v2 source schema. The current release has 355 terms without tags, 339 without primary definitions, 359 without correct examples, 359 without incorrect examples, and 389 without connection text. These are measured source properties, not silently repaired values.

The second limitation is semantic. The migration creates only `mentions` relations from textual references. It does not infer `broader`, `narrower`, `causes`, `part_of`, `inverse`, `prerequisite`, `contrasts`, or `related` edges. Future curation can add those relations with explicit review, provenance, and regression tests.

The third limitation is representational. The source schema is intentionally compact and does not yet provide multilingual labels, formal axioms, external concept identifiers, or a complete SKOS/OWL serialization. Those are extension points rather than hidden assumptions. The current design favors transparent preservation and deterministic publication while the conceptual model matures.


# Conclusion {#sec:conclusion}

This work turns a historical active-inference terms list into a reproducible publication artifact. The release has one canonical structured source, stable term identities, explicit metadata, a conservative typed graph, generated exports, a dependency-free browser, release hashes, and strict executable validation. The manuscript is generated from the same release boundary, so the reported metrics, tables, figures, and provenance can be regenerated rather than copied by hand.

The immediate value is operational: researchers and software can cite a stable release, inspect its source, distinguish explicit relations from later interpretation, and detect stale or tampered artifacts. The longer-term value is curatorial: future revisions can add aliases, statuses, stronger reviewed relations, mappings, and richer provenance while retaining the identity and validation contracts established here.

The current release should therefore be used as a documented baseline for community review. Its measured gaps and conservative relation policy are part of the artifact’s meaning. They define where future scholarship and curation can contribute without obscuring the provenance of the current vocabulary.


# Reproducibility {#sec:reproducibility}

The complete release can be regenerated from a clean checkout with Python 3.11 or later, the pinned dependencies in `requirements-ci.txt` and `requirements-manuscript.txt`, Pandoc, `pandoc-crossref`, and XeLaTeX. The ontology command is the source gate:

```text
python3 scripts/ontology.py validate --strict
python3 scripts/ontology.py build --check
python3 scripts/ontology.py export-csv --check
python3 scripts/ontology.py site --check
```

The manuscript commands then generate and render the publication layer:

```text
python3 scripts/manuscript.py generate
python3 scripts/manuscript.py validate --strict
python3 scripts/manuscript.py render --format all
python3 scripts/manuscript.py check
```

The freshness condition for a generated artifact is

$$
\operatorname{Fresh}(a) \Longleftrightarrow a_{generated} = F_a(\operatorname{source}, \operatorname{configuration}, \operatorname{toolchain})
$$ {#eq:freshness}

The manuscript manifest records the source hash, export and release-manifest input hashes, every generated figure and resolved section hash, and the four rendered publication hashes. `check` recomputes those values and fails if a path is missing or a byte sequence differs. The release manifest independently checks the ontology artifacts described in [@sec:methods].

The regression suite exercises source migration, stable identity, duplicate detection, malformed data, relation targets, schema rejection, release ordering, case-only changes, CSV diagnostics, external migration output, sidecar invocation, and generated-artifact freshness. The manuscript suite adds deterministic figure bytes, source-variable accuracy, label/reference resolution, bibliography completeness, image existence, output smoke checks, manifest tampering, and active lexical hygiene.

The browser artifact at `site/index.html` is dependency-free and includes source provenance, aliases, definitions, examples, status, tags, and incoming and outgoing relation neighborhoods. It is generated from `ontology.json`; the manuscript is generated from the same source and manifest, providing two independent human-facing views of one release boundary. The repository itself is a citable software and data artifact [@activeinferenceontology2023].


# References {#sec:references}

The bibliography is stored in [`references.bib`](references.bib) and is processed by Pandoc during rendering. The release validator checks that every cited key exists, that every entry has the required author, title, and year fields, and that type-specific metadata is present for articles, books, datasets, software, and proceedings.
