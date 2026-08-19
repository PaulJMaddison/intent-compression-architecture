# Contributing

Contributions are welcome if they make this historical reference easier to understand, safer to run or more accurate **without rewriting its history**.

## Good changes

Examples include:

- fixing bugs or security problems in the offline reference code
- adding useful edge-case and failure tests
- making the code work more reliably across different machines
- making documentation easier to understand
- improving local reproducibility
- correcting an old method or result while keeping the original historical version

## Please do not

- rewrite files in `docs/legacy/`
- present this repo as the current Clarity Gateway product
- make live or paid API calls part of normal testing
- commit secrets, private data or real production traces
- silently replace an old benchmark result because a newer result looks better

## Run the tests

For normal Python changes:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

For the full archive check:

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
bash scripts/validate_local.sh
```

On Windows PowerShell:

```powershell
.\scripts\validate_local.ps1
```

## If you change the decision contract

The JSON Schema in `spec/clarifier_output.schema.json` and the Python Pydantic model must stay in sync.

The full validation script checks this automatically with `scripts/validate_contract_parity.py`.
