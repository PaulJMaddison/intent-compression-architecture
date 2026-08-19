# Changelog

> **Historical reference.** This records changes to the old ICA package and this reference archive. It is not the release history of the current Clarity Gateway product.

## Unreleased — documentation made easier to understand

- Rewrote the maintained Markdown documentation in simpler English.
- Kept technical names and formulas only where they are needed for accuracy or for running the code.
- Simplified the ICA history, evaluation guide, security notes, contribution guide, local validation guide and UCL example.
- Left `docs/legacy/` and the generated historical pilot results unchanged so the original record is preserved.

## Archive hardening — August 2026

- Made it clear that this repo is a historical record of the ideas that led towards Clarity Gateway, not the live product.
- Preserved the previous long README and website under `docs/legacy/`.
- Added `EVOLUTION.md` to explain the history using links to the original commits.
- Added archive, security, contribution and citation guidance.
- Made sure the JSON Schema and Python Pydantic model describe the same fields, and added an automatic check for future drift.
- Added stronger validation for blank labels, negative information-gain values, duplicate clarification IDs and incomplete `ask_clarifier` decisions.
- Improved provider-response validation and stopped raw provider exception text being copied into fallback metadata.
- Fixed the command-line tool so environment settings for ambiguity and risk thresholds are actually used.
- Rejected invalid non-finite threshold values.
- Changed trace defaults so clarification text is hashed unless raw capture is explicitly requested.
- Made it clear that the simple built-in redactor is not a production anonymisation or data-loss-prevention system.
- Kept GitHub Actions absent; local offline validation remains the normal test path.

## v1.0.0 — ICA proposal and main demo

- Reworked the original README so the human problem appeared before the package details.
- Added the main "propaganda" ambiguity example based on a real LLM interaction.
- Updated the mock provider, schema example and pilot benchmark around a shorter definition question.
- Added measurements for users leaving before a misunderstanding is discovered and for first answers being reused as misleading screenshots or quotes.
- Rebuilt the pilot CSV/Markdown report and proposal DOCX/PDF with the updated example and measurements.
- Added tests for the shorter clarification question.
- Documented that stronger evidence would require live API benchmarking with real token and latency measurements.
- Extended the idea from chat clarification to keeping task state clear for coding agents.
- Described ICA as a control layer for keeping user intent clear before an AI answers or acts.

This release still used the offline mock provider for validation. Live provider adapters were left for later work.

## v0.1.0 — first `ica-core` package

- Added a provider-independent ICA engine with ordinary Python code making the final routing decision.
- Added Pydantic v2 models for the structured decision format.
- Added an offline mock provider for tests and demos.
- Added the `ica` command-line tool with JSON output, dry-run mode and local JSONL tracing.
- Added private-by-default trace helpers that hash user queries.
- Added tests for routing, schema validation, the mock provider, CLI, tracing, configuration and fallback paths.

Live provider calls were not part of this release. The provider interface was kept so adapters could be added later.
