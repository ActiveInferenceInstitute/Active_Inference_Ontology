# Active Inference Ontology TODO

This backlog scopes improvements by effort and risk. Minor tasks should be
small documentation or validation hardening. Medium tasks usually change data
contracts or release process. Major tasks reshape ontology governance,
publishing, or integration architecture.

## Completed Improvements

- [x] Add a short `README.md` inside each archive snapshot folder that records
      source date, source files, and notable differences from the prior version.
- [x] Add a CSV lint check for required headers, empty `Term` values, and
      duplicate term labels before JSON generation.
- [x] Add a small sample consumer snippet to `docs/downstream-integration.md`
      showing how to load `ontology.json` and validate graph ids.
- [x] Add a changelog section to the root `README.md` for release-level changes
      after v5.
- [x] Remove skipped duplicate or empty CSV rows while preserving generated
      `ontology.json` semantics.
- [x] Add a public citation note that explains how to cite both the Zenodo DOI
      and a repository release tag.
- [x] Add a machine-readable release manifest covering each archived version,
      including version, date, source files, term count when known, and notes.
- [x] Add a validation report that lists unresolved connection rows and likely
      canonical-term matches.
- [x] Add CI that runs `python3 scripts/build_json.py --check` and CSV lint
      checks on every pull request.
- [x] Add a documented release workflow for creating `Ontology_v6_*.csv`,
      rebuilding `ontology.json`, snapshotting archives, and tagging releases.
- [x] Add a JavaScript consumer snippet beside the Python example in
      `docs/downstream-integration.md`.
- [x] Build a version-diff pipeline that reports added, removed, renamed, and
      semantically changed terms across releases.
- [x] Establish a formal curation governance process with review roles,
      approval criteria, and release sign-off records.
- [x] Create a durable SUMO mapping contract with term ids, SUMO identifiers,
      mapping relations, confidence, reviewer, and review date.

## Minor Improvements

- [ ] Normalize obvious whitespace and punctuation artifacts in the CSV while
      preserving term meaning beyond the duplicate/empty rows already removed.

## Medium Improvements

- [ ] Add typed relation extraction for `Connections` so edges can distinguish
      examples such as inverse, prerequisite, part-of, or related-to.
- [ ] Add alias support so term renames can preserve stable downstream lookup
      without breaking generated ids.
- [ ] Add term status metadata such as draft, accepted, deprecated, merged, or
      retired.

## Major Improvements

- [ ] Move the ontology source into a structured format with explicit fields for
      aliases, relation types, provenance, reviewers, and term status while
      continuing to export CSV for spreadsheet users.
- [ ] Publish a browsable static documentation site from `ontology.json`, with
      term pages, tag filters, graph neighborhoods, and archive release notes.
- [ ] Add downstream package exports for Python and JavaScript consumers so
      tools can depend on versioned ontology artifacts rather than scraping repo
      files.
