# Local Validation

> **Status: reference/archive.** These commands validate the archived Python mock/reference package in this repository. For the active KynticAI Clarity Engine / ICA implementation, use `C:\Kyntic\kynticai-intent-compression-architecture`.

Routine local development is offline and uses the mock ICA provider. Do not add live provider, hosted API, or paid-service calls to the default validation path.

## Safe Default

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

The validation helpers compile Python files, validate the JSON schema/example, run `pytest`, build the package, run CLI smoke checks with `--provider mock`, run the example CLI demo, and rebuild the pilot report. They do not require `OPENAI_API_KEY`, `XAI_API_KEY`, or another live provider credential.

## Explicit Proof Paths

No live provider adapters are bundled in this repository today. If one is added later, keep the default path on `--provider mock` and require `KYNTIC_RUN_E2E_TESTS=1` or a provider-specific opt-in before any live API call.
