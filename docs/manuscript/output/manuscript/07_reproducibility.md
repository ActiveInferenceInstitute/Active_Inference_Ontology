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
