# Changelog

> **Status: reference/archive.** This changelog records the historical ICA package and subsequent archive-maintenance work. It is not the release log for the active Clarity Gateway implementation.

## Unreleased — archive hardening

- Reframed the repository as an explicit Clarity Gateway evolution/reference archive rather than relying on local workspace paths for context.
- Preserved the previous long-form README and website as frozen point-in-time snapshots under `docs/legacy/`.
- Added a commit-linked `EVOLUTION.md` and an explicit archive preservation policy.
- Added security, contribution and citation metadata suitable for a public reference repository.
- Aligned the JSON Schema surface with the Pydantic reference contract and added an automated parity check.
- Strengthened schema invariants for blank labels, negative information gain, duplicate candidate IDs and incomplete `ask_clarifier` decisions.
- Hardened provider-response validation and stopped copying raw provider exception text into fallback metadata.
- Fixed the CLI so environment-backed policy thresholds are actually applied instead of only applying `tau`.
- Rejected non-finite threshold values.
- Changed JSONL trace defaults so clarifying-question text is hashed unless raw capture is explicitly enabled.
- Clarified that the built-in redactor is not a production DLP/anonymisation system.

## v1.0.0 — ICA proposal and canonical LLM-derived demo

- Reframed the README so the human problem and core hook appear before package mechanics.
- Added the canonical Elon Musk propaganda example based on real LLM interaction data.
- Updated the mock provider, schema example, and pilot benchmark to use a compression-optimized yes/no definition clarifier.
- Added explicit early-exit silent-failure and screenshot-misuse risk metrics to the evaluation package.
- Regenerated the pilot CSV/Markdown report and proposal DOCX/PDF around the updated metrics and canonical example.
- Added test coverage for the compression-optimized propaganda clarifier.
- Documented that the next proof step is live API-instrumented benchmarking with billed token and latency capture.
- Added a coding-agent task-state compression bridge for applying ICA to long-running agent workflows.
- Added “control plane for intent” positioning for reliable LLM and agentic systems.
- Promoted the agentic/coding-agent use case near the top of the README and proposal framing.

This release used the offline mock provider for package validation. Live provider adapters were intentionally left as a later implementation milestone.

## v0.1.0 — initial `ica-core` package release

- Added a provider-agnostic ICA engine with deterministic policy routing.
- Added Pydantic v2 schemas aligned with the repository clarifier contract.
- Added an offline mock provider for tests, demos, and local validation.
- Added a CLI entrypoint (`ica`) with JSON, dry-run, and local JSONL tracing support.
- Added privacy-conscious trace utilities that hash queries by default.
- Added tests covering policy behavior, schema validation, mock provider behavior, CLI, tracing, config, and engine fallback paths.

Live provider calls were not validated in this release; the provider interface was retained as the extension boundary.
