# Contributing

Contributions are welcome when they improve the archive without rewriting its history.

## Good contributions

- correctness and security fixes to the offline reference runtime
- stronger contract validation and edge-case tests
- portability fixes
- clearer provenance and evolution documentation
- reproducibility improvements
- explicit corrections to historical methodology with the original preserved

## Please avoid

- silently modernising frozen historical snapshots
- presenting the archive as the current Clarity Gateway implementation
- adding a live API requirement to the default test path
- committing secrets, private data or real production traces
- replacing historical benchmark output solely because a newer result looks better

## Validate changes

Core package:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Full archive:

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
bash scripts/validate_local.sh
```

Windows PowerShell:

```powershell
.\scripts\validate_local.ps1
```

Contract changes must also keep `spec/clarifier_output.schema.json` and the Pydantic model aligned; the full validation path runs `scripts/validate_contract_parity.py`.
