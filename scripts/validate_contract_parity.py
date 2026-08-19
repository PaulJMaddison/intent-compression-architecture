"""Validate that the hand-authored ICA JSON Schema matches the Pydantic contract."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ica_core.schemas import ClarifierOutput


def _assert_same(label: str, left: set[str], right: set[str]) -> None:
    if left == right:
        return
    missing = sorted(right - left)
    extra = sorted(left - right)
    raise SystemExit(
        f"{label} drift detected; missing_from_spec={missing}, extra_in_spec={extra}"
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    spec = json.loads(
        (repo_root / "spec" / "clarifier_output.schema.json").read_text(encoding="utf-8")
    )
    example = json.loads(
        (repo_root / "spec" / "clarifier_output.example.json").read_text(encoding="utf-8")
    )
    model_schema = ClarifierOutput.model_json_schema()

    Draft202012Validator.check_schema(spec)
    Draft202012Validator(spec).validate(example)
    ClarifierOutput.model_validate(example)

    _assert_same("top-level property", set(spec["properties"]), set(model_schema["properties"]))
    _assert_same("top-level required-field", set(spec["required"]), set(model_schema["required"]))

    nested = {
        "intent_hypotheses": "IntentHypothesis",
        "candidate_clarifiers": "CandidateClarifier",
    }
    for spec_property, model_definition in nested.items():
        spec_item = spec["properties"][spec_property]["items"]
        model_item = model_schema["$defs"][model_definition]
        _assert_same(
            f"{model_definition} property",
            set(spec_item["properties"]),
            set(model_item["properties"]),
        )
        _assert_same(
            f"{model_definition} required-field",
            set(spec_item["required"]),
            set(model_item["required"]),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
