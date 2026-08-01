from __future__ import annotations

import contextlib
import csv
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ontology_cli", ROOT / "scripts/ontology.py")
assert SPEC and SPEC.loader
ontology = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ontology)


class OntologyPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = ontology.load_config()
        cls.paths = ontology.configured_paths(cls.config)
        cls.source = ontology.read_json(cls.paths["source"])
        cls.export = ontology.read_json(cls.paths["export"])

    def test_current_migration_preserves_release_shape(self) -> None:
        self.assertEqual(len(self.source["terms"]), 429)
        self.assertEqual(len(self.export["terms"]), 429)
        self.assertEqual(self.export["counts"], {"terms": 429, "tags": 8, "edges": 238})
        self.assertEqual(sum(len(term["relations"]) for term in self.source["terms"]), 238)
        self.assertEqual(ontology.validate_source(self.source, self.config), [])

    def test_generated_artifacts_are_current(self) -> None:
        source, _, errors = ontology.load_and_validate(self.config)
        self.assertEqual(len(source["terms"]), 429)
        self.assertEqual(errors, [])
        self.assertTrue(ontology.write_atomic(self.paths["export"], ontology.canonical_json(self.export), check=True))
        self.assertTrue(ontology.write_atomic(self.paths["csv_export"], ontology.csv_text(self.source), check=True))
        self.assertTrue(ontology.write_atomic(self.paths["site"], ontology.site_text(self.export), check=True))

    def test_json_schema_contracts_validate_live_documents(self) -> None:
        manifest = ontology.read_json(self.paths["manifest"])
        self.assertEqual(
            ontology.validate_json_schemas(self.source, self.export, manifest, self.paths), []
        )

    def test_json_schema_rejects_unmodeled_export_fields(self) -> None:
        export = json.loads(json.dumps(self.export))
        export["unexpected"] = True
        manifest = ontology.read_json(self.paths["manifest"])
        errors = ontology.validate_json_schemas(self.source, export, manifest, self.paths)
        self.assertTrue(any("export schema violation" in error for error in errors))

    def test_stable_id_survives_label_rename(self) -> None:
        source = json.loads(json.dumps(self.source))
        term = source["terms"][0]
        term["term"] = "Renamed publication label"
        self.assertEqual(ontology.validate_source(source, self.config), [])

    def test_core_completeness_and_allowed_historical_gaps(self) -> None:
        core = [term for term in self.source["terms"] if term["list"] == "Core"]
        self.assertEqual(len(core), 64)
        self.assertTrue(all(term["tag"] for term in core))
        self.assertTrue(all(term["definitions"]["primary"] for term in core))
        self.assertTrue(all(term["examples"]["correct"] for term in core))
        report = ontology.quality_report(self.source, self.config)
        self.assertEqual(report["missing"]["tag"], 355)
        self.assertEqual(report["missing"]["primaryDefinition"], 339)

    def test_duplicate_ids_labels_aliases_and_relations_fail(self) -> None:
        source = json.loads(json.dumps(self.source))
        source["terms"][0]["id"] = source["terms"][1]["id"]
        source["terms"][1]["aliases"] = [source["terms"][0]["term"]]
        source["terms"][2]["relations"] = [{"target": "term-does-not-exist", "type": "mentions"}]
        errors = ontology.validate_source(source, self.config)
        self.assertTrue(any("id duplicates" in error for error in errors))
        self.assertTrue(any("duplicate label/alias" in error for error in errors))
        self.assertTrue(any("target is unknown" in error for error in errors))

    def test_colliding_generated_ids_are_rejected_during_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "collision.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=ontology.SOURCE_COLUMNS)
                writer.writeheader()
                for label in ("A+B", "A B"):
                    writer.writerow(
                        {
                            "List": "Core",
                            "Tag": "Action",
                            "Term": label,
                            "Proposed Definition 1": "definition",
                            "Proposed Definition 2": "",
                            "Correct Examples": "example",
                            "Incorrect Examples": "",
                            "Connections": "",
                        }
                    )
            with self.assertRaises(ontology.OntologyError):
                ontology.source_from_csv(csv_path, self.config)

    def test_historical_import_rejects_duplicate_labels(self) -> None:
        historical = ROOT / "Archived versions/v4 (12-12-2022 snapshot)" / "Ontology _ Definitions, Examples, Connections view.csv"
        with self.assertRaises(ontology.OntologyError):
            ontology.source_from_csv(
                historical,
                self.config,
                release_override={"version": "v4", "label": "12-12-2022 snapshot", "date": "2022-12-12"},
            )

    def test_self_relation_and_invalid_status_fail(self) -> None:
        source = json.loads(json.dumps(self.source))
        source["terms"][0]["status"] = "not-a-status"
        source["terms"][0]["relations"] = [{"target": source["terms"][0]["id"], "type": "mentions"}]
        errors = ontology.validate_source(source, self.config)
        self.assertTrue(any("status is not allowed" in error for error in errors))
        self.assertTrue(any("cannot target its own term" in error for error in errors))

        source = json.loads(json.dumps(self.source))
        source["terms"][0]["relations"] = [{"target": "term_INVALID_ID", "type": "not-a-relation"}]
        errors = ontology.validate_source(source, self.config)
        self.assertTrue(any("target is invalid" in error for error in errors))
        self.assertTrue(any("type is not allowed" in error for error in errors))

    def test_case_only_label_change_is_reported(self) -> None:
        old = json.loads(json.dumps(self.source))
        new = json.loads(json.dumps(self.source))
        new["terms"][0]["term"] = old["terms"][0]["term"].swapcase()
        with tempfile.TemporaryDirectory() as directory:
            old_path = Path(directory) / "old.json"
            new_path = Path(directory) / "new.json"
            old_path.write_text(ontology.canonical_json(old), encoding="utf-8")
            new_path.write_text(ontology.canonical_json(new), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = ontology.diff_command(old_path, new_path, self.config)
        self.assertEqual(result, 0)
        diff = json.loads(output.getvalue())
        self.assertEqual(diff["renamed"][0]["id"], old["terms"][0]["id"])
        self.assertEqual(diff["caseOnlyRenames"][0]["id"], old["terms"][0]["id"])
        self.assertIn("term", diff["changed"][0]["fields"])

    def test_diff_reports_explicit_change_categories(self) -> None:
        old = json.loads(json.dumps(self.source))
        new = json.loads(json.dumps(self.source))
        term = next(item for item in new["terms"] if item["relations"])
        term["aliases"] = ["Curated alias"]
        term["status"] = "draft"
        term["tag"] = "Information" if term["tag"] != "Information" else "Action"
        term["relations"] = []
        with tempfile.TemporaryDirectory() as directory:
            old_path = Path(directory) / "old.json"
            new_path = Path(directory) / "new.json"
            old_path.write_text(ontology.canonical_json(old), encoding="utf-8")
            new_path.write_text(ontology.canonical_json(new), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = ontology.diff_command(old_path, new_path, self.config)
        self.assertEqual(result, 0)
        diff = json.loads(output.getvalue())
        term_id = term["id"]
        self.assertEqual(diff["aliasChanges"][0]["id"], term_id)
        self.assertEqual(diff["statusChanges"][0]["id"], term_id)
        self.assertEqual(diff["tagChanges"][0]["id"], term_id)
        self.assertEqual(diff["relationChanges"][0]["id"], term_id)

    def test_stale_export_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "repo"
            shutil.copytree(ROOT, copy)
            export_path = copy / "ontology.json"
            export_path.write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/ontology.py"), "validate", "--strict"],
                cwd=copy,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated export is stale", result.stderr)

    def test_malformed_source_root_fails_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "repo"
            shutil.copytree(ROOT, copy)
            (copy / "ontology.source.json").write_text("[]\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/ontology.py"), "validate", "--strict"],
                cwd=copy,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JSON root must be an object", result.stderr)

    def test_manifest_hash_and_numeric_order_failures_are_detected(self) -> None:
        manifest = json.loads(json.dumps(ontology.read_json(self.paths["manifest"])))
        current = next(item for item in manifest["releases"] if item["version"] == "v5")
        current["artifacts"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "releases.json"
            path.write_text(ontology.canonical_json(manifest), encoding="utf-8")
            errors = ontology.validate_manifest(path, self.config)
        self.assertTrue(any("hash mismatch" in error for error in errors))

        manifest = json.loads(json.dumps(ontology.read_json(self.paths["manifest"])))
        manifest["releases"][3], manifest["releases"][4] = manifest["releases"][4], manifest["releases"][3]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "releases.json"
            path.write_text(ontology.canonical_json(manifest), encoding="utf-8")
            errors = ontology.validate_manifest(path, self.config)
        self.assertTrue(any("ordered numerically" in error for error in errors))

        manifest = json.loads(json.dumps(ontology.read_json(self.paths["manifest"])))
        current = next(item for item in manifest["releases"] if item["version"] == "v5")
        current["path"] = "../outside"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "releases.json"
            path.write_text(ontology.canonical_json(manifest), encoding="utf-8")
            errors = ontology.validate_manifest(path, self.config)
        self.assertTrue(any("must stay within the repository" in error for error in errors))

    def test_manifest_symlink_escape_is_rejected(self) -> None:
        original_root = ontology.ROOT
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            outside = Path(directory) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "link").symlink_to(outside, target_is_directory=True)
            ontology.ROOT = root
            try:
                with self.assertRaises(ontology.OntologyError):
                    ontology.safe_relative_path("link", "manifest.path")
            finally:
                ontology.ROOT = original_root

    def test_sync_manifest_is_idempotent_and_preserves_validity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "repo"
            shutil.copytree(ROOT, copy)
            manifest_path = copy / "releases.json"
            before = manifest_path.read_text(encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(copy / "scripts/ontology.py"), "sync-manifest"],
                cwd=copy,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            # sync-manifest must recompute the same hashes (idempotent rewrite).
            after = manifest_path.read_text(encoding="utf-8")
            self.assertEqual(before, after)
            # And the rewritten manifest must still be internally consistent.
            manifest = json.loads(after)
            current = next(item for item in manifest["releases"] if item["version"] == "v5")
            self.assertEqual(current["validationSummary"]["termCount"], 429)

    def test_audit_csv_reports_duplicates_without_importing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "audit.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=ontology.SOURCE_COLUMNS)
                writer.writeheader()
                for label in ("A+B", "A B", "Same", "same"):
                    writer.writerow({
                        "List": "Core",
                        "Tag": "Action",
                        "Term": label,
                        "Proposed Definition 1": "definition",
                        "Proposed Definition 2": "",
                        "Correct Examples": "example",
                        "Incorrect Examples": "",
                        "Connections": "",
                    })
            report = ontology.audit_csv(csv_path)
        self.assertFalse(report["valid"])
        self.assertEqual(len(report["duplicateLabels"]), 1)
        self.assertEqual(len(report["generatedIdCollisions"]), 2)

    def test_external_migration_output_path_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "migrated.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/ontology.py"),
                    "migrate-csv",
                    str(ROOT / "Ontology_v5_May_25_2023.csv"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(output), result.stdout)

    def test_schema_files_and_sidecar_task_are_present(self) -> None:
        source_schema = json.loads((ROOT / "schemas/source-v2.json").read_text(encoding="utf-8"))
        export_schema = json.loads((ROOT / "schemas/export-v2.json").read_text(encoding="utf-8"))
        self.assertEqual(source_schema["$defs"]["term"]["properties"]["id"]["pattern"], ontology.ID_PATTERN.pattern)
        self.assertEqual(export_schema["properties"]["schemaVersion"]["const"], "2.0")
        manifest_schema = json.loads((ROOT / "schemas/manifest-v2.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest_schema["properties"]["schema"]["const"], ontology.MANIFEST_SCHEMA)
        tasks = (ROOT / ".aii/config.d/tasks.yaml").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/ontology.py validate --strict", tasks)
        self.assertIn("python3 scripts/ontology.py schema-check", tasks)

    def test_source_selection_is_explicitly_configured(self) -> None:
        self.assertEqual(self.config["paths"]["source"], "ontology.source.json")
        self.assertNotIn("latest", json.dumps(self.config).lower())

    def test_no_unfinished_active_surface_remains(self) -> None:
        self.assertFalse((ROOT / ("TO" + "DO.md")).exists())
        self.assertNotIn("work " + "in progress", (ROOT / "README.md").read_text(encoding="utf-8").lower())

    def test_generated_site_has_provenance_examples_and_neighborhoods(self) -> None:
        site = (ROOT / "site/index.html").read_text(encoding="utf-8")
        self.assertIn('id="provenance"', site)
        self.assertIn("Correct example", site)
        self.assertIn("Relation neighborhood", site)
        self.assertIn("source.sha256", site)
        payload = re.search(r"const data = (.*);\nconst byId", site, flags=re.S)
        self.assertIsNotNone(payload)
        self.assertEqual(json.loads(payload.group(1))["counts"], self.export["counts"])

    def test_site_payload_escapes_script_terminators(self) -> None:
        export = json.loads(json.dumps(self.export))
        export["terms"][0]["term"] = "</script><img src=x onerror=alert(1)>"
        site = ontology.site_text(export)
        self.assertNotIn("</script><img", site)
        self.assertIn("<\\/script>", site)


if __name__ == "__main__":
    unittest.main()
