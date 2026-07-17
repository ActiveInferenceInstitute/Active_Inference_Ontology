#!/usr/bin/env python3
"""Build, validate, diff, and publish the Active Inference Ontology."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import tempfile
import tomllib
from collections.abc import Iterable
from datetime import date
from importlib import metadata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "ontology.toml"
SOURCE_SCHEMA = "active-inference-ontology/source/v2"
EXPORT_SCHEMA = "active-inference-ontology/export/v2"
MANIFEST_SCHEMA = "active-inference-ontology/releases/v2"
DIFF_SCHEMA = "active-inference-ontology/diff/v2"
CSV_AUDIT_SCHEMA = "active-inference-ontology/csv-audit/v2"
PINNED_JSONSCHEMA = "4.24.0"
SOURCE_COLUMNS = [
    "List",
    "Tag",
    "Term",
    "Proposed Definition 1",
    "Proposed Definition 2",
    "Correct Examples",
    "Incorrect Examples",
    "Connections",
]
ID_PATTERN = re.compile(r"^term-[a-z0-9]+(?:-[a-z0-9]+)*$")
RELEASE_PATTERN = re.compile(r"^v(0|[1-9][0-9]*)$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_KINDS = {
    "source",
    "document",
    "package",
    "spreadsheet-export",
    "export",
    "site",
    "schema",
}


class OntologyError(Exception):
    """A user-correctable source, configuration, or artifact error."""


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def root_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    """Use a stable repository-relative path when possible."""

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def safe_relative_path(value: Any, label: str) -> Path:
    """Resolve a manifest path while preventing traversal outside the repository."""

    if not isinstance(value, str) or not value.strip():
        raise OntologyError(f"{label} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise OntologyError(f"{label} must stay within the repository: {value!r}")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise OntologyError(f"{label} must stay within the repository: {value!r}") from exc
    return resolved


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            config = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise OntologyError(f"missing configuration: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise OntologyError(f"invalid TOML configuration {path}: {exc}") from exc

    if config.get("schema_version") != 2:
        raise OntologyError("ontology.toml must declare schema_version = 2")
    for section in ("paths", "release", "validation"):
        if not isinstance(config.get(section), dict):
            raise OntologyError(f"ontology.toml is missing [{section}]")
    return config


def configured_paths(config: dict[str, Any]) -> dict[str, Path]:
    paths = config["paths"]
    required = (
        "source",
        "export",
        "csv_export",
        "manifest",
        "site",
        "source_schema",
        "export_schema",
        "manifest_schema",
    )
    missing = [key for key in required if not paths.get(key)]
    if missing:
        raise OntologyError("missing configured paths: " + ", ".join(missing))
    return {key: root_path(paths[key]) for key in required}


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise OntologyError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OntologyError(f"invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise OntologyError(f"invalid UTF-8 in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OntologyError(f"JSON root must be an object: {path}")
    return value


def write_atomic(path: Path, content: str, *, check: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if check:
        try:
            current = path.read_text(encoding="utf-8") if path.exists() else None
        except UnicodeDecodeError as exc:
            raise OntologyError(f"generated artifact is not valid UTF-8: {path}") from exc
        return current == content
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            handle.write(content)
            temporary = Path(handle.name)
        temporary.replace(path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return True


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if fieldnames != SOURCE_COLUMNS:
                raise OntologyError(
                    f"{path} must have exactly these columns: {', '.join(SOURCE_COLUMNS)}"
                )
            rows = []
            for line, row in enumerate(reader, start=2):
                if None in row:
                    raise OntologyError(f"{path}:{line}: extra unheaded columns")
                if any(row.get(key) is None for key in SOURCE_COLUMNS):
                    raise OntologyError(f"{path}:{line}: missing column value")
                rows.append({key: row.get(key, "") for key in SOURCE_COLUMNS})
            return rows
    except UnicodeDecodeError as exc:
        raise OntologyError(f"{path} is not valid UTF-8: {exc}") from exc


def mention_relations(text: str, self_id: str, terms: list[dict[str, Any]]) -> list[dict[str, str]]:
    lower = text.casefold()
    found: set[str] = set()
    for term in terms:
        if term["id"] == self_id:
            continue
        label = term["term"]
        pattern = r"(?<![\w])" + re.escape(label.casefold()) + r"(?![\w])"
        if re.search(pattern, lower, flags=re.UNICODE):
            found.add(term["id"])
    return [
        {"target": target, "type": "mentions"}
        for target in sorted(found)
    ]


def source_from_csv(
    csv_path: Path,
    config: dict[str, Any],
    release_override: dict[str, str] | None = None,
) -> dict[str, Any]:
    rows = read_csv(csv_path)
    terms: list[dict[str, Any]] = []
    seen_labels: set[str] = set()
    seen_ids: set[str] = set()
    for line, row in enumerate(rows, start=2):
        label = normalize(row["Term"])
        if not label:
            raise OntologyError(f"{csv_path}:{line}: empty Term")
        key = label.casefold()
        term_id = "term-" + slugify(label)
        if key in seen_labels:
            raise OntologyError(f"{csv_path}:{line}: duplicate term label {label!r}")
        if term_id in seen_ids:
            raise OntologyError(f"{csv_path}:{line}: duplicate generated id {term_id!r}")
        seen_labels.add(key)
        seen_ids.add(term_id)
        terms.append(
            {
                "id": term_id,
                "term": label,
                "aliases": [],
                "status": "published",
                "list": normalize(row["List"]),
                "tag": normalize(row["Tag"]) or None,
                "definitions": {
                    "primary": normalize(row["Proposed Definition 1"]) or None,
                    "secondary": normalize(row["Proposed Definition 2"]) or None,
                },
                "examples": {
                    "correct": normalize(row["Correct Examples"]) or None,
                    "incorrect": normalize(row["Incorrect Examples"]) or None,
                },
                "connectionsText": normalize(row["Connections"]) or None,
                "relations": [],
                "provenance": {
                    "sourceFile": csv_path.name,
                    "sourceRow": line,
                },
            }
        )

    for term in terms:
        if term["connectionsText"]:
            term["relations"] = mention_relations(
                term["connectionsText"], term["id"], terms
            )

    release = release_override or config["release"]
    return {
        "schema": SOURCE_SCHEMA,
        "release": {
            "version": str(release["version"]),
            "label": str(release["label"]),
            "date": str(release["date"]),
        },
        "terms": terms,
    }


def audit_csv(csv_path: Path) -> dict[str, Any]:
    """Return deterministic diagnostics without producing a source document."""

    report: dict[str, Any] = {
        "schema": CSV_AUDIT_SCHEMA,
        "path": display_path(csv_path),
        "valid": True,
        "rows": 0,
        "duplicateLabels": [],
        "generatedIdCollisions": [],
        "errors": [],
    }
    try:
        rows = read_csv(csv_path)
    except OntologyError as exc:
        report["valid"] = False
        report["errors"] = [str(exc)]
        return report

    labels: dict[str, list[dict[str, Any]]] = {}
    ids: dict[str, list[dict[str, Any]]] = {}
    for line, row in enumerate(rows, start=2):
        report["rows"] += 1
        label = normalize(row["Term"])
        if not label:
            report["errors"].append(f"{csv_path}:{line}: empty Term")
            continue
        label_record = {"row": line, "label": label}
        labels.setdefault(label.casefold(), []).append(label_record)
        generated_id = "term-" + slugify(label)
        ids.setdefault(generated_id, []).append(label_record)

    report["duplicateLabels"] = [
        {"normalized": key, "rows": value}
        for key, value in sorted(labels.items())
        if len(value) > 1
    ]
    report["generatedIdCollisions"] = [
        {"id": key, "rows": value}
        for key, value in sorted(ids.items())
        if len(value) > 1
    ]
    report["valid"] = not (
        report["errors"] or report["duplicateLabels"] or report["generatedIdCollisions"]
    )
    return report


def validate_source(
    source: Any, config: dict[str, Any], *, check_release: bool = True
) -> list[str]:
    errors: list[str] = []
    if not isinstance(source, dict):
        return ["source JSON root must be an object"]
    validation = config["validation"]
    if source.get("schema") != SOURCE_SCHEMA:
        errors.append(f"source schema must be {SOURCE_SCHEMA}")
    release = source.get("release")
    if not isinstance(release, dict):
        errors.append("source.release must be an object")
    else:
        for field in ("version", "label", "date"):
            if not normalize(release.get(field)):
                errors.append(f"source.release.{field} is required")
        if isinstance(release.get("version"), str) and not RELEASE_PATTERN.fullmatch(release["version"]):
            errors.append("source.release.version must match v<integer>")
        if isinstance(release.get("date"), str):
            try:
                date.fromisoformat(release["date"])
            except ValueError:
                errors.append("source.release.date must be an ISO date")
        if check_release and release.get("version") != config["release"]["version"]:
            errors.append("source release version does not match ontology.toml")
    terms = source.get("terms")
    if not isinstance(terms, list) or not terms:
        return errors + ["source.terms must be a non-empty array"]

    ids: dict[str, int] = {}
    labels: dict[str, int] = {}
    aliases: dict[str, int] = {}
    allowed_lists = set(validation["allowed_lists"])
    allowed_tags = set(validation["allowed_tags"])
    allowed_statuses = set(validation["statuses"])
    allowed_relations = set(validation["relation_types"])
    id_set: set[str] = set()
    for index, term in enumerate(terms, start=1):
        if isinstance(term, dict):
            term_id = term.get("id")
            if isinstance(term_id, str):
                if term_id in ids:
                    errors.append(f"terms[{index}].id duplicates terms[{ids[term_id]}]")
                else:
                    ids[term_id] = index
                    id_set.add(term_id)
    for index, term in enumerate(terms, start=1):
        if isinstance(term, dict):
            label = normalize(term.get("term"))
            if label:
                key = label.casefold()
                if key in labels:
                    errors.append(f"terms[{index}].term duplicates terms[{labels[key]}]")
                else:
                    labels[key] = index
    for index, term in enumerate(terms, start=1):
        if isinstance(term, dict) and isinstance(term.get("aliases"), list):
            for alias in term["aliases"]:
                if isinstance(alias, str) and normalize(alias):
                    key = normalize(alias).casefold()
                    if key in labels or key in aliases:
                        errors.append(f"terms[{index}].aliases contains a duplicate label/alias")
                    else:
                        aliases[key] = index
    for index, term in enumerate(terms, start=1):
        prefix = f"terms[{index}]"
        if not isinstance(term, dict):
            errors.append(f"{prefix} must be an object")
            continue
        term_id = term.get("id")
        label = normalize(term.get("term"))
        if not isinstance(term_id, str) or not ID_PATTERN.fullmatch(term_id):
            errors.append(f"{prefix}.id is invalid")
        elif term_id not in ids:
            ids[term_id] = index
            id_set.add(term_id)
        if not label:
            errors.append(f"{prefix}.term is required")
        else:
            key = label.casefold()
            if key not in labels:
                labels[key] = index
        aliases_value = term.get("aliases")
        if not isinstance(aliases_value, list) or not all(
            isinstance(alias, str) and normalize(alias) for alias in aliases_value
        ):
            errors.append(f"{prefix}.aliases must be an array of non-empty strings")
        else:
            for alias in aliases_value:
                key = normalize(alias).casefold()
                if key not in labels and key not in aliases:
                    aliases[key] = index
        status = term.get("status")
        if status not in allowed_statuses:
            errors.append(f"{prefix}.status is not allowed: {status!r}")
        list_name = term.get("list")
        if list_name not in allowed_lists:
            errors.append(f"{prefix}.list is not allowed: {list_name!r}")
        tag = term.get("tag")
        if tag is not None and tag not in allowed_tags:
            errors.append(f"{prefix}.tag is not allowed: {tag!r}")
        if list_name in set(validation["required_tag_lists"]) and not tag:
            errors.append(f"{prefix}.tag is required for list {list_name!r}")
        definitions = term.get("definitions")
        examples = term.get("examples")
        if not isinstance(definitions, dict) or not isinstance(examples, dict):
            errors.append(f"{prefix}.definitions and .examples must be objects")
        else:
            if list_name in set(validation["required_definition_lists"]):
                if not normalize(definitions.get("primary")):
                    errors.append(f"{prefix}.definitions.primary is required")
                if not normalize(examples.get("correct")):
                    errors.append(f"{prefix}.examples.correct is required")
            for section, value in (("definitions", definitions), ("examples", examples)):
                for field in ("primary", "secondary") if section == "definitions" else ("correct", "incorrect"):
                    if value.get(field) is not None and not isinstance(value.get(field), str):
                        errors.append(f"{prefix}.{section}.{field} must be a string or null")
        connections = term.get("connectionsText")
        if connections is not None and not isinstance(connections, str):
            errors.append(f"{prefix}.connectionsText must be a string or null")
        relations = term.get("relations")
        if not isinstance(relations, list):
            errors.append(f"{prefix}.relations must be an array")
            continue
        relation_keys: set[tuple[str, str]] = set()
        for rel_index, relation in enumerate(relations, start=1):
            rel_prefix = f"{prefix}.relations[{rel_index}]"
            if not isinstance(relation, dict):
                errors.append(f"{rel_prefix} must be an object")
                continue
            target = relation.get("target")
            relation_type = relation.get("type")
            if target == term_id:
                errors.append(f"{rel_prefix} cannot target its own term")
            if not isinstance(target, str) or not ID_PATTERN.fullmatch(target):
                errors.append(f"{rel_prefix}.target is invalid: {target!r}")
            elif target not in id_set:
                errors.append(f"{rel_prefix}.target is unknown: {target!r}")
            if relation_type not in allowed_relations:
                errors.append(f"{rel_prefix}.type is not allowed: {relation_type!r}")
            key = (str(target), str(relation_type))
            if key in relation_keys:
                errors.append(f"{rel_prefix} duplicates a relation")
            relation_keys.add(key)
    return errors


def validate_json_schemas(
    source: dict[str, Any],
    export: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    paths: dict[str, Path],
) -> list[str]:
    """Validate live documents against the repository's published schemas."""

    try:
        import jsonschema
    except ImportError:
        return [
            "strict validation requires jsonschema==4.24.0; "
            "install requirements-ci.txt"
        ]

    try:
        installed = metadata.version("jsonschema")
    except metadata.PackageNotFoundError:
        return [
            "strict validation requires jsonschema==4.24.0; "
            "install requirements-ci.txt"
        ]
    if installed != PINNED_JSONSCHEMA:
        return [
            f"strict validation requires jsonschema=={PINNED_JSONSCHEMA}; "
            f"found {installed}"
        ]

    documents = [
        ("source", source, paths["source_schema"]),
        ("export", export, paths["export_schema"]),
        ("manifest", manifest, paths["manifest_schema"]),
    ]
    errors: list[str] = []
    for name, document, schema_path in documents:
        if document is None:
            continue
        try:
            schema = read_json(schema_path)
            validator = jsonschema.Draft202012Validator(
                schema, format_checker=jsonschema.FormatChecker()
            )
            validator.check_schema(schema)
            validation_errors = sorted(
                validator.iter_errors(document),
                key=lambda error: tuple(str(part) for part in error.absolute_path),
            )
            for error in validation_errors:
                location = "".join(
                    f"[{part}]" if isinstance(part, int) else f".{part}"
                    for part in error.absolute_path
                ).lstrip(".")
                errors.append(
                    f"{name} schema violation at {location or '<root>'}: {error.message}"
                )
        except OntologyError as exc:
            errors.append(str(exc))
        except Exception as exc:
            errors.append(f"invalid {name} schema {schema_path}: {exc}")
    return errors


def build_export(source: dict[str, Any], config: dict[str, Any], source_path: Path) -> dict[str, Any]:
    errors = validate_source(source, config)
    if errors:
        raise OntologyError("source validation failed:\n- " + "\n- ".join(errors))
    terms = source["terms"]
    edges = []
    for term in terms:
        for relation in term["relations"]:
            edges.append(
                {
                    "source": term["id"],
                    "target": relation["target"],
                    "relation": relation["type"],
                }
            )
    edges.sort(key=lambda edge: (edge["source"], edge["target"], edge["relation"]))
    tags = sorted({term["tag"] for term in terms if term["tag"]})
    return {
        "schema": EXPORT_SCHEMA,
        "schemaVersion": "2.0",
        "release": source["release"],
        "source": {
            "path": display_path(source_path),
            "schema": source["schema"],
            "sha256": sha256(source_path),
        },
        "counts": {"terms": len(terms), "tags": len(tags), "edges": len(edges)},
        "tags": tags,
        "terms": terms,
        "graph": {
            "nodes": [
                {
                    "id": term["id"],
                    "label": term["term"],
                    "tag": term["tag"],
                    "status": term["status"],
                }
                for term in terms
            ],
            "edges": edges,
        },
    }


def csv_text(source: dict[str, Any]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=SOURCE_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for term in source["terms"]:
        writer.writerow(
            {
                "List": term["list"],
                "Tag": term["tag"] or "",
                "Term": term["term"],
                "Proposed Definition 1": term["definitions"]["primary"] or "",
                "Proposed Definition 2": term["definitions"]["secondary"] or "",
                "Correct Examples": term["examples"]["correct"] or "",
                "Incorrect Examples": term["examples"]["incorrect"] or "",
                "Connections": term["connectionsText"] or "",
            }
        )
    return output.getvalue()


def site_text(export: dict[str, Any]) -> str:
    payload = json.dumps(export, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    payload = payload.replace("</", "<\\/")
    title = html.escape("Active Inference Ontology")
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font: 16px/1.5 system-ui, sans-serif; margin: 0; color: #17202a; background: #f6f8fa; }}
header {{ background: #12304a; color: white; padding: 2rem max(1rem, 5vw); }}
main {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }}
label {{ display: inline-block; margin-right: .75rem; }}
input, select {{ font: inherit; padding: .55rem; margin: .2rem .5rem .8rem 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
article {{ background: white; border: 1px solid #d8dee4; border-radius: .5rem; padding: 1rem; }}
small, .muted {{ color: #57606a; }}
header .muted {{ color: #d7e4ee; }}
code {{ background: #eef1f4; padding: .1rem .25rem; border-radius: .2rem; }}
details {{ margin-top: .75rem; }}
</style>
</head>
<body>
<header>
<h1>{title}</h1>
<p id="summary"></p>
<p id="provenance" class="muted"></p>
</header>
<main>
<div class="filters">
<label for="search">Search <input id="search" type="search" placeholder="term, definition, alias, or example"></label>
<label for="tag">Tag <select id="tag"><option value="">All tags</option></select></label>
<label for="status">Status <select id="status"><option value="">All statuses</option></select></label>
</div>
<section id="terms" class="grid" aria-live="polite"></section>
</main>
<script>
const data = {payload};
const byId = new Map(data.terms.map(term => [term.id, term]));
const incoming = new Map(data.terms.map(term => [term.id, []]));
for (const term of data.terms) for (const relation of term.relations) {{
  if (incoming.has(relation.target)) incoming.get(relation.target).push({{ source: term.id, type: relation.type }});
}}
const search = document.querySelector('#search');
const tag = document.querySelector('#tag');
const status = document.querySelector('#status');
const terms = document.querySelector('#terms');
document.querySelector('#summary').textContent = `${{data.counts.terms}} terms · ${{data.counts.tags}} tags · ${{data.counts.edges}} relations · release ${{data.release.version}}`;
document.querySelector('#provenance').textContent = `Source: ${{data.source.path}} · SHA-256: ${{data.source.sha256}} · schema: ${{data.source.schema}}`;
for (const value of data.tags) tag.add(new Option(value, value));
for (const value of [...new Set(data.terms.map(term => term.status))].sort()) status.add(new Option(value, value));
function esc(value) {{ return String(value ?? '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char])); }}
function field(label, value) {{
  return value ? `<p><strong>${{esc(label)}}:</strong> ${{esc(value)}}</p>` : '';
}}
function render() {{
  const query = search.value.trim().toLowerCase();
  const filtered = data.terms.filter(term => {{
    const haystack = JSON.stringify(term).toLowerCase();
    return (!query || haystack.includes(query)) && (!tag.value || term.tag === tag.value) && (!status.value || term.status === status.value);
  }});
  terms.innerHTML = filtered.map(term => {{
    const aliases = term.aliases.length ? `<p><strong>Aliases:</strong> ${{term.aliases.map(esc).join(', ')}}</p>` : '';
    const outgoing = term.relations.map(rel => `${{rel.type}} → ${{byId.get(rel.target)?.term ?? rel.target}}`);
    const inbound = (incoming.get(term.id) ?? []).map(rel => `${{rel.type}} ← ${{byId.get(rel.source)?.term ?? rel.source}}`);
    const relations = [...outgoing, ...inbound].map(esc).join('<br>');
    return `<article data-term-id="${{esc(term.id)}}"><h2>${{esc(term.term)}}</h2><small>${{esc(term.id)}} · ${{esc(term.status)}} · ${{esc(term.tag ?? 'untagged')}}</small>${{aliases}}${{field('Definition', term.definitions.primary)}}${{field('Additional definition', term.definitions.secondary)}}${{field('Correct example', term.examples.correct)}}${{field('Incorrect example', term.examples.incorrect)}}<details><summary>Relation neighborhood (${{outgoing.length + inbound.length}})</summary><p class="muted">${{relations || 'No explicit relations.'}}</p></details></article>`;
  }}).join('') || '<p>No matching terms.</p>';
}}
search.addEventListener('input', render); tag.addEventListener('change', render); status.addEventListener('change', render); render();
</script>
</body>
</html>
'''


def validate_manifest(
    manifest_path: Path, config: dict[str, Any], *, verify_hashes: bool = True
) -> list[str]:
    try:
        manifest = read_json(manifest_path)
    except OntologyError as exc:
        return [str(exc)]
    errors: list[str] = []
    if manifest.get("schema") != MANIFEST_SCHEMA:
        errors.append(f"release manifest schema must be {MANIFEST_SCHEMA}")
    if not isinstance(manifest.get("currentRelease"), str):
        errors.append("release manifest currentRelease must be a string")
    releases = manifest.get("releases")
    if not isinstance(releases, list) or not releases:
        return errors + ["release manifest releases must be a non-empty array"]
    current = manifest.get("currentRelease")
    versions: list[int] = []
    seen_versions: set[str] = set()
    matches = [
        release for release in releases
        if isinstance(release, dict) and release.get("version") == current
    ]
    if len(matches) != 1:
        errors.append("currentRelease must identify exactly one release")
    current_statuses = 0
    for index, release in enumerate(releases, start=1):
        if not isinstance(release, dict):
            errors.append(f"releases[{index}] must be an object")
            continue
        version = release.get("version")
        prefix = f"release {version if version is not None else '<unknown>'}"
        if not isinstance(version, str) or not RELEASE_PATTERN.fullmatch(version):
            errors.append(f"{prefix}: version must match v<integer>")
        else:
            number = int(version[1:])
            versions.append(number)
            if version in seen_versions:
                errors.append(f"{prefix}: duplicate release version")
            seen_versions.add(version)
        for field in ("label", "notes"):
            if not isinstance(release.get(field), str) or not normalize(release[field]):
                errors.append(f"{prefix}: {field} is required")
        release_date = release.get("date")
        if release_date is not None:
            if not isinstance(release_date, str):
                errors.append(f"{prefix}: date must be an ISO date or null")
            else:
                try:
                    date.fromisoformat(release_date)
                except ValueError:
                    errors.append(f"{prefix}: date must be an ISO date or null")
        status = release.get("status")
        if status not in {"current", "archived"}:
            errors.append(f"{prefix}: status must be current or archived")
        elif status == "current":
            current_statuses += 1
        if "sourceSchema" not in release or "exportSchema" not in release:
            errors.append(f"{prefix}: sourceSchema and exportSchema are required")
        elif status == "current":
            if release.get("sourceSchema") != SOURCE_SCHEMA:
                errors.append(f"{prefix}: sourceSchema does not match v2")
            if release.get("exportSchema") != EXPORT_SCHEMA:
                errors.append(f"{prefix}: exportSchema does not match v2")
        elif release.get("sourceSchema") is not None or release.get("exportSchema") is not None:
            errors.append(f"{prefix}: archived schema identifiers must be null")
        summary = release.get("validationSummary")
        if not isinstance(summary, dict):
            errors.append(f"{prefix}: validationSummary must be an object")
        else:
            summary_status = summary.get("status")
            if summary_status not in {"passed", "not-evaluated"}:
                errors.append(f"{prefix}: validationSummary.status is invalid")
            for field in ("termCount", "tagCount", "relationCount"):
                value = summary.get(field)
                if status == "current" and (not isinstance(value, int) or value < 0):
                    errors.append(f"{prefix}: validationSummary.{field} must be a non-negative integer")
                elif status == "archived" and value is not None:
                    errors.append(f"{prefix}: archived validationSummary.{field} must be null")
            if status == "current" and summary_status != "passed":
                errors.append(f"{prefix}: current validationSummary.status must be passed")
            if status == "archived" and summary_status != "not-evaluated":
                errors.append(f"{prefix}: archived validationSummary.status must be not-evaluated")
        try:
            base = safe_relative_path(release.get("path"), f"{prefix}.path")
        except OntologyError as exc:
            errors.append(str(exc))
            base = None
        if base is not None and not base.is_dir():
            errors.append(f"{prefix}: path does not exist as a directory: {release.get('path')}")
        artifacts = release.get("artifacts")
        if not isinstance(artifacts, list):
            errors.append(f"{prefix}: artifacts must be an array")
            continue
        if not artifacts:
            errors.append(f"{prefix}: artifacts must not be empty")
        artifact_paths: set[str] = set()
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                errors.append(f"{prefix}: artifact must be an object")
                continue
            relative = artifact.get("path")
            kind = artifact.get("kind")
            if kind not in ARTIFACT_KINDS:
                errors.append(f"{prefix}: invalid artifact kind for {relative!r}")
            if not isinstance(relative, str) or not relative:
                errors.append(f"{prefix}: artifact path is missing")
                continue
            relative_path = Path(relative)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                errors.append(f"{prefix}: artifact path escapes release directory: {relative}")
                continue
            if relative in artifact_paths:
                errors.append(f"{prefix}: duplicate artifact path {relative}")
            artifact_paths.add(relative)
            artifact_path = (base / relative).resolve() if base is not None else None
            if artifact_path is not None and base is not None:
                try:
                    artifact_path.relative_to(base.resolve())
                except ValueError:
                    errors.append(f"{prefix}: artifact path escapes release directory: {relative}")
                    continue
            if artifact_path is None or not artifact_path.is_file():
                errors.append(f"{prefix}: missing artifact {relative}")
                continue
            expected = artifact.get("sha256")
            if not isinstance(expected, str) or not HASH_PATTERN.fullmatch(expected):
                errors.append(f"{prefix}: invalid hash for {relative}")
            elif verify_hashes and sha256(artifact_path) != expected:
                errors.append(f"{prefix}: hash mismatch for {relative}")
    if versions and versions != sorted(versions):
        errors.append("release entries must be ordered numerically by version")
    if current_statuses != 1:
        errors.append("exactly one release must have status=current")
    if matches:
        current_entry = matches[0]
        if current_entry.get("status") != "current":
            errors.append("current release must have status=current")
        if current_entry.get("version") != config["release"]["version"]:
            errors.append("current release version does not match ontology.toml")
        expected_paths = {
            Path(config["paths"][key]).as_posix()
            for key in ("source", "export", "csv_export", "site", "source_schema", "export_schema", "manifest_schema")
        }
        current_paths = {
            artifact.get("path")
            for artifact in current_entry.get("artifacts", [])
            if isinstance(artifact, dict)
        }
        missing_paths = sorted(expected_paths - current_paths)
        if missing_paths:
            errors.append("current release is missing artifacts: " + ", ".join(missing_paths))
    return errors


def quality_report(source: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    terms_value = source.get("terms", [])
    terms = [term for term in terms_value if isinstance(term, dict)] if isinstance(terms_value, list) else []
    missing = {
        "tag": sum(term.get("tag") is None for term in terms),
        "primaryDefinition": sum(not (term.get("definitions") or {}).get("primary") for term in terms),
        "correctExample": sum(not (term.get("examples") or {}).get("correct") for term in terms),
        "incorrectExample": sum(not (term.get("examples") or {}).get("incorrect") for term in terms),
        "connectionsText": sum(not term.get("connectionsText") for term in terms),
    }
    relation_count = sum(len(term.get("relations", [])) for term in terms)
    return {
        "termCount": len(terms),
        "tagCount": len({term.get("tag") for term in terms if term.get("tag")}),
        "relationCount": relation_count,
        "statuses": {
            status: sum(term.get("status") == status for term in terms)
            for status in config["validation"]["statuses"]
        },
        "missing": missing,
        "lists": {
            name: sum(term.get("list") == name for term in terms)
            for name in config["validation"]["allowed_lists"]
        },
    }


def load_and_validate(
    config: dict[str, Any], *, strict: bool = False
) -> tuple[dict[str, Any], dict[str, Path], list[str]]:
    paths = configured_paths(config)
    source = read_json(paths["source"])
    source_errors = validate_source(source, config)
    for schema_key, schema_id in (
        ("source_schema", SOURCE_SCHEMA),
        ("export_schema", EXPORT_SCHEMA),
        ("manifest_schema", MANIFEST_SCHEMA),
    ):
        schema_path = paths[schema_key]
        try:
            schema = read_json(schema_path)
            if not schema.get("$id") or schema.get("title") is None:
                source_errors.append(f"schema metadata is incomplete: {schema_path}")
            if schema.get("properties", {}).get("schema", {}).get("const") != schema_id:
                source_errors.append(f"schema identifier mismatch: {schema_path}")
        except OntologyError as exc:
            source_errors.append(str(exc))
    export = None
    try:
        export = read_json(paths["export"])
    except OntologyError as exc:
        source_errors.append(str(exc))
    source_is_valid = not validate_source(source, config)
    if export is not None and source_is_valid:
        expected_export = build_export(source, config, paths["source"])
        if export != expected_export:
            source_errors.append(f"generated export is stale: {paths['export']}")
    if source_is_valid:
        expected_csv = csv_text(source)
        if not paths["csv_export"].exists() or paths["csv_export"].read_text(encoding="utf-8") != expected_csv:
            source_errors.append(f"generated CSV is stale: {paths['csv_export']}")
        expected_site = site_text(build_export(source, config, paths["source"]))
        if not paths["site"].exists() or paths["site"].read_text(encoding="utf-8") != expected_site:
            source_errors.append(f"generated site is stale: {paths['site']}")
    source_errors.extend(validate_manifest(paths["manifest"], config))
    manifest = None
    try:
        manifest = read_json(paths["manifest"])
        current_release = next(
            release for release in manifest["releases"]
            if release.get("version") == manifest.get("currentRelease")
        )
        expected_counts = quality_report(source, config)
        for field, expected in (
            ("termCount", expected_counts["termCount"]),
            ("tagCount", expected_counts["tagCount"]),
            ("relationCount", expected_counts["relationCount"]),
        ):
            for location, actual in (
                (f"current release {field}", current_release.get(field)),
                (
                    f"current release validationSummary.{field}",
                    (current_release.get("validationSummary") or {}).get(field),
                ),
            ):
                if actual != expected:
                    source_errors.append(
                        f"{location} does not match source: {actual!r} != {expected!r}"
                    )
    except (OntologyError, KeyError, StopIteration) as exc:
        source_errors.append(f"cannot verify current release counts: {exc}")
    if strict:
        source_errors.extend(validate_json_schemas(source, export, manifest, paths))
    return source, paths, source_errors


def migrate_command(args: argparse.Namespace, config: dict[str, Any]) -> int:
    csv_path = root_path(args.csv)
    output = root_path(args.output)
    release = {
        "version": args.version or config["release"]["version"],
        "label": args.label or config["release"]["label"],
        "date": args.date or config["release"]["date"],
    }
    source = source_from_csv(csv_path, config, release_override=release)
    errors = validate_source(source, config, check_release=False)
    if errors:
        raise OntologyError("migration validation failed:\n- " + "\n- ".join(errors))
    write_atomic(output, canonical_json(source), check=False)
    print(f"Wrote {display_path(output)}: {len(source['terms'])} terms")
    return 0


def build_command(config: dict[str, Any], *, check: bool = False) -> int:
    paths = configured_paths(config)
    source = read_json(paths["source"])
    errors = validate_source(source, config)
    if errors:
        raise OntologyError("source validation failed:\n- " + "\n- ".join(errors))
    export = canonical_json(build_export(source, config, paths["source"]))
    if not write_atomic(paths["export"], export, check=check):
        raise OntologyError(f"generated export is stale: {paths['export']}")
    print(f"{'Checked' if check else 'Wrote'} {paths['export'].relative_to(ROOT)}")
    return 0


def export_csv_command(config: dict[str, Any], *, check: bool = False) -> int:
    paths = configured_paths(config)
    source = read_json(paths["source"])
    errors = validate_source(source, config)
    if errors:
        raise OntologyError("source validation failed:\n- " + "\n- ".join(errors))
    if not write_atomic(paths["csv_export"], csv_text(source), check=check):
        raise OntologyError(f"generated CSV is stale: {paths['csv_export']}")
    print(f"{'Checked' if check else 'Wrote'} {paths['csv_export'].relative_to(ROOT)}")
    return 0


def site_command(config: dict[str, Any], *, check: bool = False) -> int:
    paths = configured_paths(config)
    source = read_json(paths["source"])
    errors = validate_source(source, config)
    if errors:
        raise OntologyError("source validation failed:\n- " + "\n- ".join(errors))
    export = build_export(source, config, paths["source"])
    if not write_atomic(paths["site"], site_text(export), check=check):
        raise OntologyError(f"generated site is stale: {paths['site']}")
    print(f"{'Checked' if check else 'Wrote'} {paths['site'].relative_to(ROOT)}")
    return 0


def validate_command(config: dict[str, Any], *, strict: bool = False) -> int:
    source, _, errors = load_and_validate(config, strict=strict)
    report = quality_report(source, config)
    if errors:
        print("Ontology validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"Ontology validation passed: {report['termCount']} terms, "
        f"{report['relationCount']} relations, {report['tagCount']} tags."
    )
    return 0


def schema_check_command(config: dict[str, Any]) -> int:
    paths = configured_paths(config)
    source = read_json(paths["source"])
    export = read_json(paths["export"])
    manifest = read_json(paths["manifest"])
    errors = validate_json_schemas(source, export, manifest, paths)
    if errors:
        print("JSON Schema validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("JSON Schema validation passed: source, export, and release manifest.")
    return 0


def audit_csv_command(csv_path: Path) -> int:
    report = audit_csv(csv_path)
    print(canonical_json(report), end="")
    return 0 if report["valid"] else 1


def report_command(config: dict[str, Any]) -> int:
    source, _, errors = load_and_validate(config)
    report = quality_report(source, config)
    report["schema"] = SOURCE_SCHEMA
    report["release"] = source.get("release")
    report["errors"] = errors
    print(canonical_json(report), end="")
    return 1 if errors else 0


def comparable_term(term: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in term.items() if key != "provenance"}


def diff_command(old_path: Path, new_path: Path, config: dict[str, Any]) -> int:
    old = read_json(old_path)
    new = read_json(new_path)
    for label, source in (("old", old), ("new", new)):
        errors = validate_source(source, config, check_release=False)
        if errors:
            raise OntologyError(f"{label} source validation failed:\n- " + "\n- ".join(errors))
    old_terms = {term["id"]: term for term in old["terms"]}
    new_terms = {term["id"]: term for term in new["terms"]}
    added = sorted(set(new_terms) - set(old_terms))
    removed = sorted(set(old_terms) - set(new_terms))
    renamed = []
    case_only_renames = []
    alias_changes = []
    status_changes = []
    list_changes = []
    tag_changes = []
    relation_changes = []
    metadata_changes = []
    changed = []
    for term_id in sorted(set(old_terms) & set(new_terms)):
        before = old_terms[term_id]
        after = new_terms[term_id]
        if before["term"] != after["term"]:
            renamed.append({"id": term_id, "oldTerm": before["term"], "newTerm": after["term"]})
            if before["term"].casefold() == after["term"].casefold():
                case_only_renames.append(
                    {"id": term_id, "oldTerm": before["term"], "newTerm": after["term"]}
                )
        if before["aliases"] != after["aliases"]:
            alias_changes.append(
                {"id": term_id, "oldAliases": before["aliases"], "newAliases": after["aliases"]}
            )
        if before["status"] != after["status"]:
            status_changes.append(
                {"id": term_id, "oldStatus": before["status"], "newStatus": after["status"]}
            )
        if before["list"] != after["list"]:
            list_changes.append(
                {"id": term_id, "oldList": before["list"], "newList": after["list"]}
            )
        if before["tag"] != after["tag"]:
            tag_changes.append(
                {"id": term_id, "oldTag": before["tag"], "newTag": after["tag"]}
            )
        if before["relations"] != after["relations"]:
            relation_changes.append(
                {"id": term_id, "oldRelations": before["relations"], "newRelations": after["relations"]}
            )
        fields = sorted(
            key for key in comparable_term(before)
            if comparable_term(before).get(key) != comparable_term(after).get(key)
        )
        if fields:
            changed.append({"id": term_id, "fields": fields})
            metadata_fields = [
                field for field in fields if field not in {"term", "aliases", "status", "list", "tag", "relations"}
            ]
            if metadata_fields:
                metadata_changes.append({"id": term_id, "fields": metadata_fields})
    result = {
        "schema": DIFF_SCHEMA,
        "oldRelease": old["release"],
        "newRelease": new["release"],
        "addedIds": added,
        "removedIds": removed,
        "renamed": renamed,
        "caseOnlyRenames": case_only_renames,
        "aliasChanges": alias_changes,
        "statusChanges": status_changes,
        "listChanges": list_changes,
        "tagChanges": tag_changes,
        "relationChanges": relation_changes,
        "metadataChanges": metadata_changes,
        "changed": changed,
    }
    print(canonical_json(result), end="")
    return 0


def sync_manifest(config: dict[str, Any]) -> int:
    paths = configured_paths(config)
    manifest = read_json(paths["manifest"])
    errors = validate_manifest(paths["manifest"], config, verify_hashes=False)
    if errors:
        raise OntologyError("manifest validation failed:\n- " + "\n- ".join(errors))
    current = manifest.get("currentRelease")
    for release in manifest.get("releases", []):
        base = root_path(release.get("path", "."))
        for artifact in release.get("artifacts", []):
            artifact_path = base / artifact["path"]
            if not artifact_path.is_file():
                raise OntologyError(f"missing manifest artifact: {artifact_path}")
            artifact["sha256"] = sha256(artifact_path)
        if release.get("version") != current:
            continue
        source = read_json(paths["source"])
        release["termCount"] = len(source["terms"])
        release["tagCount"] = len({term["tag"] for term in source["terms"] if term["tag"]})
        release["relationCount"] = sum(len(term["relations"]) for term in source["terms"])
        release["sourceSchema"] = SOURCE_SCHEMA
        release["exportSchema"] = EXPORT_SCHEMA
        release["validationSummary"] = {
            "status": "passed",
            "termCount": release["termCount"],
            "tagCount": release["tagCount"],
            "relationCount": release["relationCount"],
        }
        break
    write_atomic(paths["manifest"], canonical_json(manifest))
    print(f"Updated {display_path(paths['manifest'])}")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build").add_argument("--check", action="store_true")
    validate = sub.add_parser("validate")
    validate.add_argument("--strict", action="store_true")
    sub.add_parser("report")
    sub.add_parser("schema-check")
    sub.add_parser("export-csv").add_argument("--check", action="store_true")
    sub.add_parser("site").add_argument("--check", action="store_true")
    migrate = sub.add_parser("migrate-csv")
    migrate.add_argument("csv", type=Path)
    migrate.add_argument("--output", type=Path, required=True)
    migrate.add_argument("--version")
    migrate.add_argument("--label")
    migrate.add_argument("--date")
    audit = sub.add_parser("audit-csv")
    audit.add_argument("csv", type=Path)
    diff = sub.add_parser("diff")
    diff.add_argument("old_source", type=Path)
    diff.add_argument("new_source", type=Path)
    sub.add_parser("sync-manifest")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        config = load_config(args.config)
        if args.command == "build":
            return build_command(config, check=args.check)
        if args.command == "validate":
            return validate_command(config, strict=args.strict)
        if args.command == "schema-check":
            return schema_check_command(config)
        if args.command == "report":
            return report_command(config)
        if args.command == "export-csv":
            return export_csv_command(config, check=args.check)
        if args.command == "site":
            return site_command(config, check=args.check)
        if args.command == "migrate-csv":
            return migrate_command(args, config)
        if args.command == "audit-csv":
            return audit_csv_command(root_path(args.csv))
        if args.command == "diff":
            return diff_command(root_path(args.old_source), root_path(args.new_source), config)
        if args.command == "sync-manifest":
            return sync_manifest(config)
        parser.error(f"unknown command: {args.command}")
    except OntologyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
