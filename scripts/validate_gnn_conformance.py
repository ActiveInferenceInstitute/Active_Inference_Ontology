#!/usr/bin/env python3
"""Validate the ontology vocabulary bridge against the pinned GNN release.

The repository already treats ``GNN/declared-labels.json`` as reviewed input and
``GNN/act_inf_ontology_terms.json`` as its generated bridge. This check closes
the other half of that contract: it installs the exact GNN revision named by
``.github/gnn-pin.json`` (``--install``, the gate arm does this), verifies the GNN
vocabulary bytes that the reviewed input records, and compares the pinned
parser's term set with the bridge's declared labels.

Pin normalization belongs to ``gnn.importers.read_pin``; the gate separately
calls ``python -m gnn.importers check`` for pin, pointer, and specification
validation. Only the raw repository/revision bootstrap read precedes installation;
it performs no normalization or validation and uses no second pin.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from importlib import resources
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PIN_PATH = ROOT / ".github" / "gnn-pin.json"
DECLARED_PATH = ROOT / "GNN" / "declared-labels.json"
BRIDGE_PATH = ROOT / "GNN" / "act_inf_ontology_terms.json"
BRIDGE_SCHEMA = "active-inference-ontology/gnn-terms/v1"


class ConformanceError(SystemExit):
    """Raised when the pinned parser and the ontology bridge disagree."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConformanceError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConformanceError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ConformanceError(f"{path} must contain a JSON object")
    return document


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def install_pin(repository: str, revision: str) -> None:
    """Install the pinned parser revision into the active interpreter."""

    specification = (
        f"generalized-notation-notation @ git+https://github.com/{repository}.git@{revision}"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            specification,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise ConformanceError(
            "installing the pinned GNN parser failed: "
            + (detail[-1] if detail else "unknown error")
        )


def bootstrap_pin(path: Path) -> tuple[str, str]:
    """Extract only the raw install pair before the pinned reader exists."""
    document = json.loads(path.read_text(encoding="utf-8"))
    return document["repository"], document["revision"]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--install",
        action="store_true",
        help="install the parser revision pinned in .github/gnn-pin.json before verifying",
    )
    args = parser.parse_args(argv)
    if args.install:
        install_pin(*bootstrap_pin(PIN_PATH))

    from gnn.importers import read_pin

    pin = read_pin(PIN_PATH)
    declared = _read_json(DECLARED_PATH)
    bridge = _read_json(BRIDGE_PATH)

    repository = pin.repository
    revision = pin.commit
    tag = pin.tag

    source = declared.get("source")
    if not isinstance(source, dict):
        raise ConformanceError("declared-labels.json is missing source provenance")
    if source.get("repository") != repository:
        raise ConformanceError("declared-labels repository does not match the GNN pin")
    if source.get("commit") != revision:
        raise ConformanceError("declared-labels commit does not match the GNN pin")
    if source.get("release") != tag:
        raise ConformanceError("declared-labels release does not match the GNN pin")

    labels = declared.get("labels")
    if not isinstance(labels, list) or not labels:
        raise ConformanceError("declared-labels.json carries no labels")
    expected_labels = []
    for index, entry in enumerate(labels, start=1):
        if not isinstance(entry, dict) or not isinstance(entry.get("label"), str):
            raise ConformanceError(f"declared-labels.json labels[{index}] is invalid")
        expected_labels.append(entry["label"])
    if len(expected_labels) != len(set(expected_labels)):
        raise ConformanceError("declared-labels.json contains duplicate labels")

    from gnn.ontology.processor import load_defined_ontology_terms

    import gnn

    expected_version = tag.removeprefix("v")
    if gnn.__version__ != expected_version:
        raise ConformanceError(
            f"installed GNN version {gnn.__version__!r} does not match {tag!r}"
        )

    vocabulary = resources.files("gnn").joinpath("ontology/act_inf_ontology_terms.json")
    vocabulary_bytes = vocabulary.read_bytes()
    actual_digest = _sha256(vocabulary_bytes)
    if actual_digest != source.get("sha256"):
        raise ConformanceError(
            "pinned GNN vocabulary digest does not match declared-labels provenance"
        )

    actual_terms = load_defined_ontology_terms()
    if set(actual_terms) != set(expected_labels):
        missing = sorted(set(expected_labels) - set(actual_terms))
        extra = sorted(set(actual_terms) - set(expected_labels))
        raise ConformanceError(
            f"GNN vocabulary mismatch; missing={missing!r} extra={extra!r}"
        )

    if bridge.get("schema") != BRIDGE_SCHEMA:
        raise ConformanceError(f"bridge schema must be {BRIDGE_SCHEMA}")
    declared_bridge = bridge.get("declared")
    if not isinstance(declared_bridge, dict):
        raise ConformanceError("bridge is missing the declared mapping")
    if set(declared_bridge) != set(expected_labels):
        raise ConformanceError("bridge declared labels do not match the GNN pin")

    resolved = 0
    for label in expected_labels:
        entry = declared_bridge[label]
        if not isinstance(entry, dict):
            raise ConformanceError(f"bridge entry for {label!r} is not an object")
        status = entry.get("status")
        identifier = entry.get("id")
        if status == "resolved":
            if not isinstance(identifier, str) or not identifier.startswith("term-"):
                raise ConformanceError(
                    f"resolved bridge label {label!r} lacks a term identifier"
                )
            resolved += 1
        elif status == "unresolved":
            if identifier is not None:
                raise ConformanceError(
                    f"unresolved bridge label {label!r} carries an identifier"
                )
        else:
            raise ConformanceError(
                f"bridge label {label!r} has unknown status {status!r}"
            )

    print(
        json.dumps(
            {
                "gnn-version": gnn.__version__,
                "pin-revision": revision,
                "vocabulary-sha256": actual_digest,
                "declared-labels": len(expected_labels),
                "resolved": resolved,
                "unresolved": len(expected_labels) - resolved,
                "bridge": "verified",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
