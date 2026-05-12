import pytest

from ica_core.core import (
    IntentCompressor,
    StructuredOutputValidationError,
)
from ica_core.policy import PolicyConfig
from ica_core.providers.mock import MockIntentProvider
from ica_core.schemas import Decision


def _bad_policy_payload() -> dict:
    return {
        "trace_id": "provider-trace",
        "ambiguity_score": 0.8,
        "risk_score": 0.1,
        "intent_entropy_bits": 1.0,
        "intent_hypotheses": [
            {
                "label": "speed",
                "probability": 0.5,
                "answer_delta_if_true": "high",
            },
            {
                "label": "cost",
                "probability": 0.5,
                "answer_delta_if_true": "high",
            },
        ],
        "candidate_clarifiers": [
            {
                "id": "q1",
                "question": "Do you care most about latency, throughput, or cost?",
                "expected_information_gain_bits": 0.6,
                "expected_utility": 0.4,
                "estimated_cost_tokens": 12,
            }
        ],
        "decision": "answer_direct",
        "answer_constraints": ["state assumptions"],
        "rationale": "Provider guessed direct, but policy should override.",
    }


def test_intent_compressor_successful_mock_provider_path() -> None:
    provider = MockIntentProvider()
    compressor = IntentCompressor(provider=provider)

    decision = compressor.process(
        "Make this API faster.",
        trace_id="trace-123",
        metadata={"domain": "coding"},
    )

    assert decision.decision == Decision.ASK_CLARIFIER
    assert decision.trace_id == "trace-123"
    assert decision.clarifying_question is not None
    assert decision.metadata is not None
    assert decision.metadata["provider_name"] == "mock"
    assert decision.metadata["policy_applied"] is True
    assert decision.metadata["fallback"] is False
    assert provider.requests[0].system_instructions
    assert provider.requests[0].response_schema is not None
    assert provider.requests[0].metadata == {"domain": "coding"}


def test_intent_compressor_raises_on_validation_failure_in_strict_mode() -> None:
    provider = MockIntentProvider(
        payload_overrides={
            "bad": {
                "ambiguity_score": 2.0,
                "risk_score": 0.0,
                "intent_entropy_bits": 0.0,
                "intent_hypotheses": [],
                "decision": "answer_direct",
                "answer_constraints": [],
            }
        }
    )
    compressor = IntentCompressor(provider=provider)

    with pytest.raises(StructuredOutputValidationError):
        compressor.process("bad")


def test_intent_compressor_returns_explicit_fallback_when_not_strict() -> None:
    provider = MockIntentProvider(
        payload_overrides={
            "bad": {
                "ambiguity_score": 2.0,
                "risk_score": 0.0,
                "intent_entropy_bits": 0.0,
                "intent_hypotheses": [],
                "decision": "answer_direct",
                "answer_constraints": [],
            }
        }
    )
    compressor = IntentCompressor(provider=provider, strict=False)

    decision = compressor.process("bad", trace_id="trace-fallback")

    assert decision.decision == Decision.ANSWER_DIRECT
    assert decision.trace_id == "trace-fallback"
    assert decision.metadata is not None
    assert decision.metadata["source"] == "fallback"
    assert decision.metadata["fallback"] is True
    assert decision.metadata["fallback_reason"] == "validation_error"
    assert "provider analysis failed" in decision.answer_constraints


def test_intent_compressor_returns_explicit_fallback_on_provider_failure() -> None:
    compressor = IntentCompressor(
        provider=MockIntentProvider(fail_on_call=True),
        strict=False,
    )

    decision = compressor.process("Make this API faster.")

    assert decision.decision == Decision.ANSWER_DIRECT
    assert decision.metadata is not None
    assert decision.metadata["fallback_reason"] == "provider_error"


def test_policy_overrides_bad_provider_decision() -> None:
    provider = MockIntentProvider(payload_overrides={"override": _bad_policy_payload()})
    compressor = IntentCompressor(
        provider=provider,
        policy_config=PolicyConfig(tau=0.15),
    )

    decision = compressor.process("override")

    assert decision.decision == Decision.ASK_CLARIFIER
    assert decision.selected_clarifier_id == "q1"
    assert decision.metadata is not None
    assert decision.metadata["provider_proposed_decision"] == "answer_direct"
    assert decision.metadata["policy_applied"] is True
