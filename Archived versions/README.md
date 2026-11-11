# Archived versions

Immutable historical source evidence for the Active Inference Ontology, kept for
provenance and hash checking. These files are **never rewritten or edited in
place**; the current release is the v2 structured source at
[`../ontology.source.json`](../ontology.source.json), and the `releases.json`
manifest records their hashes.

| Archive | Snapshot | Contents |
| --- | --- | --- |
| [v1 (terms list)](<v1 (terms list)/README.md>) | v1 terms-list candidate (no date in folder name) | XLSX source and two PDF supplements. |
| [v2 (T2.D1.L1.E1)](<v2 (T2.D1.L1.E1)/README.md>) | v2 `T2.D1.L1.E1` snapshot | XLSX, ODS, and packaged ZIP. |
| [v3](v3/README.md) | v3 (no date in folder name) | XLSX, ODS, ZIP, and definitions/translation TSVs. |
| [v4 (12-12-2022 snapshot)](<v4 (12-12-2022 snapshot)/README.md>) | 12 December 2022 | Two exported CSV views. |

Each archive folder carries its own `README.md` with a file table and provenance
notes. To see how these versions relate to the current release, use
`python3 scripts/ontology.py diff OLD.json NEW.json` and read
[`../docs/archive-and-provenance.md`](../docs/archive-and-provenance.md).
