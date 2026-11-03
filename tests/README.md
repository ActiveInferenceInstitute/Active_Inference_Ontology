# Regression tests

Run the suite from the repository root:

```bash
python3 -m pip install -r requirements-ci.txt
python3 -m unittest discover -s tests -v
```

CI runs the same command in
[`.github/workflows/ontology.yml`](../.github/workflows/ontology.yml).

- `test_ontology.py` — source, export, and manifest contracts: schema
  validation, stable IDs across label renames, duplicate IDs/labels/aliases,
  self-relations and invalid statuses, allowed historical gaps, stale generated
  artifacts, manifest hashes/order/symlink escape, mention-relation
  conservatism, CSV audit, external migration output, and configured source
  selection.
- `test_manuscript.py` — release counts in generated variables, deterministic
  generation, committed PNG canvas and validity, template sections and labels,
  manifest tampering and closure, manifest counts and figure provenance,
  rendered format structure, HTML escaping, the CLI check path, and lexical
  hygiene.
- `test_sidecar.py` — structural checks for the InstituteOS `.aii/` sidecar:
  schema marker and required sections, repository identity and provenance,
  artifact paths and kinds, documentation paths, relations and links, and task
  commands. The authoritative sidecar validator is private; this is the public
  dependency-light check.

The tests load `schemas/source-v2.json`, `schemas/export-v2.json`, and
`schemas/manifest-v2.json` by name. Keep those filenames stable.
