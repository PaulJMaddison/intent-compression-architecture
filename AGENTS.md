# AGENTS.md

## What this repo is

This is a **historical reference repo** for Intent Compression Architecture (ICA), one of the ideas that led to KynticAI Clarity Gateway.

It is **not** the current Clarity Gateway code. Do not use this repo as proof of how the live product works today.

## Before changing anything

- Read `ARCHIVE_POLICY.md` before making large changes.
- Do not edit files in `docs/legacy/`. They are frozen copies of the original documentation.
- Do not silently replace old benchmark results or published design files.
- Keep the README, tests, schema and validation scripts easy to use.

## Build and test

For normal Python changes:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

For a full archive check:

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
bash scripts/validate_local.sh
```

On Windows PowerShell:

```powershell
.\scripts\validate_local.ps1
```

The full check makes sure the Python files compile, the JSON contract is valid, the JSON contract still matches the Python model, the tests pass, the package builds, the command-line examples work and the pilot report can still be rebuilt.

## Keep normal testing offline

- Do not make OpenAI, xAI or other paid/live API calls part of normal testing.
- The included provider is an offline mock provider.
- Any future live test must be clearly optional and must never require real credentials for routine validation.
- GitHub Actions are intentionally not used for this archive. Local validation is the normal check.

## Secrets and private data

- Never commit API keys, tokens, `.env` secrets, private prompts, customer data or production traces.
- Keep query and clarification text private by default in traces.
- The built-in text redactor is only a simple debugging helper. It is not a full data-loss-prevention or anonymisation system.

## Git safety

- Work only on the branch the user has asked you to use.
- Preserve unrelated work.
- Do not use destructive Git commands such as `git reset --hard`, `git clean`, forced checkout, branch deletion or force push unless the user explicitly asks for that exact action.
- If Git state is unsafe or unclear, report it instead of trying to destroy or recreate work.
- Never recreate lost uncommitted code from memory.

## Quality rules

- Fix problems when it is safe to do so instead of only writing them down.
- Add tests for bad input, edge cases, failures, state changes and privacy behaviour when runtime code changes.
- Keep `spec/clarifier_output.schema.json` and the Python `ClarifierOutput` model in sync.
- Record important changes in `CHANGELOG.md`.
