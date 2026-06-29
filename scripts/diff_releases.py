from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
from pathlib import Path

COMPARISON_FIELDS = [
    "List",
    "Tag",
    "Proposed Definition 1",
    "Proposed Definition 2",
    "Correct Examples",
    "Incorrect Examples",
    "Connections",
]


def norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def load_terms(path: Path) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = csv.DictReader(handle)
        terms: dict[str, dict] = {}
        for line_number, row in enumerate(rows, start=2):
            term = norm(row.get("Term"))
            if not term:
                continue
            key = term.lower()
            if key in terms:
                continue
            terms[key] = {
                "line": line_number,
                "term": term,
                "fields": {field: norm(row.get(field)) for field in COMPARISON_FIELDS},
            }
    return terms


def changed_fields(old_term: dict, new_term: dict) -> list[str]:
    changed = []
    for field in COMPARISON_FIELDS:
        if old_term["fields"].get(field, "") != new_term["fields"].get(field, ""):
            changed.append(field)
    return changed


def diff_releases(old_path: Path, new_path: Path) -> dict:
    old_terms = load_terms(old_path)
    new_terms = load_terms(new_path)
    old_keys = set(old_terms)
    new_keys = set(new_terms)
    added_keys = sorted(new_keys - old_keys)
    removed_keys = sorted(old_keys - new_keys)
    common_keys = sorted(old_keys & new_keys)

    changed = [
        {
            "term": new_terms[key]["term"],
            "oldLine": old_terms[key]["line"],
            "newLine": new_terms[key]["line"],
            "fields": changed_fields(old_terms[key], new_terms[key]),
        }
        for key in common_keys
        if changed_fields(old_terms[key], new_terms[key])
    ]

    rename_candidates = []
    for removed_key in removed_keys:
        matches = difflib.get_close_matches(removed_key, added_keys, n=3, cutoff=0.72)
        for match in matches:
            rename_candidates.append(
                {
                    "oldTerm": old_terms[removed_key]["term"],
                    "newTerm": new_terms[match]["term"],
                    "oldLine": old_terms[removed_key]["line"],
                    "newLine": new_terms[match]["line"],
                }
            )

    return {
        "oldSource": str(old_path),
        "newSource": str(new_path),
        "oldTermCount": len(old_terms),
        "newTermCount": len(new_terms),
        "addedTermCount": len(added_keys),
        "removedTermCount": len(removed_keys),
        "changedTermCount": len(changed),
        "renameCandidateCount": len(rename_candidates),
        "addedTerms": [new_terms[key]["term"] for key in added_keys],
        "removedTerms": [old_terms[key]["term"] for key in removed_keys],
        "changedTerms": changed,
        "renameCandidates": rename_candidates,
    }


def print_text(report: dict) -> None:
    print(f"Old source: {report['oldSource']}")
    print(f"New source: {report['newSource']}")
    print(f"Old terms: {report['oldTermCount']}")
    print(f"New terms: {report['newTermCount']}")
    print(f"Added terms: {report['addedTermCount']}")
    print(f"Removed terms: {report['removedTermCount']}")
    print(f"Changed terms: {report['changedTermCount']}")
    print(f"Rename candidates: {report['renameCandidateCount']}")

    if report["addedTerms"]:
        print("\nAdded")
        for term in report["addedTerms"][:50]:
            print(f"- {term}")
    if report["removedTerms"]:
        print("\nRemoved")
        for term in report["removedTerms"][:50]:
            print(f"- {term}")
    if report["changedTerms"]:
        print("\nChanged")
        for item in report["changedTerms"][:50]:
            fields = ", ".join(item["fields"])
            print(f"- {item['term']}: {fields}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two ontology CSV releases by term identity and content fields."
    )
    parser.add_argument("old_csv", type=Path)
    parser.add_argument("new_csv", type=Path)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    report = diff_releases(args.old_csv, args.new_csv)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
