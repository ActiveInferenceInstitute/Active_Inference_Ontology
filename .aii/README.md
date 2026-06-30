# .aii — InstituteOS sidecar

A standalone, version-controlled sidecar that declares this repository's identity and
configuration within the [Active Inference Institute](https://www.activeinference.org)
ecosystem. Read by **InstituteOS** tooling to federate a unified view across all Institute
repos — without touching the repo's own content (like `.github/`).

**This is the reference / exemplar `.aii` sidecar.** Other repos follow this shape.

## Contents

| File | Purpose |
| --- | --- |
| [`config.yaml`](config.yaml) | Machine-readable metadata (schema `aii-sidecar/v1`). |
| [`docs/INTEGRATION.md`](docs/INTEGRATION.md) | InstituteOS-specific integration notes for this repo. |
| [`README.md`](README.md) · [`AGENTS.md`](AGENTS.md) | Human + agent guidance. |

## `config.yaml` schema (`aii-sidecar/v1`)

| Section | Fields |
| --- | --- |
| `meta` | `sidecar_version`, `updated` |
| `repo` | `name`, `slug`, `full_name`, `description`, `default_branch`, `homepage` |
| `institute` | `affiliation` (institute\|ecosystem), `category`, `status`, `maturity`, `steward` |
| `ecosystem` | `relations[]` (`repo`, `relation`, `note`), `links{}` (URL or repo-path) |
| `artifacts[]` | `path`, `kind` (source\|dataset\|export\|code\|doc\|model), `description` |
| `provenance` | `license`, `citation{doi,zenodo,text}`, `current_release`, `releases_manifest` |
| `instituteos` | `dashboard_mode`, `registries[]`, `tags[]` |
| `docs[]` | paths under `.aii/` (validated to exist) |

Validate (and score completeness): `python -m instituteos.platform.aii_sidecar.validate <repo>`.
The validator checks the schema, that artifact/manifest/doc paths exist, that repo-relative
links resolve, and that relation targets are `owner/repo`.

Canonical schema/source: `instituteos.platform.aii_sidecar` in
[InstituteOS](https://github.com/ActiveInferenceInstitute/InstituteOS).
