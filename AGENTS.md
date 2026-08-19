# AGENTS.md

## Repository role

This repository is a **reference/archive** for Intent Compression Architecture (ICA), preserving the design, benchmark material and offline Python implementation that form part of the engineering lineage toward KynticAI Clarity Gateway.

It is not the active product source of truth. Do not infer current product behaviour from this archive or add private/local workspace paths as public routing instructions.

## Preservation rules

- Read `ARCHIVE_POLICY.md` before making broad documentation or artefact changes.
- Treat `docs/legacy/` as frozen point-in-time snapshots.
- Preserve published proposal and benchmark provenance; corrections should be additive and explained.
- Keep the root README, evolution map, runtime, schema and validation helpers maintainable.

## Build and test

Core development:

- `python -m pip install -e ".[dev]"`
- `python -m pytest`

Full archive validation:

- install `requirements.txt` (or `requirements.lock` for the pinned artefact toolchain)
- install `.[dev]`
- run `bash scripts/validate_local.sh` or `.\scripts\validate_local.ps1`

The validation path compiles Python, validates the JSON Schema and example, checks schema/Pydantic parity, runs tests, builds the package, exercises CLI smoke paths and rebuilds the pilot report.

## External proof boundary

- Do not add live OpenAI, xAI, hosted API, or paid-provider calls to default validation.
- No live provider adapter is bundled in the archive.
- Any future live proof must be explicit opt-in and must never require real credentials for routine validation.

## Privacy and secrets

- Never commit API keys, `.env` secrets, production traces, private prompts or customer data.
- Preserve privacy-safe trace defaults. Raw query or clarifier capture must remain explicit opt-in behaviour.
- Treat the built-in redactor as a debugging convenience, not a production DLP system.

## Git safety — mandatory

- Work only on the branch the user provides or explicitly authorises. Preserve unrelated changes.
- Never run `git stash`, `git stash drop`, `git reset --hard`, `git clean`, branch deletion, force checkout, force push, or another destructive Git operation unless the user explicitly directs that exact action.
- If Git state prevents safe continuation, report it instead of autonomously destroying or reconstructing work.
- Never recreate lost uncommitted code from conversational memory.

## Change quality

- Fix issues rather than merely documenting them when a safe correction is possible.
- Add boundary, malformed-input, state, failure-path and privacy tests for runtime changes.
- Keep `spec/clarifier_output.schema.json` and `ClarifierOutput` structurally aligned.
- Record meaningful archive/runtime changes in `CHANGELOG.md`.
