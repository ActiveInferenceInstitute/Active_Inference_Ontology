# Archive and Provenance

The repository keeps previous ontology releases under `Archived versions/`.
Those files are source evidence and should not be rewritten casually.

The root `releases.json` file provides machine-readable release metadata across
the current release and archived snapshots.

## Current Archive Layout

| Path | Contents |
| --- | --- |
| `Archived versions/v1 (terms list)/` | Early terms-list candidate files and PDF supplements. |
| `Archived versions/v2 (T2.D1.L1.E1)/` | Version 2 spreadsheet and packaged release files. |
| `Archived versions/v3/` | Version 3 spreadsheet, archive, definitions TSV, and translation TSV. |
| `Archived versions/v4 (12-12-2022 snapshot)/` | Version 4 CSV snapshots for definitions/examples/connections and terms/translations. |

The current root CSV is version 5 material and is not stored under the archive
folder.

## Provenance Rules

- Treat archive files as immutable historical records.
- Add new archive folders for new release snapshots rather than overwriting old
  folders.
- Keep original filenames where possible because they carry release context.
- Document any format conversion used to create a new archive snapshot.
- Do not manually change `ontology.json` to represent archived data; create a
  separate export if archived JSON is needed.
- Keep `releases.json` synchronized when adding a new release snapshot.

## Recommended New Release Snapshot

For a future version, use a folder name that includes both version and date:

```text
Archived versions/v6 (YYYY-MM-DD snapshot)/
```

Include:

- release CSV or spreadsheet source;
- any translation tables;
- any packaged release artifact;
- a short `README.md` explaining source, date, and differences from the prior
  release.

## Release Manifest

`releases.json` records:

- version;
- label;
- status;
- date when known;
- path;
- source or generated files;
- counts for the current JSON-backed release;
- provenance notes.

Archive folders also carry local `README.md` files for human review.
