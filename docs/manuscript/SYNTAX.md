# Manuscript Syntax

The manuscript follows the template project conventions.

- Main sections are ordered Markdown H1 headings and carry `{#sec:name}` labels.
- Displayed equations use Pandoc-crossref labels such as `{#eq:ontology-model}` and references such as `[@eq:ontology-model]`.
- Figures use Pandoc-crossref image labels and a generated registry at `output/figures/figure_registry.json`.
- Tables use a caption line with `{#tbl:name}`.
- Citations use `[@key]` and resolve against `references.bib`.
- Source variables use `{{UPPER_SNAKE_CASE}}` and are resolved only into `output/manuscript/`.

The renderer validates labels, references, image paths, citations, section order, and generated hashes before a release is accepted.
