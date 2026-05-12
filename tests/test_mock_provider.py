from ica_core import ICAController, MockIntentProvider
from ica_core.schemas import Decision


def test_mock_provider_runs_offline_and_asks_for_ambiguous_query() -> None:
    controller = ICAController(provider=MockIntentProvider())

    decision = controller.resolve("Make this API faster.")

    assert decision.decision == Decision.ASK_CLARIFIER
    assert decision.clarifying_question is not None
    assert decision.intent_entropy_bits > 0


def test_mock_provider_answers_direct_for_clear_query() -> None:
    controller = ICAController(provider=MockIntentProvider())

    decision = controller.resolve("Explain what a transformer is in one sentence.")

    assert decision.decision == Decision.ANSWER_DIRECT
    assert decision.candidate_clarifiers == []


def test_mock_provider_premise_checks_false_premise() -> None:
    controller = ICAController(provider=MockIntentProvider())

    decision = controller.resolve("Would you do X offensive act to stop nuclear war?")

    assert decision.decision == Decision.PREMISE_CHECK
    assert "false_premise" in decision.risk_labels
