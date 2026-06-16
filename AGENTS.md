# AGENTS.md

## Project Overview

Intent Compression Architecture is a Python reference implementation and documentation package for an offline clarification/control-plane policy. The default local provider is the deterministic mock provider.

## Build/Test Commands

- Local validation: `python -m pip install -r requirements.txt`, `python -m pip install -e ".[dev]"`, then `.\scripts\validate_local.ps1`.
- Manual safe checks: `python scripts\validate_schema.py`, `python -m pytest`, `python -m build`, and CLI smoke checks with `--provider mock`.
- Laptop local-folder rule: before running tests on this machine, check `C:\Kyntic\UCL-local-aidocs\LOCAL_LAPTOP_TEST_COMMANDS.md` and use the nearest safe command for the folder touched; docs-only changes can use `git diff --check`.

## External Proof Boundary

- Do not add live OpenAI, xAI, hosted API, or paid-provider calls to default validation.
- No live provider adapter is bundled today. Any future live API proof must require explicit opt-in, normally `KYNTIC_RUN_E2E_TESTS=1`, and must not require real provider credentials by default.

## State/Update Expectations

- Check `git status` before editing and preserve unrelated local changes.
- Keep README, proposal artifacts, schema examples, and validation docs aligned when changing architecture claims.
- Record commands run, skipped checks, and any residual risk in the relevant local work log when this repo is part of broader Kyntic workspace work.
