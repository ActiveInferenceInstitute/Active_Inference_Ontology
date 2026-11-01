"""Structural checks for the InstituteOS `.aii/` sidecar.

The authoritative validator (`aii_platform.aii_sidecar`) ships in a private kernel
package and is therefore not part of the public workflow. This dependency-light check
keeps the sidecar's documented invariants covered in the public regression suite: the
schema marker, the required sections, artifact and documentation paths that exist, and
`owner/repo` relation targets.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SIDECAR = ROOT / ".aii"
FRAGMENTS = (
    "config.yaml",
    "config.d/ecosystem.yaml",
    "config.d/artifacts.yaml",
    "config.d/tasks.yaml",
)
ARTIFACT_KINDS = {"source", "dataset", "export", "code", "doc", "model"}
RELATION_TARGET = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL = re.compile(r"^https?://")


def deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_sidecar() -> dict[str, Any]:
    config: dict[str, Any] = {}
    for name in FRAGMENTS:
        path = SIDECAR / name
        if path.is_file():
            config = deep_merge(config, yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    return config


class SidecarStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_sidecar()

    def test_schema_marker_and_required_sections(self) -> None:
        self.assertEqual(self.config.get("schema"), "aii-sidecar/v1")
        for section in (
            "meta",
            "repo",
            "institute",
            "provenance",
            "instituteos",
            "capabilities",
            "artifacts",
            "tasks",
            "ecosystem",
            "integration",
            "docs",
        ):
            self.assertIn(section, self.config, f"sidecar section missing: {section}")
        meta = self.config["meta"]
        self.assertRegex(str(meta["sidecar_version"]), VERSION)
        self.assertRegex(str(meta["updated"]), DATE)

    def test_repository_identity_and_provenance_are_complete(self) -> None:
        repo = self.config["repo"]
        for field in ("name", "slug", "full_name", "description", "default_branch", "homepage"):
            self.assertTrue(repo.get(field), f"repo field missing: {field}")
        self.assertRegex(repo["full_name"], RELATION_TARGET)
        provenance = self.config["provenance"]
        self.assertTrue(provenance.get("license"))
        self.assertTrue(provenance.get("current_release"))
        self.assertIn("citation", provenance)
        self.assertTrue(
            any(provenance["citation"].get(field) for field in ("doi", "zenodo", "text")),
            "citation needs at least one of doi, zenodo, text",
        )
        manifest = ROOT / str(provenance["releases_manifest"])
        self.assertTrue(manifest.is_file(), f"release manifest missing: {manifest}")

    def test_artifact_paths_exist_and_kinds_are_declared(self) -> None:
        artifacts = self.config["artifacts"]
        self.assertIsInstance(artifacts, list)
        self.assertTrue(artifacts)
        for item in artifacts:
            self.assertIn(item["kind"], ARTIFACT_KINDS)
            self.assertTrue(item.get("description"), f"artifact needs a description: {item}")
            path = ROOT / str(item["path"])
            self.assertTrue(path.exists(), f"artifact path missing: {item['path']}")

    def test_documentation_paths_live_under_the_sidecar(self) -> None:
        for name in self.config["docs"]:
            self.assertTrue((SIDECAR / str(name)).is_file(), f"sidecar documentation missing: {name}")

    def test_relations_and_links_are_well_formed(self) -> None:
        ecosystem = self.config["ecosystem"]
        for relation in ecosystem["relations"]:
            self.assertRegex(relation["repo"], RELATION_TARGET)
            self.assertTrue(relation.get("relation"), f"relation needs a type: {relation}")
        for name, target in ecosystem["links"].items():
            if URL.match(str(target)):
                continue
            self.assertTrue((ROOT / str(target)).is_file(), f"sidecar link does not resolve: {name}")

    def test_tasks_declare_run_commands(self) -> None:
        tasks = self.config["tasks"]
        self.assertTrue(tasks)
        for name, task in tasks.items():
            self.assertTrue(task.get("cmd"), f"task needs a command: {name}")
            self.assertTrue(task.get("description"), f"task needs a description: {name}")


if __name__ == "__main__":
    unittest.main()
