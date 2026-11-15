from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("documentation_checker", ROOT / "scripts/check_docs.py")
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class DocumentationCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        original_root, original_index = checker.ROOT, checker.INDEX
        self.addCleanup(setattr, checker, "ROOT", original_root)
        self.addCleanup(setattr, checker, "INDEX", original_index)
        checker.ROOT = self.root
        checker.INDEX = self.root / "docs/documentation-index.md"

    def document(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_hidden_authored_documents_are_checked_without_dependency_traversal(self) -> None:
        self.document(".aii/docs/guide.md", "[missing](absent.md)\n")
        self.document(".github/guide.md", "[missing](absent.md)\n")
        self.document("README.md", "# Read me\n")
        for directory in (".venv", "venv", "node_modules", "build", "Archived versions"):
            self.document(directory + "/ignored.md", "[broken](absent.md)\n")
        documents = checker.markdown_files()
        self.assertEqual(
            {p.relative_to(self.root).as_posix() for p in documents},
            {"README.md", ".aii/docs/guide.md", ".github/guide.md"},
        )
        problems = [problem for path in documents for problem in checker.check(path, {})]
        self.assertEqual(len(problems), 2)
        self.assertTrue(all("unresolved link target" in problem for problem in problems))

    def test_code_heading_text_and_duplicate_anchors_resolve(self) -> None:
        self.document("target.md", "# `tool_name.py`\n# `tool_name.py`\n# _Emphasis_\n")
        source = self.document(
            "README.md",
            "[one](target.md#tool_namepy)\n[two](target.md#tool_namepy-1)\n"
            "[three](target.md#emphasis)\n",
        )
        self.assertEqual(checker.check(source, {}), [])
        self.assertEqual(
            checker.anchors(self.root / "target.md"),
            {"tool_namepy", "tool_namepy-1", "emphasis"},
        )

    def test_fence_delimiters_and_inline_links_do_not_create_false_links(self) -> None:
        source = self.document(
            "README.md",
            "# Actual\n````python\n# Hidden\n```\n[hidden](absent.md)\n````\n"
            "`[inline](absent.md)`\n`{#invented}`\n`<a id=\"invented-html\">`\n"
            "~~~\n# Also hidden\n~~~\n",
        )
        self.assertEqual(checker.check(source, {}), [])
        self.assertEqual(checker.anchors(source), {"actual"})

    def test_explicit_anchors_resolve_but_inline_examples_do_not(self) -> None:
        self.document(
            "target.md",
            "# Actual {#declared}\n<a id=\"live\"></a>\n"
            "`{#invented}`\n`<a id=\"invented-html\">`\n",
        )
        valid = self.document(
            "valid.md", "[declared](target.md#declared)\n[html](target.md#live)\n",
        )
        invalid = self.document(
            "invalid.md", "[literal](target.md#invented)\n[html literal](target.md#invented-html)\n",
        )
        self.assertEqual(checker.check(valid, {}), [])
        self.assertEqual(len(checker.check(invalid, {})), 2)

    def test_exact_case_is_checked_before_filesystem_resolution(self) -> None:
        self.document("docs/Target.md", "# Target\n")
        wrong = self.document("README.md", "[wrong](docs/target.md#target)\n")
        errors = checker.check(wrong, {})
        self.assertEqual(len(errors), 1)
        self.assertIn("unresolved link target", errors[0])
        right = self.document("README.md", "[right](docs/Target.md#target)\n")
        self.assertEqual(checker.check(right, {}), [])


if __name__ == "__main__":
    unittest.main()
