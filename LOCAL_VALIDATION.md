# Local Validation

> **Status: reference/archive.** These commands validate the offline Python reference package and reproducibility artefacts preserved in this repository. They are not a validation procedure for the active Clarity Gateway product.

Routine validation is offline and uses the deterministic mock provider. No real provider key is needed.

## Core package

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Full archive validation

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
bash scripts/validate_local.sh
```

PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
.\scripts\validate_local.ps1
```

Set `PYTHON` first if a specific interpreter should be used.

The full helpers:

- compile Python sources and tooling
- validate the JSON Schema and canonical example
- verify structural parity between the hand-authored schema and Pydantic model
- run `pytest`
- build the Python package
- smoke-test CLI help, dry-run and JSON output
- run the example CLI
- rebuild the pilot report

## Dependency note

`requirements.txt` is the intentionally loose dependency set for archive artefact/evaluation tooling. `requirements.lock` pins that same toolchain for a closer historical replay. Neither file is a complete resolver lock for `ica-core` plus its `.[dev]` dependencies; those dependencies are declared in `pyproject.toml`.

## Live proof boundary

No live provider adapters are bundled. If one is ever added for historical experimentation, default validation must remain on the offline provider and any live call must require an explicit opt-in such as `KYNTIC_RUN_E2E_TESTS=1`.
