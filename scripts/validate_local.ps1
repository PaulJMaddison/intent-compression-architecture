$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$pythonCmd = if ($env:PYTHON) { $env:PYTHON } else { "python" }

Set-Location $repoRoot

& $pythonCmd -m compileall -q src tests eval examples scripts
& $pythonCmd scripts/validate_schema.py
& $pythonCmd scripts/validate_contract_parity.py
& $pythonCmd -m pytest
& $pythonCmd -m build
& $pythonCmd -m ica_core.cli --help
& $pythonCmd -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --dry-run
& $pythonCmd -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --json
& $pythonCmd examples/cli_demo.py
& $pythonCmd eval/build_pilot_report.py
