# Local Validation

> **This validates the historical reference code in this repo.** It does not test the current production Clarity Gateway.

Normal validation is completely offline. It uses the included mock provider, so you do not need an OpenAI, xAI or other API key.

## Quick test

For normal Python changes:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Full archive check

Install the extra packages used by the old benchmark and document tools, then run the validation script:

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
bash scripts/validate_local.sh
```

On Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
.\scripts\validate_local.ps1
```

If you need a particular Python executable, set the `PYTHON` environment variable first.

## What the full check does

It checks that:

- the Python files compile
- the example JSON matches the JSON Schema
- the JSON Schema and Python model still describe the same fields
- all tests pass
- the Python package builds
- the command-line tool starts and returns valid output
- the example command-line demo works
- the old pilot report can still be rebuilt

## Dependency files

`requirements.txt` contains the extra packages used by the archive's benchmark and document-building tools.

`requirements.lock` pins versions of those same tools for a closer replay of the historical setup.

The actual `ica-core` package and development dependencies are defined in `pyproject.toml`.

## Live API calls

There are no live provider adapters in this archive.

If a live adapter is ever added for an experiment, normal validation must stay offline. Any live test must require a clear opt-in, for example `KYNTIC_RUN_E2E_TESTS=1`.

## GitHub Actions

GitHub Actions are intentionally not used in this repo. The normal validation path is local and offline.
