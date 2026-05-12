$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$pythonCmd = if ($env:PYTHON) { $env:PYTHON } else { "python" }

Set-Location $repoRoot

$packageFiles = @(
    "src/ica_core/__init__.py",
    "src/ica_core/config.py",
    "src/ica_core/schemas.py",
    "src/ica_core/policy.py",
    "src/ica_core/core.py",
    "src/ica_core/tracing.py",
    "src/ica_core/cli.py",
    "src/ica_core/providers/__init__.py",
    "src/ica_core/providers/base.py",
    "src/ica_core/providers/mock.py",
    "examples/cli_demo.py"
)

& $pythonCmd -m py_compile eval/build_pilot_report.py scripts/build_repo_artifacts.py scripts/validate_schema.py @packageFiles
& $pythonCmd scripts/validate_schema.py
& $pythonCmd -m pytest
& $pythonCmd -m build
& $pythonCmd -m ica_core.cli --help
& $pythonCmd -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --dry-run
& $pythonCmd -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --json
& $pythonCmd examples/cli_demo.py
& $pythonCmd eval/build_pilot_report.py
