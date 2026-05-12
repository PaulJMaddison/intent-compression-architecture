# Changelog

## v0.1.0 - Initial `ica-core` package release

- Added a provider-agnostic ICA engine with deterministic policy routing.
- Added Pydantic v2 schemas aligned with the repository clarifier contract.
- Added an offline mock provider for tests, demos, and local validation.
- Added a CLI entrypoint (`ica`) with JSON, dry-run, and local JSONL tracing support.
- Added privacy-conscious trace utilities that hash queries by default.
- Added tests covering policy behavior, schema validation, mock provider behavior, CLI, tracing, config, and engine fallback paths.

Live OpenAI/xAI provider calls are not validated in this release because no real API key is configured. Provider adapters can be added later through the structured provider interface.
