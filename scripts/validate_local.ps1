$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$pythonCmd = if ($env:PYTHON) { $env:PYTHON } else { "python" }

Set-Location $repoRoot

& $pythonCmd -m py_compile eval/build_pilot_report.py scripts/build_repo_artifacts.py
& $pythonCmd -m jsonschema spec/clarifier_output.schema.json -i spec/clarifier_output.example.json
& $pythonCmd eval/build_pilot_report.py
