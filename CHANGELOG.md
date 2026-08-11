# Changelog

> **Status: reference/archive.** This changelog records the archived Python mock/reference package and proposal artifact history. Current Clarity/ICA implementation history lives in `C:\Kyntic\kynticai-clarity-gateway`.

## v1.0.0 - ICA proposal and canonical LLM-derived demo

- Reframed the README so the human problem and core hook appear before package mechanics.
- Added the canonical Elon Musk propaganda example based on real LLM interaction data.
- Updated the mock provider, schema example, and pilot benchmark to use a compression-optimized yes/no definition clarifier.
- Added explicit early-exit silent-failure and screenshot-misuse risk metrics to the evaluation package.
- Regenerated the pilot CSV/Markdown report and proposal DOCX/PDF around the updated metrics and canonical example.
- Added test coverage for the compression-optimized propaganda clarifier.
- Documented that the next proof step is live API-instrumented benchmarking with billed token and latency capture.
- Added a coding-agent task-state compression bridge for applying ICA to long-running agent workflows.
- Added "control plane for intent" positioning for reliable LLM and agentic systems.
- Promoted the agentic/coding-agent use case near the top of the README and proposal framing.
- Rewrote the README opening so ICA leads as an intent-control architecture rather than a cautious clarification feature.
- Added a standalone "Agentic & Coding Workflows" section and elevated the agentic claim in the claim ladder.

This release still uses the offline mock provider for package validation. Live OpenAI/xAI provider adapters are intentionally left as the next implementation milestone.

## v0.1.0 - Initial `ica-core` package release

- Added a provider-agnostic ICA engine with deterministic policy routing.
- Added Pydantic v2 schemas aligned with the repository clarifier contract.
- Added an offline mock provider for tests, demos, and local validation.
- Added a CLI entrypoint (`ica`) with JSON, dry-run, and local JSONL tracing support.
- Added privacy-conscious trace utilities that hash queries by default.
- Added tests covering policy behavior, schema validation, mock provider behavior, CLI, tracing, config, and engine fallback paths.

Live OpenAI/xAI provider calls are not validated in this release because no real API key is configured. Provider adapters can be added later through the structured provider interface.
