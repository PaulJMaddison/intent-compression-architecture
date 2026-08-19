# Archive Preservation Policy

## Purpose

This repository is both historical evidence and an executable reference. Maintenance should improve discoverability, reproducibility, correctness and safety **without silently rewriting the historical record** of how ICA evolved toward the Clarity Gateway.

## Content classes

### 1. Frozen historical snapshots

Files under `docs/legacy/` are point-in-time snapshots. Do not modernise their wording, links, claims or terminology in place. If context is needed, add a note in a maintained document that links to the snapshot.

### 2. Published historical artefacts

The proposal PDF/DOCX, architecture artwork and published pilot outputs are provenance-bearing artefacts. If a material error is found, preserve the original and document the correction and its impact rather than replacing history invisibly.

### 3. Maintained reference surfaces

The following may evolve to keep the archive usable:

- root `README.md` and `index.html`
- `EVOLUTION.md`, `ARCHIVE_POLICY.md`, `SECURITY.md`, `CONTRIBUTING.md`
- the offline `ica-core` reference runtime
- schemas, contract validation and tests
- local validation helpers

Changes here should preserve historical behaviour where practical. Where a correctness or security fix changes behaviour, record it in `CHANGELOG.md`.

## Maintenance rules

1. **Preserve provenance.** Do not delete historical meaning merely because current product terminology changed.
2. **No machine-specific truth.** Public archive docs must not depend on a particular developer's local filesystem paths or private workspace layout.
3. **No live dependency by default.** Tests and normal validation remain offline. Live-provider experiments, if ever added, must be explicit opt-ins and must not be required to reproduce the archive.
4. **No secrets or customer data.** Never commit keys, access tokens, production traces, private prompts, customer records or copied credentials.
5. **Contract drift must fail validation.** The portable JSON Schema and executable Pydantic reference model must remain structurally aligned.
6. **Corrections are additive.** If benchmark methodology or a historical claim is corrected, preserve the previous artefact and explain the delta.
7. **Local validation remains canonical.** This is a deliberate historical choice, not an accidental absence of CI.
8. **Non-destructive Git practices.** Archive maintenance should preserve unrelated work and never use destructive repository operations as an automated convenience.

## When changing benchmark material

A benchmark change should document:

- what changed
- whether old numbers are still comparable
- whether the change is methodology, bug fix, data correction, or new experiment
- which artefact represents the historical result
- which artefact represents the corrected/new result

Never replace a published result solely to make the archive look stronger.

## When changing the reference runtime

Prefer changes that strengthen invariants, validation, privacy, portability and failure handling. Avoid redesigning the archived architecture to match a later product unless the goal is explicitly to add a new historical comparison layer.
