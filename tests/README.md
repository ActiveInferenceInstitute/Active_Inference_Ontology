# Regression tests

Run the suite through the gate arms (from the repository root):

```bash
./run.sh deps   # one locked install
./run.sh fast   # tests/test_ontology.py and tests/test_sidecar.py
./run.sh full   # python3 -m unittest discover -s tests -v
```

`fast` is the inner-loop selection: the source, export, manifest, and sidecar
contracts, with no figure rasterization or rendering. `full` is what the public
workflow runs. [`../.github/workflows/ontology.yml`](../.github/workflows/ontology.yml)
calls the same arms, so a local run and a hosted run execute the same command.

Fixtures that need a repository copy use `copy_repository()` in
`test_ontology.py`, which copies repository content only: VCS state (`.git`),
local virtual environments, and interpreter caches are excluded, so the fixtures do
not depend on a host's Git configuration or in-tree `.venv`.

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
  hygiene (which skips local environments and caches).
- `test_sidecar.py` — structural checks for the InstituteOS `.aii/` sidecar:
  schema marker and required sections, repository identity and provenance,
  artifact paths and kinds, documentation paths, relations and links, and task
  commands. The authoritative sidecar validator is private; this is the public
  dependency-light check.

The tests load `schemas/source-v2.json`, `schemas/export-v2.json`, and
`schemas/manifest-v2.json` by name. Keep those filenames stable.
