# .aii — InstituteOS sidecar

A standalone, version-controlled sidecar that declares this repository's identity and
configuration within the [Active Inference Institute](https://www.activeinference.org)
ecosystem. It is read by **InstituteOS** tooling to federate a unified view across all
Institute repos — without touching the repo's own content (like `.github/`).

## Contents

| File | Purpose |
| --- | --- |
| [`config.yaml`](config.yaml) | Machine-readable identity, affiliation, category, ecosystem links, tags. |
| [`README.md`](README.md) | This file. |
| [`AGENTS.md`](AGENTS.md) | Agent guidance for InstituteOS conventions. |
| `docs/` | (optional) InstituteOS-specific documentation. |

## Schema

`config.yaml` validates against `instituteos.platform.aii_sidecar.models.AiiSidecar`
(`schema: aii-sidecar/v1`). It is intentionally minimal and human-editable; GitHub-derived
facts (stars, language, size) are **not** duplicated here — only curated metadata that the
API cannot provide.

This sidecar is independent of InstituteOS internals and is safe to keep in the public repo.
