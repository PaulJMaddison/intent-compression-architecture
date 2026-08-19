import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ica_core.cli import main
from ica_core.config import ICAConfig
from ica_core.core import IntentCompressor, StructuredOutputValidationError
from ica_core.schemas import CandidateClarifier, ClarifierOutput, entropy_bits
from ica_core.tracing import JSONLTraceSink, query_hash


def base_payload(**overrides):
    payload = {
        "ambiguity_score": 0.8,
        "risk_score": 0.1,
        "intent_entropy_bits": 1.0,
        "intent_hypotheses": [
            {"label": "speed", "probability": 0.5, "answer_delta_if_true": "high"},
            {"label": "cost", "probability": 0.5, "answer_delta_if_true": "high"},
        ],
        "candidate_clarifiers": [{
            "id": "q1", "question": "Which constraint matters most?",
            "expected_information_gain_bits": 0.5,
            "expected_utility": 0.3, "estimated_cost_tokens": 8,
        }],
        "decision": "answer_direct", "answer_constraints": [],
    }
    payload.update(overrides)
    return payload


def test_blank_hypothesis_label_is_rejected() -> None:
    payload = base_payload()
    payload["intent_hypotheses"][0]["label"] = "   "
    with pytest.raises(ValidationError):
        ClarifierOutput.model_validate(payload)


def test_whitespace_rationale_normalizes_to_empty_string_not_none() -> None:
    output = ClarifierOutput.model_validate(base_payload(rationale="   "))
    assert output.rationale == ""
    assert isinstance(output.rationale, str)


def test_negative_information_gain_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CandidateClarifier(
            id="q1", question="Which?", expected_information_gain_bits=-0.01,
            expected_utility=0.1, estimated_cost_tokens=1,
        )


def test_duplicate_candidate_ids_are_rejected() -> None:
    payload = base_payload()
    payload["candidate_clarifiers"].append(dict(payload["candidate_clarifiers"][0]))
    with pytest.raises(ValidationError):
        ClarifierOutput.model_validate(payload)


def test_ask_clarifier_requires_selected_candidate() -> None:
    with pytest.raises(ValidationError):
        ClarifierOutput.model_validate(base_payload(decision="ask_clarifier"))


def test_ask_clarifier_populates_selected_question() -> None:
    output = ClarifierOutput.model_validate(
        base_payload(decision="ask_clarifier", selected_clarifier_id="q1")
    )
    assert output.clarifying_question == "Which constraint matters most?"


def test_entropy_rejects_invalid_probabilities() -> None:
    with pytest.raises(ValueError):
        entropy_bits([0.8, -0.2])
    with pytest.raises(ValueError):
        entropy_bits([0.5, float("inf")])


class SecretFailProvider:
    name = "secret-fail"

    def generate_structured(self, request):
        del request
        raise RuntimeError("Authorization failed: api_key=do-not-copy")


def test_non_strict_fallback_does_not_copy_provider_exception_text() -> None:
    decision = IntentCompressor(provider=SecretFailProvider(), strict=False).process(
        "Make this API faster."
    )
    serialized = json.dumps(decision.model_dump(mode="json"))
    assert "do-not-copy" not in serialized
    assert decision.metadata["fallback_error_type"] == "RuntimeError"


class WrongResponseProvider:
    name = "wrong-response"

    def generate_structured(self, request):
        del request
        return {"not": "ProviderResponse"}


def test_wrong_provider_response_type_is_contract_error_in_strict_mode() -> None:
    with pytest.raises(StructuredOutputValidationError):
        IntentCompressor(provider=WrongResponseProvider()).process("hello")


def test_wrong_provider_response_type_falls_back_in_non_strict_mode() -> None:
    decision = IntentCompressor(provider=WrongResponseProvider(), strict=False).process("hello")
    assert decision.metadata["fallback_reason"] == "validation_error"
    assert decision.metadata["fallback_error_type"] == "TypeError"


def test_jsonl_trace_hashes_clarifier_text_by_default(tmp_path) -> None:
    path = tmp_path / "trace.jsonl"
    sink = JSONLTraceSink(path)
    sink.record("decision", {"clarifying_question": "What account do you mean?"})
    row = json.loads(path.read_text(encoding="utf-8").strip())
    assert "clarifying_question" not in row
    assert row["clarifying_question_hash"] == query_hash("What account do you mean?")


def test_jsonl_trace_can_opt_in_to_raw_clarifier_text(tmp_path) -> None:
    path = tmp_path / "trace.jsonl"
    sink = JSONLTraceSink(path, include_clarifier_text=True)
    sink.record("decision", {"clarifying_question": "What account do you mean?"})
    row = json.loads(path.read_text(encoding="utf-8").strip())
    assert row["clarifying_question"] == "What account do you mean?"
    assert "clarifying_question_hash" not in row


def test_cli_honors_environment_min_ambiguity_threshold(monkeypatch, capsys) -> None:
    monkeypatch.setenv("ICA_MIN_AMBIGUITY_TO_ASK", "0.9")
    code = main(["Make this API faster."])
    captured = capsys.readouterr()
    assert code == 0
    assert "decision: answer_direct" in captured.out


def test_config_rejects_non_finite_tau(monkeypatch) -> None:
    monkeypatch.setenv("ICA_TAU", "nan")
    with pytest.raises(ValidationError):
        ICAConfig()


def test_cli_rejects_non_finite_tau() -> None:
    with pytest.raises(SystemExit):
        main(["--tau", "nan", "hello"])


def test_cli_trace_does_not_store_raw_clarifier_by_default(tmp_path, capsys) -> None:
    path = tmp_path / "trace.jsonl"
    assert main(["--trace", "--trace-path", str(path), "Make this API faster."]) == 0
    capsys.readouterr()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    decision = rows[-1]
    assert "clarifying_question" not in decision
    assert "clarifying_question_hash" in decision


def test_canonical_example_validates_against_json_schema_and_model() -> None:
    root = Path(__file__).parents[1]
    schema = json.loads(
        (root / "spec" / "clarifier_output.schema.json").read_text(encoding="utf-8")
    )
    example = json.loads(
        (root / "spec" / "clarifier_output.example.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(example)
    output = ClarifierOutput.model_validate(example)
    assert output.selected_clarifier_id == "q1"
