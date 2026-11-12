#!/usr/bin/env python3
"""Measure the gate arms and regenerate ``docs/_generated/gate.md``.

The generated page is the only place that records measured gate numbers (arm wall
time, regression-test count, documentation link count, source term count). Run
``./run.sh bench`` after changing an arm; ``--check`` fails when the recorded arm
list or the cheap-to-recompute counts no longer match the repository, so the page
cannot drift.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "_generated" / "gate.md"
SCHEMA = "active-inference-ontology/gate-report/v1"
MARKER = "<!-- gate-report"

# Measured by `bench`. Composite/manual arms are excluded and documented below.
EXCLUDED = {
    "bench": "measures the other arms; measuring itself is meaningless",
    "all": "composite of the arms it lists",
    "render": "needs the Pandoc/XeLaTeX/qpdf toolchain and rewrites publication bytes",
}

DESCRIPTIONS = {
    "deps": "one locked install of `requirements-manuscript.txt` (warm re-run)",
    "lint": "`ruff check`, policy in `ruff.toml`",
    "ontology": "`validate --strict`, `schema-check`, `build`, `export-csv`, `site` checks, `report`, `diff`",
    "fast": "regression subset without the publication layer (`test_ontology`, `test_sidecar`)",
    "full": "`python -m unittest discover -s tests -v`",
    "docs": "`scripts/check_docs.py`: relative links, anchors, index coverage",
    "manuscript": "`generate`, `manifest`, byte-identity diff, `validate --strict`, `check`",
    "gnn": "pinned GNN parser install plus `validate_gnn_conformance.py` and `gnn-terms --check`",
}

# An arm that installs something is measured against a cold installation, so the
# recorded number includes the acquisition the arm performs.
def prepare(name: str) -> list[list[str]]:
    if name == "gnn":
        return [
            [
                python_bin(),
                "-m",
                "pip",
                "uninstall",
                "-y",
                "--quiet",
                "generalized-notation-notation",
            ]
        ]
    return []


JOBS = {
    "lint": "gate",
    "ontology": "gate",
    "full": "gate",
    "docs": "gate",
    "manuscript": "gate",
    "gnn": "gnn-conformance",
}

# `python -m unittest` has no list-only mode, so discovery runs in a child
# interpreter that imports the modules and counts cases without executing one.
DISCOVERY = """
import unittest

suite = unittest.TestLoader().discover("tests")


def walk(test):
    for item in test:
        if isinstance(item, unittest.TestSuite):
            yield from walk(item)
        else:
            yield item


print(sum(1 for _ in walk(suite)))
"""


def arms() -> list[str]:
    result = subprocess.run(
        ["./run.sh", "--arms"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def python_bin() -> str:
    if os.environ.get("PYTHON"):
        return os.environ["PYTHON"]
    candidate = ROOT / ".venv" / "bin" / "python"
    return str(candidate) if candidate.is_file() else sys.executable


def counts() -> dict[str, int]:
    python = python_bin()
    discovery = subprocess.run(
        [python, "-c", DISCOVERY],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    tests = int(discovery.stdout.strip() or 0)
    source = json.loads((ROOT / "ontology.source.json").read_text(encoding="utf-8"))
    return {
        "regression_tests": tests,
        "terms": len(source["terms"]),
    }


def measure(name: str) -> dict[str, Any]:
    for command in prepare(name):
        subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    started = time.monotonic()
    result = subprocess.run(["./run.sh", name], cwd=ROOT, capture_output=True, text=True)
    elapsed = time.monotonic() - started
    status = "pass" if result.returncode == 0 else f"fail ({result.returncode})"
    if result.returncode:
        tail = (result.stdout + result.stderr).strip().splitlines()[-12:]
        print(f"!! ./run.sh {name} {status}", file=sys.stderr)
        for line in tail:
            print(f"   {line}", file=sys.stderr)
    print(f"{elapsed:8.2f}s  {status:10s} {name}", flush=True)
    return {"arm": name, "wall_seconds": round(elapsed, 2), "status": status}


def render(measured: list[dict[str, Any]], measured_counts: dict[str, int]) -> str:
    generated = datetime.now(UTC).replace(microsecond=0).isoformat()
    payload = {
        "schema": SCHEMA,
        "generated": generated,
        "host": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "measured_arms": [entry["arm"] for entry in measured],
        "excluded_arms": EXCLUDED,
        "arms": measured,
        "counts": measured_counts,
    }
    lines = [
        "# Gate arms — measured",
        "",
        MARKER,
        json.dumps(payload, indent=2, sort_keys=True),
        "-->",
        "",
        "Generated by `./run.sh bench` (`scripts/report_gate.py`). Do not hand-edit: the",
        "metadata block above and the tables below are written by that script, and",
        "`./run.sh docs` fails when the recorded arm list or counts drift from the",
        "repository.",
        "",
        f"- Measured: {generated}",
        f"- Host: {payload['host']['system']} {payload['host']['machine']}, "
        f"Python {payload['host']['python']}",
        "",
        "## Arms",
        "",
        "| Arm | Public job | Wall time (s) | Result | Runs |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for entry in measured:
        name = entry["arm"]
        lines.append(
            f"| `{name}` | {JOBS.get(name, 'local')} | {entry['wall_seconds']:.2f} | "
            f"{entry['status']} | {DESCRIPTIONS.get(name, '')} |"
        )
    lines.extend(
        [
            "",
            "Wall time is one run per arm on the host above, including the interpreter",
            "startup of each command in the arm. It is a measurement, not a budget.",
            "`deps` is a warm re-run of a satisfied install; arms that acquire a package",
            "(`gnn`) are measured after that package is removed but keep the host's pip",
            "cache, so a first run on a new machine also pays the download.",
            "",
            "## Counts",
            "",
            "| Measurement | Value | Source |",
            "| --- | ---: | --- |",
            f"| Regression tests | {measured_counts['regression_tests']} | "
            "`unittest` discovery in a child interpreter |",
            f"| Source terms | {measured_counts['terms']} | `ontology.source.json` |",
            "",
            "## Not measured here",
            "",
        ]
    )
    for name in sorted(EXCLUDED):
        lines.append(f"- `{name}` — {EXCLUDED[name]}")
    lines.append("")
    return "\n".join(lines)


def check() -> int:
    if not DOC.is_file():
        print(f"missing generated gate report: {DOC.relative_to(ROOT)}; run ./run.sh bench")
        return 1
    text = DOC.read_text(encoding="utf-8")
    start = text.find(MARKER)
    end = text.find("-->", start)
    if start < 0 or end < 0:
        print(f"{DOC.relative_to(ROOT)} is missing its generated metadata block")
        return 1
    try:
        payload = json.loads(text[start + len(MARKER) : end])
    except json.JSONDecodeError as exc:
        print(f"{DOC.relative_to(ROOT)} metadata block is not valid JSON: {exc}")
        return 1
    problems = []
    if payload.get("schema") != SCHEMA:
        problems.append(f"unexpected schema {payload.get('schema')!r}, expected {SCHEMA!r}")
    known = set(arms())
    measured = set(payload.get("measured_arms") or [])
    excluded = set(payload.get("excluded_arms") or {})
    unlisted = known - measured - excluded
    stale = (measured | excluded) - known
    if unlisted:
        problems.append(f"arms missing from the report: {sorted(unlisted)}")
    if stale:
        problems.append(f"reported arms no longer exist: {sorted(stale)}")
    current = counts()
    recorded = payload.get("counts") or {}
    for key, value in current.items():
        if recorded.get(key) != value:
            problems.append(f"recorded {key}={recorded.get(key)!r} but measured {value!r}")
    for problem in problems:
        print(f"ERROR {problem}")
    if problems:
        print("regenerate with ./run.sh bench")
        return 1
    print(
        f"gate report current: {len(measured)} measured arms, "
        f"{current['regression_tests']} tests, {current['terms']} terms"
    )
    return 0


def main() -> int:
    if "--check" in sys.argv[1:]:
        return check()
    measured = [measure(name) for name in arms() if name not in EXCLUDED]
    measured_counts = counts()
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(render(measured, measured_counts), encoding="utf-8")
    print(f"wrote {DOC.relative_to(ROOT)}")
    return 0 if all(entry["status"] == "pass" for entry in measured) else 1


if __name__ == "__main__":
    sys.exit(main())
