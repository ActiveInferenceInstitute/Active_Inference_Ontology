# Future Curation: Typed Relations and Alias-Aware Mention Extraction

**Status:** Proposal for curator / domain review — NOT implemented.
**Owner:** Active Inference Institute (semantic curation lead + release maintainer).
**Last updated:** 2026-08-01

## Purpose

This document is the deliberately-deferred design for raising the ontology's relation
expressiveness. It is intentionally **not** merged as a code change: any of the options
below changes the curated graph (edge counts and meaning), so it must be approved and
_reviewed_ by a domain curator before it touches `ontology.source.json`. Nothing here is
auto-applied.

## Current contract (what exists and must not regress)

- `scripts/ontology.py::mention_relations` creates a `mentions` edge for every **exact,
  case-insensitive, word-boundary** occurrence of another term's canonical label in the
  owning term's `connectionsText`.
- It infers **nothing else**: no plurals/derivatives, no aliases, no `broader` /
  `narrower` / `causes` / `related`, etc. This is the conservative migration contract
  documented in `docs/manuscript/05_discussion.md` and `docs/source-data-contract.md`.
- Stronger relation types are already representable in the v2 schema
  (`relation_types` in `ontology.toml`) but are only added deliberately.

## Option A — Alias-aware mention pass (codified, low-risk)

**What:** extend `mention_relations` to also match each term's curated `aliases`, still
word-boundary and case-insensitive, still emitting only `mentions`.

**Why it matters:** today an alias like "FEP" for "Free Energy Principle" produces no edge
even when it is the exact phrase used in another term's connections text. Aliases were
already curated as non-canonical labels in the source, so matching them is a mechanical
completion rather than a semantic invention.

**Risks / controls:**
- Alias collisions across terms are already rejected by `validate_source`; the pass must
  run before that guarantee so a shared alias does not become a spurious multi-target edge
  (dedupe to one `mentions` edge per unique target).
- Any alias that casefolds to another term's canonical label must be skipped to avoid
  doubling.
- This **changes edge counts** (currently 238). Requires regeneration of
  `ontology.json`, CSV, site, manuscript variables/figures, and `releases.json` counts via
  `sync-manifest`, plus a release-note. Must not be merged as a silent change.

## Option B — Reviewed native typed-relation curation

**What:** curators add explicit `related` / `part_of` / `broader` / `narrower` /
`prerequisite` / `contrasts` / `causes` / `inverse` edges directly in
`ontology.source.json`, each with provenance and a regression test.

**Why it matters:** the manuscript's central claim is that free-text connections are
preserved as auditable `mentions` "without automatic semantic strengthening." Native
typed relations are the reviewed path to real semantics.

**Risks / controls:**
- Every edge is human-reviewed; the validator already enforces known targets, known types,
  no self-loops, and no duplicates.
- Edges must carry a justification in the claim ledger or a curation note so provenance is
  preserved; `diff` already reports `relationChanges`.

## Recommendation

Pursue **Option A** first (it is mechanical, within the existing conservative contract,
reversible, and directly addresses the documented gap), then layer **Option B** edges by
curator review. Before either lands:

1. Approve this proposal (owner + curator sign-off).
2. Implement `mention_relations` alias support with the regression tests above.
3. `sync-manifest`; regenerate all artifacts; bump release notes; run the full gate
   (`ontology.py validate --strict`, full test suite, manuscript `validate --strict`).
4. Record the count change in `docs/version-diff.md`.

The repository's current release (v5; 429 terms, 238 `mentions` edges) remains the stable
canonical boundary until a curator-approved release is produced.
