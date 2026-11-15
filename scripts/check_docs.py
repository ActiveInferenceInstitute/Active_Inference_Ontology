#!/usr/bin/env python3
"""Check repository documentation: relative links, anchors, and index coverage.

The repository has no third-party documentation linter, so this script is the
documentation gate. It enforces three things that a reviewer cannot cheaply check
by hand:

* every relative link and image target in tracked Markdown resolves, with exact
  filename case so a tree that passes on a case-insensitive host still passes on
  Linux CI;
* every in-repository fragment (``path#anchor``) matches a heading slug or an
  explicit ``{#id}``/``<a id=...>`` anchor in the target file;
* ``docs/documentation-index.md`` lists every long-lived document under ``docs/``.

``Archived versions/`` is immutable historical evidence and is not checked: its
relative links cannot be repaired without rewriting the archive.
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "docs" / "documentation-index.md"
ARCHIVE = "Archived versions"
GENERATED_OUTPUT = ("docs", "manuscript", "output")
SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox",
    "site-packages", "build", "dist",
}

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'))?\s*\)")
DEFINITION = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(\S+)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
EXPLICIT_ID = re.compile(r"\{#([^}\s]+)\}")
HTML_ANCHOR = re.compile(r"<a\s+(?:id|name)=\"([^\"]+)\"")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
SLUG_DROP = re.compile(r"[^\w\- ]", re.UNICODE)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def slugify(heading: str) -> str:
    text = EXPLICIT_ID.sub("", heading)
    text = "".join(
        part[1:-1] if part.startswith("`") and part.endswith("`")
        else re.sub(r"[*_]", "", part)
        for part in re.split(r"(`[^`\n]*`)", text)
    )
    text = normalize(text).strip().casefold()
    return SLUG_DROP.sub("", text).replace(" ", "-")


def markdown_files() -> list[Path]:
    files = []
    for directory, names, filenames in os.walk(ROOT, followlinks=False):
        current = Path(directory)
        names[:] = sorted(
            name for name in names
            if name not in SKIP_DIRS
            and not (current == ROOT and name == ARCHIVE)
            and not (current / name).is_symlink()
        )
        files.extend(current / name for name in sorted(filenames) if name.endswith(".md"))
    return sorted(files)


def strip_code(text: str, *, inline: bool = True) -> str:
    """Blank fenced content; optionally hide code spans when finding links."""

    lines = []
    fence = ""
    for line in text.splitlines():
        match = FENCE.match(line)
        if fence:
            if (
                match and match[1][0] == fence[0]
                and len(match[1]) >= len(fence) and not match[2].strip()
            ):
                fence = ""
            lines.append("")
        elif match:
            fence = match[1]
            lines.append("")
        else:
            lines.append(INLINE_CODE.sub("", line) if inline else line)
    return "\n".join(lines)


def anchors(path: Path) -> set[str]:
    try:
        text = strip_code(path.read_text(encoding="utf-8"), inline=False)
    except (OSError, UnicodeDecodeError):
        return set()
    found = set()
    for line in text.splitlines():
        anchor_text = INLINE_CODE.sub("", line)
        found.update(EXPLICIT_ID.findall(anchor_text))
        found.update(HTML_ANCHOR.findall(anchor_text))
        match = HEADING.match(line)
        if match:
            slug = slugify(match.group(1))
            if slug:
                seen = 1
                candidate = slug
                while candidate in found:
                    candidate = f"{slug}-{seen}"
                    seen += 1
                found.add(candidate)
    return found


def exact_exists(path: Path) -> bool:
    """Resolve a path component by component, comparing names byte for byte."""

    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return path.exists()
    current = ROOT
    for part in relative.parts:
        if part in ("", "."):
            continue
        if part == "..":
            current = current.parent
            continue
        try:
            entries = {normalize(entry.name): entry for entry in current.iterdir()}
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            return False
        entry = entries.get(normalize(part))
        if entry is None:
            return False
        current = entry
    return current.exists()


def targets(text: str) -> list[tuple[int, str]]:
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        for match in LINK.finditer(line):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1].strip()
            found.append((number, target))
        definition = DEFINITION.match(line)
        if definition:
            found.append((number, definition.group(1).strip("<>")))
    return found


def check(path: Path, cache: dict[Path, set[str]]) -> list[str]:
    problems = []
    try:
        text = strip_code(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{path.relative_to(ROOT)}: unreadable: {exc}"]
    for number, target in targets(text):
        if not target or SCHEME.match(target):
            continue
        location = f"{path.relative_to(ROOT)}:{number}"
        if target.startswith("//"):
            continue
        raw_path, _, fragment = target.partition("#")
        raw_path = raw_path.split("?", 1)[0]
        if not raw_path:
            destination = path
        else:
            destination = path.parent / unquote(raw_path)
            if not exact_exists(destination):
                problems.append(f"{location}: unresolved link target {target!r}")
                continue
            destination = destination.resolve()
        if not fragment:
            continue
        if destination.suffix.lower() != ".md":
            continue
        if destination not in cache:
            cache[destination] = anchors(destination)
        if unquote(fragment) not in cache[destination]:
            problems.append(f"{location}: missing anchor #{fragment} in {raw_path!r}")
    return problems


def index_coverage(files: list[Path]) -> list[str]:
    if not INDEX.is_file():
        return ["docs/documentation-index.md is missing"]
    text = strip_code(INDEX.read_text(encoding="utf-8"))
    listed = set()
    for _, target in targets(text):
        if SCHEME.match(target):
            continue
        raw_path = unquote(target.partition("#")[0].split("?", 1)[0])
        if not raw_path:
            continue
        destination = (INDEX.parent / raw_path).resolve()
        try:
            listed.add(destination.relative_to(ROOT).as_posix())
        except ValueError:
            continue
    missing = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if not relative.startswith("docs/"):
            continue
        if relative.startswith("/".join(GENERATED_OUTPUT) + "/"):
            continue
        # The manuscript is an ordered section set indexed by its own hub page.
        if relative.startswith("docs/manuscript/") and relative != "docs/manuscript/README.md":
            continue
        if relative not in listed:
            missing.append(relative)
    return [f"docs/documentation-index.md does not list {item}" for item in sorted(missing)]


def main() -> int:
    as_json = "--json" in sys.argv[1:]
    files = markdown_files()
    cache: dict[Path, set[str]] = {}
    problems: list[str] = []
    for path in files:
        problems.extend(check(path, cache))
    problems.extend(index_coverage(files))
    links = sum(len(targets(strip_code(path.read_text(encoding="utf-8")))) for path in files)
    if as_json:
        print(
            json.dumps(
                {
                    "documents": len(files),
                    "links": links,
                    "problems": problems,
                    "skipped": f"{ARCHIVE}/",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1 if problems else 0
    for problem in problems:
        print(f"ERROR {problem}")
    print(
        f"checked {len(files)} Markdown files, {links} links, "
        f"{len(problems)} problem(s); skipped immutable '{ARCHIVE}/'"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
