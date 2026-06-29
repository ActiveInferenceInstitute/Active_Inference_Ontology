#!/usr/bin/env python3
"""Build a machine-readable JSON export of the Active Inference Ontology.

Reads the latest ``Ontology_v*.csv`` in the repository root and writes
``ontology.json`` next to it. The export carries one record per term plus a
derived concept graph (nodes typed by tag; term-to-term edges parsed from each
term's ``Connections`` field), so downstream tools can consume the ontology
without parsing the multi-line CSV.

Usage:
    python3 scripts/build_json.py
    python3 scripts/build_json.py --check
    python3 scripts/build_json.py --lint
    python3 scripts/build_json.py --report
"""

from __future__ import annotations

import argparse
import csv
import difflib
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ontology.json")
REQUIRED_COLUMNS = [
    "List",
    "Tag",
    "Term",
    "Proposed Definition 1",
    "Proposed Definition 2",
    "Correct Examples",
    "Incorrect Examples",
    "Connections",
]
EXPECTED_TAGS = {
    "Action",
    "Agents in the Niche",
    "Bayesian Statistics",
    "Free Energy",
    "Information",
    "Markov Partitioning",
    "Perception",
    "Systems",
}


def latest_csv() -> str:
    candidates = sorted(glob.glob(os.path.join(ROOT, "Ontology_v*.csv")))
    if not candidates:
        raise SystemExit("No Ontology_v*.csv found in repository root.")
    return candidates[-1]


def norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_rows(csv_path: str) -> tuple[list[str], list[tuple[int, dict[str, str]]]]:
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = [(index, row) for index, row in enumerate(reader, start=2)]
    return fieldnames, rows


def lint_csv(csv_path: str) -> dict:
    fieldnames, rows = read_rows(csv_path)
    errors: list[str] = []
    warnings: list[str] = []

    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    extra = [column for column in fieldnames if column not in REQUIRED_COLUMNS]
    if missing:
        errors.append("missing required CSV columns: " + ", ".join(missing))
    if extra:
        warnings.append("unexpected CSV columns: " + ", ".join(extra))

    seen_terms: dict[str, tuple[int, str]] = {}
    for line_number, row in rows:
        if None in row:
            errors.append(f"row {line_number}: extra unheaded columns are present")

        term = norm(row.get("Term"))
        if not term:
            errors.append(f"row {line_number}: empty Term")
            continue

        term_key = term.lower()
        if term_key in seen_terms:
            first_line, first_term = seen_terms[term_key]
            errors.append(
                f"row {line_number}: duplicate Term {term!r}; first seen "
                f"as {first_term!r} on row {first_line}"
            )
        else:
            seen_terms[term_key] = (line_number, term)

        tag = norm(row.get("Tag"))
        if tag and tag not in EXPECTED_TAGS:
            warnings.append(f"row {line_number}: unexpected Tag {tag!r}")

    return {
        "source": os.path.basename(csv_path),
        "rowCount": len(rows),
        "columnCount": len(fieldnames),
        "errors": errors,
        "warnings": warnings,
    }


def refs(text: str, self_term: str, by_lower: dict[str, dict]) -> set[str]:
    low = (text or "").lower()
    out: set[str] = set()
    for lower_name, obj in by_lower.items():
        if obj["term"] == self_term:
            continue
        if re.search(r"(?<![a-z])" + re.escape(lower_name) + r"(?![a-z])", low):
            out.add(obj["term"])
    return out


def build(csv_path: str) -> dict:
    _, rows = read_rows(csv_path)

    terms: list[dict] = []
    seen: set[str] = set()
    for _, row in rows:
        term = norm(row.get("Term"))
        if not term or term.lower() in seen:
            continue
        seen.add(term.lower())
        terms.append(
            {
                "id": "term-" + slugify(term),
                "term": term,
                "tag": norm(row.get("Tag")),
                "list": norm(row.get("List")),
                "definition": norm(row.get("Proposed Definition 1")),
                "definition2": norm(row.get("Proposed Definition 2")),
                "examples": norm(row.get("Correct Examples")),
                "counterExamples": norm(row.get("Incorrect Examples")),
                "connections": norm(row.get("Connections")),
            }
        )

    by_lower = {t["term"].lower(): t for t in terms}
    id_of = {t["term"]: t["id"] for t in terms}

    edges = set()
    for t in terms:
        for ref in refs(t["connections"], t["term"], by_lower):
            edges.add((t["term"], ref))

    nodes = [
        {
            "id": t["id"],
            "label": t["term"],
            "type": t["tag"] or "Other",
            "meta": (t["definition"][:160] + ("…" if len(t["definition"]) > 160 else ""))
            if t["definition"]
            else t["tag"],
        }
        for t in terms
    ]
    edge_list = [
        {"source": id_of[a], "target": id_of[b], "relation": "connects"}
        for a, b in sorted(edges)
    ]
    tags = sorted({t["tag"] for t in terms if t["tag"]})

    return {
        "description": "Machine-readable export of the Active Inference Ontology.",
        "source": os.path.basename(csv_path),
        "termCount": len(terms),
        "tagCount": len(tags),
        "edgeCount": len(edge_list),
        "tags": tags,
        "terms": terms,
        "graph": {"nodes": nodes, "edges": edge_list},
    }


def serialize(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def suggest_terms(text: str, self_term: str, term_names: list[str]) -> list[str]:
    normalized = norm(re.sub(r"[^A-Za-z0-9]+", " ", text)).lower()
    lookup = {term.lower(): term for term in term_names if term != self_term}
    suggestions: set[str] = set()

    for match in difflib.get_close_matches(normalized, list(lookup), n=5, cutoff=0.48):
        suggestions.add(lookup[match])

    words = normalized.split()
    for size in range(2, min(6, len(words)) + 1):
        for index in range(0, len(words) - size + 1):
            phrase = " ".join(words[index : index + size])
            for match in difflib.get_close_matches(phrase, list(lookup), n=2, cutoff=0.84):
                suggestions.add(lookup[match])

    return sorted(suggestions)[:5]


def validation_report(csv_path: str) -> dict:
    data = build(csv_path)
    terms = data["terms"]
    by_lower = {t["term"].lower(): t for t in terms}
    term_names = [t["term"] for t in terms]
    unresolved = []

    for term in terms:
        connections = term["connections"]
        if not connections or refs(connections, term["term"], by_lower):
            continue
        unresolved.append(
            {
                "term": term["term"],
                "connections": connections[:240],
                "suggestions": suggest_terms(connections, term["term"], term_names),
            }
        )

    return {
        "source": data["source"],
        "termCount": data["termCount"],
        "tagCount": data["tagCount"],
        "edgeCount": data["edgeCount"],
        "lint": lint_csv(csv_path),
        "unresolvedConnectionRowCount": len(unresolved),
        "unresolvedConnectionRows": unresolved,
    }


def print_lint(result: dict) -> None:
    status = "passed" if not result["errors"] else "failed"
    print(
        f"CSV lint {status}: {result['rowCount']} rows, "
        f"{result['columnCount']} columns, {len(result['errors'])} errors, "
        f"{len(result['warnings'])} warnings."
    )
    for error in result["errors"]:
        print(f"error: {error}", file=sys.stderr)
    for warning in result["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)


def lint_exit_code(result: dict, *, strict: bool = False) -> int:
    if result["errors"] or (strict and result["warnings"]):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify ontology.json is current")
    parser.add_argument("--lint", action="store_true", help="validate CSV headers and term identities")
    parser.add_argument("--strict", action="store_true", help="make lint warnings fail")
    parser.add_argument("--report", action="store_true", help="print a JSON validation report")
    args = parser.parse_args()

    csv_path = latest_csv()

    if args.report:
        report = validation_report(csv_path)
        print(serialize(report), end="")
        return lint_exit_code(report["lint"], strict=args.strict)

    lint_result = lint_csv(csv_path)
    if args.lint:
        print_lint(lint_result)
        return lint_exit_code(lint_result, strict=args.strict)

    if lint_result["errors"]:
        print_lint(lint_result)
        return 1

    data = build(csv_path)
    rendered = serialize(data)

    if args.check:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != rendered:
            print("ontology.json is stale; run: python3 scripts/build_json.py", file=sys.stderr)
            return 1
        print(f"ontology.json is up to date ({data['termCount']} terms, {data['edgeCount']} edges).")
        return 0

    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    print(f"Wrote {os.path.relpath(OUT, ROOT)}: {data['termCount']} terms, "
          f"{data['tagCount']} tags, {data['edgeCount']} edges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
