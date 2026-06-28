#!/usr/bin/env python3
"""Build a machine-readable JSON export of the Active Inference Ontology.

Reads the latest ``Ontology_v*.csv`` in the repository root and writes
``ontology.json`` next to it. The export carries one record per term plus a
derived concept graph (nodes typed by tag; term-to-term edges parsed from each
term's ``Connections`` field), so downstream tools can consume the ontology
without parsing the multi-line CSV.

Usage:
    python3 scripts/build_json.py            # build ontology.json from the latest CSV
    python3 scripts/build_json.py --check    # verify ontology.json is up to date (exit 1 if stale)
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ontology.json")


def latest_csv() -> str:
    candidates = sorted(glob.glob(os.path.join(ROOT, "Ontology_v*.csv")))
    if not candidates:
        raise SystemExit("No Ontology_v*.csv found in repository root.")
    return candidates[-1]


def norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def build(csv_path: str) -> dict:
    with open(csv_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    terms: list[dict] = []
    seen: set[str] = set()
    for row in rows:
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

    def refs(text: str, self_term: str) -> set[str]:
        low = (text or "").lower()
        out: set[str] = set()
        for lower_name, obj in by_lower.items():
            if obj["term"] == self_term:
                continue
            if re.search(r"(?<![a-z])" + re.escape(lower_name) + r"(?![a-z])", low):
                out.add(obj["term"])
        return out

    edges = set()
    for t in terms:
        for ref in refs(t["connections"], t["term"]):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify ontology.json is current")
    args = parser.parse_args()

    data = build(latest_csv())
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
