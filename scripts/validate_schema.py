"""Validate the ICA clarifier example against the repository JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "spec" / "clarifier_output.schema.json"
    example_path = repo_root / "spec" / "clarifier_output.example.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
