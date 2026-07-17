from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("manuscript_cli", ROOT / "scripts" / "manuscript.py")
assert SPEC and SPEC.loader
manuscript = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manuscript)


class ManuscriptPipelineTests(unittest.TestCase):
    def test_generated_variables_preserve_release_counts(self) -> None:
        variables = json.loads(manuscript.VARIABLES_PATH.read_text(encoding="utf-8"))
        self.assertEqual(variables["TERM_COUNT"], 429)
        self.assertEqual(variables["RELATION_COUNT"], 238)
        self.assertEqual(variables["TAG_COUNT"], 8)
        self.assertEqual(variables["lists"], {"Core": 64, "Entailed": 73, "Supplement": 292})

    def test_generation_is_current_and_figures_are_deterministic(self) -> None:
        self.assertEqual(manuscript.generate(check=True), [])
        _, _, _, _, report = manuscript.ontology_state(strict=True)
        values = manuscript.flatten_variables(
            manuscript.ontology_state(strict=True)[1],
            manuscript.ontology_state(strict=True)[2],
            manuscript.ontology_state(strict=True)[3],
            report,
        )
        self.assertEqual(manuscript.figure_bytes("metadata_completeness", values), manuscript.figure_bytes("metadata_completeness", values))

    def test_template_sections_and_labels_are_valid(self) -> None:
        self.assertEqual(manuscript.validate_document_structure(), [])
        self.assertEqual(manuscript.validate_references_and_labels(), [])
        self.assertEqual(manuscript.validate_claim_ledger(), [])

    def test_manifest_tampering_is_detected_without_repo_write(self) -> None:
        manifest = json.loads(manuscript.MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest["artifacts"][0]["sha256"] = "0" * 64
        errors = manuscript.validate_manifest_document(manifest, require_rendered=True)
        self.assertTrue(any("manifest hash mismatch" in error for error in errors))

    def test_rendered_formats_are_nonempty_and_well_formed(self) -> None:
        pdf = manuscript.OUTPUT / "pdf" / "active_inference_ontology.pdf"
        html = manuscript.OUTPUT / "html" / "active_inference_ontology.html"
        docx = manuscript.OUTPUT / "docx" / "active_inference_ontology.docx"
        epub = manuscript.OUTPUT / "epub" / "active_inference_ontology.epub"
        self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
        self.assertIn("The Active Inference Ontology", html.read_text(encoding="utf-8"))
        self.assertEqual(docx.read_bytes()[:2], b"PK")
        self.assertEqual(epub.read_bytes()[:2], b"PK")
        self.assertGreater(pdf.stat().st_size, 1000)

    def test_html_payload_escaping_is_preserved(self) -> None:
        ontology_spec = importlib.util.spec_from_file_location("ontology_cli_for_manuscript", ROOT / "scripts" / "ontology.py")
        assert ontology_spec and ontology_spec.loader
        ontology = importlib.util.module_from_spec(ontology_spec)
        ontology_spec.loader.exec_module(ontology)
        export = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))
        export["terms"][0]["term"] = "<script>alert('x')</script>"
        site = ontology.site_text(export)
        self.assertIn("<\\/script>", site)
        self.assertIn("function esc", site)

    def test_cli_check_path_is_executable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "manuscript.py"), "check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_active_lexical_hygiene_is_clean(self) -> None:
        self.assertEqual(manuscript.lexical_hygiene(), [])


if __name__ == "__main__":
    unittest.main()
