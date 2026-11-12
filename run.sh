#!/usr/bin/env bash
# Single gate entry point.
#
# Every arm below runs exactly the command the public workflow runs; the workflow
# calls these arms instead of restating the commands. `docs/build-and-validation.md`
# documents the arms and `docs/_generated/gate.md` records their measured wall time
# (regenerate with `./run.sh bench`).
#
# Interpreter: set PYTHON to override; otherwise `.venv/bin/python` when present,
# then `python3` from PATH.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PROG="$(basename "$0")"

python_bin() {
  if [[ -n "${PYTHON:-}" ]]; then
    printf '%s' "$PYTHON"
  elif [[ -x .venv/bin/python ]]; then
    printf '%s' .venv/bin/python
  else
    command -v python3
  fi
}

usage() {
  cat <<'EOF'
usage: ./run.sh [ARM ...]

With no arm, ./run.sh runs the fast inner-loop selection.

Arms (each runs the same command the public workflow runs):
  deps        install the pinned dependencies in one locked install
  lint        static analysis (ruff, policy in ruff.toml)
  ontology    ontology contract and generated-artifact gates
  fast        regression subset without the publication layer (inner loop)
  full        complete regression suite
  docs        documentation links, anchors, and index coverage
  manuscript  manuscript freshness: generate, byte-identity, validate, check
  render      render PDF/HTML/DOCX/EPUB (needs Pandoc, pandoc-crossref, XeLaTeX, qpdf)
  gnn         pinned GNN parser conformance (installs the pin; needs network)
  bench       measure every arm and regenerate docs/_generated/gate.md
  all         every arm the public workflow runs (lint ontology full docs manuscript gnn)

Examples:
  ./run.sh deps
  ./run.sh fast
  MANUSCRIPT_PORTABLE_CHECK=1 ./run.sh manuscript
EOF
}

arm_deps() {
  "$PY" -m pip install --disable-pip-version-check --requirement requirements-manuscript.txt
}

arm_lint() {
  "$PY" -m ruff check --no-cache scripts tests
}

arm_ontology() {
  "$PY" scripts/ontology.py validate --strict
  "$PY" scripts/ontology.py schema-check
  "$PY" scripts/ontology.py build --check
  "$PY" scripts/ontology.py export-csv --check
  "$PY" scripts/ontology.py site --check
  "$PY" scripts/ontology.py report > /dev/null
  "$PY" scripts/ontology.py diff ontology.source.json ontology.source.json > /dev/null
}

arm_fast() {
  "$PY" -m unittest tests.test_ontology tests.test_sidecar -v
}

arm_full() {
  "$PY" -m unittest discover -s tests -v
}

arm_docs() {
  "$PY" scripts/check_docs.py
  "$PY" scripts/report_gate.py --check
}

arm_manuscript() {
  "$PY" scripts/manuscript.py generate
  "$PY" scripts/manuscript.py manifest
  # Byte-identity for every non-rasterized artifact the generator owns; figure
  # bytes are host-dependent and the manifest hashes those figures.
  git diff --exit-code -- \
    docs/manuscript/data/manuscript_variables.json \
    docs/manuscript/output/manuscript \
    docs/manuscript/output/figures/figure_registry.json
  "$PY" scripts/manuscript.py validate --strict
  "$PY" scripts/manuscript.py check
  git diff --check
}

arm_render() {
  "$PY" scripts/manuscript.py render --format all
  "$PY" scripts/manuscript.py check
}

arm_gnn() {
  "$PY" -m pip install --disable-pip-version-check --requirement requirements-gnn.txt
  "$PY" scripts/validate_gnn_conformance.py --install
  "$PY" scripts/ontology.py gnn-terms --check
}

arm_bench() {
  "$PY" scripts/report_gate.py "$@"
}

arm_all() {
  arm_lint
  arm_ontology
  arm_manuscript
  arm_full
  arm_docs
  arm_gnn
}

PY="$(python_bin)"

ARMS=(deps lint ontology manuscript full docs fast gnn render bench all)

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" || "${1:-}" == "--list" ]]; then
  usage
  exit 0
fi

if [[ $# -eq 0 ]]; then
  printf '%s: no arm named; running the fast inner-loop arm (./run.sh --help lists all arms)\n' "$PROG"
  set -- fast
fi

if [[ "${1:-}" == "--arms" ]]; then
  printf '%s\n' "${ARMS[@]}"
  exit 0
fi

unknown=()
for raw in "$@"; do
  name="${raw%%=*}"
  found=0
  for known in "${ARMS[@]}"; do
    [[ "$name" == "$known" ]] && found=1 && break
  done
  [[ $found -eq 1 ]] || unknown+=("$raw")
done
if [[ ${#unknown[@]} -gt 0 ]]; then
  printf '%s: unknown arm(s): %s\n\n' "$PROG" "${unknown[*]}" >&2
  usage >&2
  exit 2
fi

for arm in "$@"; do
  printf '\n==> ./run.sh %s\n' "$arm"
  "arm_${arm%%=*}"
done
