#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
python_cmd="${PYTHON:-python}"

cd "$repo_root"

"$python_cmd" -m py_compile \
  eval/build_pilot_report.py \
  scripts/build_repo_artifacts.py \
  scripts/validate_schema.py \
  src/ica_core/__init__.py \
  src/ica_core/config.py \
  src/ica_core/schemas.py \
  src/ica_core/policy.py \
  src/ica_core/core.py \
  src/ica_core/tracing.py \
  src/ica_core/cli.py \
  src/ica_core/providers/__init__.py \
  src/ica_core/providers/base.py \
  src/ica_core/providers/mock.py \
  examples/cli_demo.py
"$python_cmd" scripts/validate_schema.py
"$python_cmd" -m pytest
"$python_cmd" -m build
"$python_cmd" -m ica_core.cli --help
"$python_cmd" -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --dry-run
"$python_cmd" -m ica_core.cli "Does Elon Musk post right-wing propaganda?" --provider mock --json
"$python_cmd" examples/cli_demo.py
"$python_cmd" eval/build_pilot_report.py
