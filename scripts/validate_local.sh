#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
python_cmd="${PYTHON:-python}"

cd "$repo_root"

"$python_cmd" -m py_compile eval/build_pilot_report.py scripts/build_repo_artifacts.py
"$python_cmd" -m jsonschema spec/clarifier_output.schema.json -i spec/clarifier_output.example.json
"$python_cmd" eval/build_pilot_report.py
