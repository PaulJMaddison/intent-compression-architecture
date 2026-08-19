#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
python_cmd="${PYTHON:-python}"

cd "$repo_root"

"$python_cmd" -m compileall -q src tests eval examples scripts
"$python_cmd" scripts/validate_schema.py
"$python_cmd" scripts/validate_contract_parity.py
"$python_cmd" -m pytest
"$python_cmd" -m build
"$python_cmd" -m ica_core.cli --help
"$python_cmd" -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --dry-run
"$python_cmd" -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --json
"$python_cmd" examples/cli_demo.py
"$python_cmd" eval/build_pilot_report.py
