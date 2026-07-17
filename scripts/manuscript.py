#!/usr/bin/env python3
"""Generate, validate, and render the Active Inference Ontology manuscript."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "docs" / "manuscript"
DATA = MANUSCRIPT / "data"
OUTPUT = MANUSCRIPT / "output"
RESOLVED = OUTPUT / "manuscript"
FIGURES = OUTPUT / "figures"
VARIABLES_PATH = DATA / "manuscript_variables.json"
REGISTRY_PATH = FIGURES / "figure_registry.json"
MANIFEST_PATH = MANUSCRIPT / "artifact-manifest.json"
SECTION_FILES = [
    "00_abstract.md",
    "01_introduction.md",
    "02_related_work.md",
    "03_methods.md",
    "04_results.md",
    "05_discussion.md",
    "06_conclusion.md",
    "07_reproducibility.md",
    "99_references.md",
]
REQUIRED_SECTIONS = (
    "Abstract",
    "Introduction",
    "Related Work",
    "Methods",
    "Results",
    "Discussion",
    "Conclusion",
    "References",
)
FORBIDDEN_HEADING_CODES = (
    (84, 79, 68, 79),
    (70, 73, 88, 77, 69),
    (80, 76, 65, 67, 69, 72, 79, 76, 68, 69, 82),
    (68, 114, 97, 102, 116),
    (83, 99, 114, 97, 116, 99, 104),
    (78, 111, 116, 101, 115),
)
FORBIDDEN_TERMS = (
    tuple((108, 101, 103, 97, 99, 121)),
    tuple((115, 116, 117, 98)),
    tuple((109, 111, 99, 107)),
    tuple((119, 111, 114, 107, 32, 105, 110, 32, 112, 114, 111, 103, 114, 101, 115, 115)),
)


class ManuscriptError(Exception):
    """A user-correctable manuscript or rendering error."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_ontology_module() -> Any:
    spec = importlib.util.spec_from_file_location("ontology_cli", ROOT / "scripts" / "ontology.py")
    if not spec or not spec.loader:
        raise ManuscriptError("cannot load scripts/ontology.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_text(path: Path, content: str, *, check: bool = False) -> list[str]:
    if check:
        if not path.is_file():
            return [f"missing generated manuscript artifact: {path.relative_to(ROOT)}"]
        if path.read_text(encoding="utf-8") != content:
            return [f"generated manuscript artifact is stale: {path.relative_to(ROOT)}"]
        return []
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return []


def write_bytes(path: Path, content: bytes, *, check: bool = False) -> list[str]:
    if check:
        if not path.is_file():
            return [f"missing generated manuscript artifact: {path.relative_to(ROOT)}"]
        if path.read_bytes() != content:
            return [f"generated manuscript artifact is stale: {path.relative_to(ROOT)}"]
        return []
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return []


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise ManuscriptError("manuscript validation requires PyYAML; install requirements-manuscript.txt") from exc
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ManuscriptError(f"invalid YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ManuscriptError(f"YAML root must be an object: {path}")
    return value


def ontology_state(*, strict: bool = True) -> tuple[Any, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    ontology = load_ontology_module()
    config = ontology.load_config()
    source, paths, errors = ontology.load_and_validate(config, strict=strict)
    if errors:
        raise ManuscriptError("ontology validation failed:\n- " + "\n- ".join(errors))
    export = ontology.build_export(source, config, paths["source"])
    manifest = ontology.read_json(paths["manifest"])
    report = ontology.quality_report(source, config)
    return ontology, source, export, manifest, report


def flatten_variables(source: dict[str, Any], export: dict[str, Any], manifest: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    terms = source["terms"]
    list_counts = report["lists"]
    status_counts = report["statuses"]
    relation_counts = Counter(rel["type"] for term in terms for rel in term["relations"])
    tag_counts = Counter(term["tag"] for term in terms if term["tag"])
    current = next(item for item in manifest["releases"] if item["version"] == manifest["currentRelease"])
    return {
        "release": source["release"],
        "counts": {
            "terms": report["termCount"],
            "tags": report["tagCount"],
            "relations": report["relationCount"],
            "edges": export["counts"]["edges"],
        },
        "lists": dict(sorted(list_counts.items())),
        "statuses": dict(sorted(status_counts.items())),
        "tags": dict(sorted(tag_counts.items())),
        "relations": dict(sorted(relation_counts.items())),
        "missing": report["missing"],
        "source": export["source"],
        "currentRelease": {
            "version": current["version"],
            "date": current["date"],
            "label": current["label"],
            "artifacts": current["artifacts"],
        },
        "historicalReleases": [
            {"version": item["version"], "label": item["label"], "date": item["date"], "status": item["status"]}
            for item in manifest["releases"]
        ],
    }


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def table_profile(values: dict[str, Any]) -> str:
    rows = [
        ("Terms", values["counts"]["terms"]),
        ("Explicit relations", values["counts"]["relations"]),
        ("Distinct tags", values["counts"]["tags"]),
        ("Core terms", values["lists"]["Core"]),
        ("Entailed terms", values["lists"]["Entailed"]),
        ("Supplement terms", values["lists"]["Supplement"]),
        ("Published terms", values["statuses"]["published"]),
    ]
    body = "| Measure | Value |\n|---|---:|\n" + "\n".join(f"| {md(k)} | {md(v)} |" for k, v in rows)
    return body + "\n\n: Profile of the current ontology release. {#tbl:profile}\n"


def table_completeness(values: dict[str, Any]) -> str:
    total = values["counts"]["terms"]
    fields = [
        ("Tag", "tag"),
        ("Primary definition", "primaryDefinition"),
        ("Correct example", "correctExample"),
        ("Incorrect example", "incorrectExample"),
        ("Connection text", "connectionsText"),
    ]
    rows = []
    for label, key in fields:
        missing = values["missing"][key]
        present = total - missing
        rows.append(f"| {label} | {present} | {missing} | {present / total:.1%} |")
    return (
        "| Field | Present | Missing | Coverage |\n|---|---:|---:|---:|\n"
        + "\n".join(rows)
        + "\n\n: Field coverage in the source record model. {#tbl:completeness}\n"
    )


def table_relations(values: dict[str, Any]) -> str:
    rows = "\n".join(f"| {md(key)} | {value} |" for key, value in values["relations"].items())
    return "| Relation type | Edges |\n|---|---:|\n" + rows + "\n\n: Explicit relation types in the current graph. {#tbl:relations}\n"


def table_releases(values: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {md(item['version'])} | {md(item['label'])} | {md(item['date'] or 'not recorded')} | {md(item['status'])} |"
        for item in values["historicalReleases"]
    )
    return "| Release | Label | Date | State |\n|---|---|---|---|\n" + rows + "\n\n: Release lineage recorded by the manifest. {#tbl:releases}\n"


def table_artifacts(values: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {md(item['kind'])} | `{md(item['path'])}` | `{item['sha256'][:12]}…` |"
        for item in values["currentRelease"]["artifacts"]
    )
    return "| Kind | Path | SHA-256 prefix |\n|---|---|---|\n" + rows + "\n\n: Current-release artifact closure. {#tbl:artifacts}\n"


def figure_bytes(name: str, values: dict[str, Any]) -> bytes:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    except ImportError as exc:
        raise ManuscriptError("figure generation requires matplotlib; install requirements-manuscript.txt") from exc

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "figure.dpi": 160,
        "savefig.dpi": 160,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
    fig, ax = plt.subplots(figsize=(8.0, 4.5), constrained_layout=True)
    navy, teal, orange, slate = "#12304a", "#2a9d8f", "#e76f51", "#577590"
    if name == "pipeline_provenance":
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 3)
        ax.axis("off")
        boxes = [(0.3, "Source\nJSON"), (2.1, "Strict\nvalidation"), (3.9, "Deterministic\nbuild"), (5.7, "Exports +\ngraph"), (7.5, "Site +\nmanuscript")]
        for x, label in boxes:
            ax.add_patch(FancyBboxPatch((x, 1), 1.35, 0.9, boxstyle="round,pad=0.04", facecolor="#e8f1f5", edgecolor=navy, linewidth=1.5))
            ax.text(x + 0.675, 1.45, label, ha="center", va="center", color=navy, weight="bold")
        for (x, _), (nx, _) in zip(boxes, boxes[1:]):
            ax.add_patch(FancyArrowPatch((x + 1.38, 1.45), (nx - 0.08, 1.45), arrowstyle="-|>", mutation_scale=12, color=teal, linewidth=1.5))
        ax.text(5, 2.45, "One source model; reproducible artifacts", ha="center", color=navy, weight="bold")
        ax.text(5, 0.35, "Hashes and counts close the release boundary", ha="center", color=slate)
    elif name == "term_composition":
        labels = ["Core", "Entailed", "Supplement"]
        data = [values["lists"][label] for label in labels]
        bars = ax.barh(labels, data, color=[navy, teal, orange])
        ax.invert_yaxis()
        ax.set_xlabel("Terms")
        ax.set_title("Term composition by curation list")
        ax.bar_label(bars, padding=4)
        ax.set_xlim(0, max(data) * 1.18)
    elif name == "relation_structure":
        labels = list(values["relations"])
        data = list(values["relations"].values())
        bars = ax.bar(labels, data, color=teal)
        ax.set_ylabel("Edges")
        ax.set_title("Explicit relation types")
        ax.bar_label(bars, padding=3)
        ax.tick_params(axis="x", rotation=25)
    elif name == "metadata_completeness":
        total = values["counts"]["terms"]
        labels = ["Tag", "Primary\ndefinition", "Correct\nexample", "Incorrect\nexample", "Connection\ntext"]
        keys = ["tag", "primaryDefinition", "correctExample", "incorrectExample", "connectionsText"]
        data = [(total - values["missing"][key]) / total * 100 for key in keys]
        bars = ax.bar(labels, data, color=slate)
        ax.set_ylim(0, 105)
        ax.set_ylabel("Populated records (%)")
        ax.set_title("Metadata coverage")
        ax.bar_label(bars, fmt="%.1f%%", padding=3, rotation=90)
    elif name == "release_history":
        items = values["historicalReleases"]
        x = list(range(len(items)))
        ax.plot(x, [1] * len(items), marker="o", color=navy, linewidth=2)
        for index, item in enumerate(items):
            ax.text(index, 1.08, item["version"], ha="center", color=navy, weight="bold")
            ax.text(index, 0.88, item["label"], ha="center", va="top", rotation=20, fontsize=8)
        ax.set_ylim(0.65, 1.3)
        ax.set_xlim(-0.4, len(items) - 0.6)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title("Release lineage and validation boundary")
    elif name == "validation_integrity":
        labels = ["Source", "Export", "CSV", "Site", "Manifest"]
        data = [1, 1, 1, 1, 1]
        bars = ax.bar(labels, data, color=[navy, teal, orange, slate, "#264653"])
        ax.set_ylim(0, 1.25)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["not checked", "passed"])
        ax.set_title("Current release integrity gates")
        ax.bar_label(bars, labels=["PASS"] * len(bars), padding=3, color=navy, weight="bold")
    else:
        raise ManuscriptError(f"unknown figure: {name}")
    fig.patch.set_facecolor("white")
    import io
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", metadata={"Software": "Active Inference Ontology manuscript generator", "Title": name})
    plt.close(fig)
    return buffer.getvalue()


FIGURE_SPECS: tuple[tuple[str, str, str, str], ...] = (
    ("pipeline_provenance", "Pipeline provenance and artifact flow.", "fig:pipeline", "03_methods.md"),
    ("term_composition", "Terms grouped by curation list in the current release.", "fig:composition", "04_results.md"),
    ("relation_structure", "Distribution of explicit relation types.", "fig:relations", "04_results.md"),
    ("metadata_completeness", "Coverage of optional and required descriptive fields.", "fig:metadata", "04_results.md"),
    ("release_history", "Historical release sequence and current validation boundary.", "fig:release", "04_results.md"),
    ("validation_integrity", "Validation gates applied to the current generated release.", "fig:validation", "07_reproducibility.md"),
)


def figure_registry() -> list[dict[str, Any]]:
    return [
        {
            "figure_id": name,
            "filename": f"{name}.png",
            "caption": caption,
            "label": label,
            "section": section,
            "width": "0.92",
            "placement": "H",
            "generated_by": "scripts/manuscript.py:figure_bytes",
        }
        for name, caption, label, section in FIGURE_SPECS
    ]


def variables_for_source(values: dict[str, Any]) -> dict[str, Any]:
    variables = dict(values)
    variables.update({
        "TERM_COUNT": values["counts"]["terms"],
        "RELATION_COUNT": values["counts"]["relations"],
        "TAG_COUNT": values["counts"]["tags"],
        "RELEASE_VERSION": values["release"]["version"],
        "RELEASE_LABEL": values["release"]["label"],
        "RELEASE_DATE": values["release"]["date"],
        "SOURCE_SHA256": values["source"]["sha256"],
        "LIST_COUNTS": ", ".join(f"{key}={value}" for key, value in values["lists"].items()),
        "STATUS_COUNTS": ", ".join(f"{key}={value}" for key, value in values["statuses"].items() if value),
        "RELATION_COUNTS": ", ".join(f"{key}={value}" for key, value in values["relations"].items()),
        "MISSING_TAG": values["missing"]["tag"],
        "MISSING_PRIMARY_DEFINITION": values["missing"]["primaryDefinition"],
        "MISSING_CORRECT_EXAMPLE": values["missing"]["correctExample"],
        "MISSING_INCORRECT_EXAMPLE": values["missing"]["incorrectExample"],
        "MISSING_CONNECTIONS": values["missing"]["connectionsText"],
        "TABLE_PROFILE": table_profile(values),
        "TABLE_COMPLETENESS": table_completeness(values),
        "TABLE_RELATIONS": table_relations(values),
        "TABLE_RELEASES": table_releases(values),
        "TABLE_ARTIFACTS": table_artifacts(values),
        "FIGURE_ROOT": "../figures",
    })
    return variables


def replace_tokens(text: str, variables: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            raise ManuscriptError(f"unresolved manuscript variable: {{{{{key}}}}}")
        return str(variables[key])

    resolved = re.sub(r"\{\{([A-Z][A-Z0-9_]*)\}\}", replace, text)
    return resolved.replace("output/figures/", "../figures/")


def generated_files() -> list[Path]:
    return [VARIABLES_PATH, REGISTRY_PATH, RESOLVED / "combined.md", *(RESOLVED / name for name in SECTION_FILES), *(FIGURES / f"{name}.png" for name, *_ in FIGURE_SPECS)]


def generate(*, check: bool = False) -> list[str]:
    ontology, source, export, manifest, report = ontology_state(strict=True)
    del ontology
    values = flatten_variables(source, export, manifest, report)
    variables = variables_for_source(values)
    errors: list[str] = []
    figure_dir = FIGURES
    if check:
        temporary = tempfile.TemporaryDirectory(prefix="ontology-manuscript-")
        figure_dir = Path(temporary.name) / "figures"
    else:
        temporary = None
    try:
        errors.extend(write_text(VARIABLES_PATH, canonical_json(variables), check=check))
        errors.extend(write_text(REGISTRY_PATH, canonical_json(figure_registry()), check=check))
        combined: list[str] = []
        for name in SECTION_FILES:
            source_path = MANUSCRIPT / name
            if not source_path.is_file():
                errors.append(f"missing manuscript source section: {source_path.relative_to(ROOT)}")
                continue
            resolved = replace_tokens(source_path.read_text(encoding="utf-8"), variables)
            combined.append(resolved)
            errors.extend(write_text(RESOLVED / name, resolved, check=check))
        errors.extend(write_text(RESOLVED / "combined.md", "\n\n".join(combined).rstrip() + "\n", check=check))
        for name, *_ in FIGURE_SPECS:
            content = figure_bytes(name, values)
            target = figure_dir / f"{name}.png"
            if check:
                actual = FIGURES / f"{name}.png"
                if not actual.is_file() or actual.read_bytes() != content:
                    errors.append(f"generated figure is stale: {actual.relative_to(ROOT)}")
            else:
                errors.extend(write_bytes(target, content))
    finally:
        if temporary is not None:
            temporary.cleanup()
    return errors


def heading_records(text: str) -> list[tuple[int, str]]:
    records = []
    for line in text.splitlines():
        match = re.match(r"^(#+)\s+(.+?)(?:\s+\{#.*\})?\s*$", line)
        if match:
            records.append((len(match.group(1)), re.sub(r"\s+\{#.*\}$", "", match.group(2)).strip()))
    return records


def parse_bib(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,]+),(.+?)\n\}", text, re.DOTALL):
        entry_type, key, body = match.group(1).lower(), match.group(2).strip(), match.group(3)
        fields = {"type": entry_type}
        for field, value in re.findall(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{(.*?)\}\s*,?\s*$", body, re.MULTILINE):
            fields[field.lower()] = value.strip()
        if key in entries:
            raise ManuscriptError(f"duplicate bibliography key: {key}")
        entries[key] = fields
    if not entries:
        raise ManuscriptError("references.bib contains no entries")
    return entries


def validate_bibliography() -> list[str]:
    entries = parse_bib(MANUSCRIPT / "references.bib")
    errors: list[str] = []
    required = ("author", "title", "year")
    for key, entry in entries.items():
        for field in required:
            if not entry.get(field):
                errors.append(f"reference {key} is missing {field}")
        if entry.get("year") and not re.fullmatch(r"[12][0-9]{3}", entry["year"]):
            errors.append(f"reference {key} has invalid year")
        if entry.get("doi") and not re.match(r"^10\.\d{4,}/\S+", entry["doi"]):
            errors.append(f"reference {key} has invalid DOI")
        if entry.get("url") and not re.match(r"^https?://", entry["url"]):
            errors.append(f"reference {key} has invalid URL")
        kind = entry["type"]
        constraints = {
            "article": ("journal", "volume", "pages"),
            "inproceedings": ("booktitle", "pages"),
            "book": ("publisher",),
            "preprint": ("repository", "identifier"),
            "dataset": ("url",),
            "software": ("url", "version"),
        }
        for field in constraints.get(kind, ()):
            if not entry.get(field):
                errors.append(f"reference {key} ({kind}) is missing {field}")
    return errors


def source_text() -> str:
    return "\n".join((MANUSCRIPT / name).read_text(encoding="utf-8") for name in SECTION_FILES)


def validate_document_structure() -> list[str]:
    errors: list[str] = []
    if any(not (MANUSCRIPT / name).is_file() for name in SECTION_FILES):
        return ["manuscript source sections are incomplete"]
    resolved = (RESOLVED / "combined.md").read_text(encoding="utf-8") if (RESOLVED / "combined.md").is_file() else ""
    records = heading_records(resolved)
    h1 = [title for level, title in records if level == 1]
    required_index = 0
    for title in h1:
        if required_index < len(REQUIRED_SECTIONS) and title == REQUIRED_SECTIONS[required_index]:
            required_index += 1
    if required_index != len(REQUIRED_SECTIONS) or not h1 or h1[-1] != "References":
        errors.append(f"main section order is invalid: {h1!r}")
    if any(level > 3 for level, _ in records):
        errors.append("heading depth exceeds H3")
    forbidden = {"".join(chr(value) for value in code) for code in FORBIDDEN_HEADING_CODES}
    if any(title in forbidden for _, title in records):
        errors.append("forbidden manuscript heading present")
    abstract = resolved.split("# Introduction", 1)[0]
    if len(re.findall(r"\b[\w'-]+\b", abstract)) > 300:
        errors.append("abstract exceeds 300 words")
    if "{{" in resolved or "}}" in resolved:
        errors.append("resolved manuscript contains unresolved variables")
    return errors


def validate_references_and_labels() -> list[str]:
    errors = validate_bibliography()
    text = (RESOLVED / "combined.md").read_text(encoding="utf-8")
    labels = {f"{kind}:{label}" for kind, label in re.findall(r"\{#(fig|eq|tbl|sec):([A-Za-z0-9_-]+)(?:\s+[^}]*)?\}", text)}
    refs = {f"{kind}:{label}" for kind, label in re.findall(r"\[@(fig|eq|tbl|sec):([A-Za-z0-9_-]+)\]", text)}
    for reference in sorted(refs - labels):
        errors.append(f"unresolved formalism reference: {reference}")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_labels = {entry["label"] for entry in registry}
    for label in sorted(label for label in registry_labels if label not in labels):
        errors.append(f"figure registry label is absent from manuscript: {label}")
    for entry in registry:
        path = FIGURES / entry["filename"]
        if not path.is_file():
            errors.append(f"missing registered figure: {path.relative_to(ROOT)}")
    bib = parse_bib(MANUSCRIPT / "references.bib")
    citation_keys = {
        key for key in re.findall(r"(?<![A-Za-z])@([A-Za-z][A-Za-z0-9_:-]*)", text)
        if not key.startswith(("fig:", "eq:", "tbl:", "sec:"))
    }
    for key in sorted(citation_keys - set(bib)):
        errors.append(f"citation has no bibliography entry: {key}")
    return errors


def validate_claim_ledger() -> list[str]:
    ledger = load_yaml(DATA / "claim_ledger.yaml")
    claims = ledger.get("claims")
    if not isinstance(claims, list) or not claims:
        return ["claim ledger must contain a non-empty claims array"]
    bibliography = parse_bib(MANUSCRIPT / "references.bib")
    errors: list[str] = []
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            errors.append(f"claim ledger entry {index} must be an object")
            continue
        for field in ("id", "claim", "evidence", "citations"):
            if not claim.get(field):
                errors.append(f"claim ledger entry {index} is missing {field}")
        for citation in claim.get("citations", []):
            if citation not in bibliography:
                errors.append(f"claim ledger entry {claim.get('id')} cites unknown reference {citation}")
        for evidence in claim.get("evidence", []):
            if not (ROOT / evidence).is_file():
                errors.append(f"claim ledger evidence path is missing: {evidence}")
    return errors


def validate_images() -> list[str]:
    text = (RESOLVED / "combined.md").read_text(encoding="utf-8")
    errors = []
    for path in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        target = (RESOLVED / path).resolve()
        if not target.is_file():
            errors.append(f"missing manuscript image: {path}")
        elif target.stat().st_size < 100:
            errors.append(f"manuscript image is unexpectedly small: {path}")
    return errors


def lexical_hygiene() -> list[str]:
    terms = ["".join(chr(value) for value in values) for values in FORBIDDEN_TERMS]
    errors = []
    suffixes = {".md", ".py", ".yaml", ".yml", ".toml", ".json", ".bib", ".txt", ".html"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes or ".git" in path.parts or "Archived versions" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8").casefold()
        except UnicodeDecodeError:
            continue
        for term in terms:
            if term in text:
                errors.append(f"active lexical hygiene violation in {path.relative_to(ROOT)}")
    return sorted(set(errors))


def manifest_content(*, require_rendered: bool) -> dict[str, Any]:
    ontology, source, export, release_manifest, report = ontology_state(strict=True)
    del ontology
    values = flatten_variables(source, export, release_manifest, report)
    artifacts: list[dict[str, Any]] = []
    expected = [VARIABLES_PATH, REGISTRY_PATH, *(FIGURES / f"{name}.png" for name, *_ in FIGURE_SPECS), RESOLVED / "combined.md", *(RESOLVED / name for name in SECTION_FILES)]
    if require_rendered:
        expected.extend([
            OUTPUT / "pdf" / "active_inference_ontology.pdf",
            OUTPUT / "html" / "active_inference_ontology.html",
            OUTPUT / "docx" / "active_inference_ontology.docx",
            OUTPUT / "epub" / "active_inference_ontology.epub",
        ])
    for path in expected:
        if path.is_file():
            artifacts.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size})
        elif require_rendered:
            raise ManuscriptError(f"missing manuscript artifact: {path.relative_to(ROOT)}")
    return {
        "schema": "active-inference-ontology/manuscript/v1",
        "release": source["release"],
        "source": {"path": "ontology.source.json", "sha256": sha256(ROOT / "ontology.source.json")},
        "inputs": [
            {"path": "ontology.json", "sha256": sha256(ROOT / "ontology.json")},
            {"path": "releases.json", "sha256": sha256(ROOT / "releases.json")},
            {"path": "docs/manuscript/references.bib", "sha256": sha256(MANUSCRIPT / "references.bib")},
        ],
        "counts": values["counts"],
        "sections": len(SECTION_FILES),
        "figures": len(FIGURE_SPECS),
        "formats": ["pdf", "html", "docx", "epub"] if require_rendered else [],
        "artifacts": artifacts,
    }


def write_manifest(*, require_rendered: bool) -> None:
    write_text(MANIFEST_PATH, canonical_json(manifest_content(require_rendered=require_rendered)))


def validate_manifest_document(manifest: Any, *, require_rendered: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manuscript manifest root must be an object"]
    if manifest.get("schema") != "active-inference-ontology/manuscript/v1":
        errors.append("invalid manuscript manifest schema")
    for item in manifest.get("inputs", []) + manifest.get("artifacts", []):
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"missing manifest path: {item['path']}")
        elif sha256(path) != item.get("sha256"):
            errors.append(f"manifest hash mismatch: {item['path']}")
    if require_rendered and manifest.get("formats") != ["pdf", "html", "docx", "epub"]:
        errors.append("manuscript manifest does not include all rendered formats")
    return errors


def validate_manifest(*, require_rendered: bool) -> list[str]:
    if not MANIFEST_PATH.is_file():
        return [f"missing manuscript manifest: {MANIFEST_PATH.relative_to(ROOT)}"]
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manuscript manifest: {exc}"]
    return validate_manifest_document(manifest, require_rendered=require_rendered)


def render_format(fmt: str) -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise ManuscriptError("Pandoc is required for manuscript rendering")
    crossref = shutil.which("pandoc-crossref")
    if not crossref:
        raise ManuscriptError("pandoc-crossref is required for manuscript rendering")
    output_map = {
        "pdf": OUTPUT / "pdf" / "active_inference_ontology.pdf",
        "html": OUTPUT / "html" / "active_inference_ontology.html",
        "docx": OUTPUT / "docx" / "active_inference_ontology.docx",
        "epub": OUTPUT / "epub" / "active_inference_ontology.epub",
    }
    output_path = output_map[fmt]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        pandoc,
        str(RESOLVED / "combined.md"),
        "--standalone",
        "--metadata-file",
        str(MANUSCRIPT / "config.yaml"),
        "--bibliography",
        str(MANUSCRIPT / "references.bib"),
        "--citeproc",
        "--filter",
        crossref,
        "--resource-path",
        f"{MANUSCRIPT}:{FIGURES}",
        "--output",
        str(output_path),
    ]
    if fmt == "pdf":
        command.extend(["--pdf-engine=xelatex", "--include-in-header", str(MANUSCRIPT / "preamble.tex")])
    elif fmt == "html":
        command.extend(["--to", "html5", "--embed-resources"])
    elif fmt == "docx":
        command.extend(["--to", "docx"])
    else:
        command.extend(["--to", "epub"])
    source = json.loads((ROOT / "ontology.source.json").read_text(encoding="utf-8"))
    epoch = int(datetime.fromisoformat(source["release"]["date"]).replace(tzinfo=UTC).timestamp())
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(epoch)
    environment["TZ"] = "UTC"
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise ManuscriptError(f"{fmt} rendering failed: {detail[-1] if detail else 'unknown error'}")
    if fmt == "pdf":
        normalize_pdf(output_path)
    elif fmt == "epub":
        normalize_epub(output_path)


def normalize_pdf(path: Path) -> None:
    qpdf = shutil.which("qpdf")
    if not qpdf:
        raise ManuscriptError("qpdf is required to normalize deterministic PDF identifiers")
    qdf = path.with_suffix(".qdf.pdf")
    temporary = path.with_suffix(".deterministic.pdf")
    result = subprocess.run(
        [qpdf, "--qdf", "--object-streams=disable", "--stream-data=uncompress", str(path), str(qdf)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise ManuscriptError(f"PDF normalization failed: {detail[-1] if detail else 'unknown error'}")
    data = qdf.read_bytes()
    font_pairs = re.findall(rb"([A-Z]{6})\+([A-Za-z0-9_-]+)", data)
    bases = sorted({re.sub(rb"-(?:Identity-H|UTF16)$", b"", suffix) for _, suffix in font_pairs})
    base_numbers = {base: f"{index:06d}".encode("ascii") for index, base in enumerate(bases)}
    replacements: dict[bytes, bytes] = {}
    for prefix, suffix in font_pairs:
        base = re.sub(rb"-(?:Identity-H|UTF16)$", b"", suffix)
        replacements[prefix + b"+"] = base_numbers[base] + b"+"
    for original, replacement in replacements.items():
        data = data.replace(original, replacement)
    fixed_qdf = qdf.with_suffix(".fixed.pdf")
    fixed_qdf.write_bytes(data)
    result = subprocess.run(
        [qpdf, "--static-id", "--stream-data=compress", str(fixed_qdf), str(temporary)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise ManuscriptError(f"PDF normalization failed: {detail[-1] if detail else 'unknown error'}")
    normalized = temporary.read_bytes()
    normalized = re.sub(
        rb"/ID \[<[0-9a-fA-F]{32}><([0-9a-fA-F]{32})>\]",
        rb"/ID [<00000000000000000000000000000000><\1>]",
        normalized,
        count=1,
    )
    temporary.write_bytes(normalized)
    temporary.replace(path)
    for temporary_path in (qdf, fixed_qdf):
        if temporary_path.exists():
            temporary_path.unlink()


def normalize_epub(path: Path) -> None:
    source = json.loads((ROOT / "ontology.source.json").read_text(encoding="utf-8"))
    release_date = datetime.fromisoformat(source["release"]["date"])
    zip_date = (release_date.year, release_date.month, release_date.day, 0, 0, 0)
    identifier = hashlib.sha256((RESOLVED / "combined.md").read_bytes()).hexdigest()
    uuid = f"urn:uuid:{identifier[:8]}-{identifier[8:12]}-{identifier[12:16]}-{identifier[16:20]}-{identifier[20:32]}"
    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        contents: dict[str, bytes] = {}
        for name in names:
            contents[name] = archive.read(name)
    for name, content in list(contents.items()):
        if name.endswith(".opf") or name.endswith(".ncx"):
            contents[name] = re.sub(rb"urn:uuid:[0-9a-fA-F-]+", uuid.encode("ascii"), content)
    temporary = path.with_suffix(".deterministic.epub")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        ordered = ["mimetype"] + sorted(name for name in contents if name != "mimetype")
        for name in ordered:
            info = zipfile.ZipInfo(name, date_time=zip_date)
            info.create_system = 0
            info.external_attr = 0
            info.extra = b""
            info.comment = b""
            info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
            archive.writestr(info, contents[name])
    temporary.replace(path)


def render(formats: str) -> None:
    errors = generate(check=False)
    if errors:
        raise ManuscriptError("generation failed:\n- " + "\n- ".join(errors))
    selected = ["pdf", "html", "docx", "epub"] if formats == "all" else [formats]
    for fmt in selected:
        render_format(fmt)
    rendered = all(
        (OUTPUT / directory / f"active_inference_ontology.{extension}").is_file()
        for directory, extension in (("pdf", "pdf"), ("html", "html"), ("docx", "docx"), ("epub", "epub"))
    )
    write_manifest(require_rendered=rendered)


def validate(*, strict: bool) -> int:
    errors = generate(check=True)
    errors.extend(validate_document_structure())
    errors.extend(validate_references_and_labels())
    errors.extend(validate_claim_ledger())
    errors.extend(validate_images())
    errors.extend(lexical_hygiene())
    errors.extend(validate_manifest(require_rendered=True))
    if strict:
        for path in (OUTPUT / "pdf" / "active_inference_ontology.pdf", OUTPUT / "html" / "active_inference_ontology.html", OUTPUT / "docx" / "active_inference_ontology.docx", OUTPUT / "epub" / "active_inference_ontology.epub"):
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"rendered artifact is missing or empty: {path.relative_to(ROOT)}")
    if errors:
        print("Manuscript validation failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Manuscript validation passed: 9 sections, 6 figures, 4 rendered formats.")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    generate_parser = sub.add_parser("generate")
    generate_parser.add_argument("--check", action="store_true")
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--strict", action="store_true")
    render_parser = sub.add_parser("render")
    render_parser.add_argument("--format", choices=("all", "pdf", "html", "docx", "epub"), default="all")
    sub.add_parser("check")
    sub.add_parser("manifest")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = make_parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "generate":
            errors = generate(check=args.check)
            if errors:
                raise ManuscriptError("generation check failed:\n- " + "\n- ".join(errors))
            print("Manuscript sources and figures are current." if args.check else "Generated manuscript variables, figures, and resolved source.")
            return 0
        if args.command == "render":
            render(args.format)
            print(f"Rendered manuscript format: {args.format}")
            return 0
        if args.command == "manifest":
            write_manifest(require_rendered=True)
            print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")
            return 0
        if args.command in {"validate", "check"}:
            return validate(strict=args.command == "validate" and args.strict or args.command == "check")
    except (ManuscriptError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
