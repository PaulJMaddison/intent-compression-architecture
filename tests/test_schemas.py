import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ica_core.schemas import (
    CandidateClarifier,
    ClarifierOutput,
    Decision,
    entropy_bits,
)


def test_repo_schema_example_validates_against_model() -> None:
    example_path = Path(__file__).resolve().parents[1] / "spec" / "clarifier_output.example.json"
    data = json.loads(example_path.read_text(encoding="utf-8"))

    output = ClarifierOutput.model_validate(data)

    assert output.decision == "ask_clarifier"
    assert output.best_candidate() is not None
    assert output.best_candidate().id == "q1"
    assert output.tau == 0.15


def test_selected_clarifier_must_reference_candidate() -> None:
    with pytest.raises(ValidationError):
        ClarifierOutput.model_validate(
            {
                "ambiguity_score": 0.5,
                "risk_score": 0.1,
                "intent_entropy_bits": 0.0,
                "intent_hypotheses": [
                    {
                        "label": "plain",
                        "probability": 1.0,
                        "answer_delta_if_true": "low",
                    }
                ],
                "candidate_clarifiers": [],
                "decision": "ask_clarifier",
                "selected_clarifier_id": "missing",
                "answer_constraints": [],
            }
        )


def test_entropy_bits_normalizes_distribution() -> None:
    assert round(entropy_bits([2, 2]), 3) == 1.0


def test_schema_allows_practical_package_extensions() -> None:
    output = ClarifierOutput.model_validate(
        {
            "query_id": "request-1",
            "trace_id": "trace-1",
            "ambiguity_score": 0.4,
            "risk_score": 0.1,
            "intent_entropy_bits": 0.8,
            "intent_hypotheses": [
                {
                    "label": "plain",
                    "probability": 1.0,
                    "answer_delta_if_true": "low",
                    "metadata": {"source": "test"},
                }
            ],
            "candidate_clarifiers": [
                {
                    "id": "q1",
                    "question": "Which output format do you want?",
                    "expected_information_gain_bits": 0.4,
                    "expected_utility": 0.2,
                    "estimated_cost_tokens": 10,
                    "estimated_token_savings": 30,
                }
            ],
            "decision": "ask_clarifier",
            "selected_clarifier_id": "q1",
            "decision_threshold": 0.15,
            "answer_constraints": [" concise "],
            "estimated_token_savings": 30,
            "metadata": {"domain": "test", "offline": True},
            "rationale": "Useful clarifier.",
        }
    )

    assert output.trace_id == "trace-1"
    assert output.clarifying_question == "Which output format do you want?"
    assert output.answer_constraints == ["concise"]
    assert output.selected_candidate() == output.candidate_clarifiers[0]


def test_blank_candidate_question_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CandidateClarifier(
            id="q1",
            question=" ",
            expected_information_gain_bits=0.1,
            expected_utility=0.1,
            estimated_cost_tokens=1,
        )


def test_decision_enum_values_match_repo_contract() -> None:
    assert [decision.value for decision in Decision] == [
        "answer_direct",
        "ask_clarifier",
        "premise_check",
        "refuse_redirect",
    ]
