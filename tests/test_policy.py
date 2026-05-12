from ica_core.policy import (
    PolicyConfig,
    PolicyInputs,
    ClarificationPolicy,
    compute_candidate_utility,
    decide_policy,
)
from ica_core.schemas import (
    AnswerDelta,
    CandidateClarifier,
    ClarifierOutput,
    Decision,
    IntentHypothesis,
)


def _candidate(
    *,
    expected_utility: float,
    information_gain: float = 0.5,
    cost_tokens: float = 10,
) -> CandidateClarifier:
    return CandidateClarifier(
        id="q1",
        question="Which meaning do you intend?",
        expected_information_gain_bits=information_gain,
        expected_utility=expected_utility,
        estimated_cost_tokens=cost_tokens,
    )


def _inputs(
    *,
    ambiguity_score: float,
    risk_score: float = 0.0,
    risk_labels: tuple[str, ...] = (),
    candidate: CandidateClarifier | None = None,
) -> PolicyInputs:
    return PolicyInputs(
        ambiguity_score=ambiguity_score,
        risk_score=risk_score,
        intent_entropy_bits=1.0,
        risk_labels=risk_labels,
        candidates=(candidate,) if candidate is not None else (),
    )


def _analysis(
    *,
    ambiguity_score: float,
    risk_score: float = 0.0,
    risk_labels: list[str] | None = None,
    candidate: CandidateClarifier | None = None,
) -> ClarifierOutput:
    return ClarifierOutput(
        ambiguity_score=ambiguity_score,
        risk_score=risk_score,
        intent_entropy_bits=1.0,
        risk_labels=risk_labels or [],
        intent_hypotheses=[
            IntentHypothesis(
                label="one",
                probability=0.5,
                answer_delta_if_true=AnswerDelta.HIGH,
            ),
            IntentHypothesis(
                label="two",
                probability=0.5,
                answer_delta_if_true=AnswerDelta.HIGH,
            ),
        ],
        candidate_clarifiers=[candidate] if candidate is not None else [],
        decision=Decision.ANSWER_DIRECT,
        answer_constraints=[],
    )


def test_policy_asks_when_expected_utility_clears_tau() -> None:
    decision = decide_policy(
        _inputs(ambiguity_score=0.8, candidate=_candidate(expected_utility=0.2)),
        PolicyConfig(tau=0.15),
    )

    assert decision.decision == Decision.ASK_CLARIFIER
    assert decision.selected_clarifier is not None
    assert decision.selected_clarifier.id == "q1"


def test_policy_uses_strict_greater_than_tau() -> None:
    decision = decide_policy(
        _inputs(ambiguity_score=0.8, candidate=_candidate(expected_utility=0.15)),
        PolicyConfig(tau=0.15),
    )

    assert decision.decision == Decision.ANSWER_DIRECT


def test_policy_answers_direct_when_candidate_utility_is_too_low() -> None:
    decision = decide_policy(
        _inputs(ambiguity_score=0.8, candidate=_candidate(expected_utility=0.05)),
        PolicyConfig(tau=0.15),
    )

    assert decision.decision == Decision.ANSWER_DIRECT
    assert decision.selected_clarifier is None


def test_policy_ignores_low_information_gain_candidate() -> None:
    decision = decide_policy(
        _inputs(
            ambiguity_score=0.8,
            candidate=_candidate(expected_utility=0.9, information_gain=0.01),
        ),
        PolicyConfig(tau=0.15, min_candidate_information_gain_bits=0.1),
    )

    assert decision.decision == Decision.ANSWER_DIRECT
    assert decision.selected_clarifier is None


def test_policy_handles_missing_candidate_clarifiers() -> None:
    decision = decide_policy(_inputs(ambiguity_score=0.9), PolicyConfig(tau=0.15))

    assert decision.decision == Decision.ANSWER_DIRECT
    assert decision.selected_clarifier is None
    assert decision.utility is None


def test_policy_keeps_high_risk_low_ambiguity_from_becoming_auto_clarification() -> None:
    decision = decide_policy(
        _inputs(
            ambiguity_score=0.1,
            risk_score=0.8,
            candidate=_candidate(expected_utility=0.8),
        ),
        PolicyConfig(tau=0.15),
    )

    assert decision.decision == Decision.ANSWER_DIRECT


def test_policy_routes_false_premise_to_premise_check_even_when_ambiguity_is_low() -> None:
    decision = decide_policy(
        _inputs(
            ambiguity_score=0.1,
            risk_score=0.7,
            risk_labels=("false_premise",),
            candidate=_candidate(expected_utility=0.2),
        ),
        PolicyConfig(tau=0.15),
    )

    assert decision.decision == Decision.PREMISE_CHECK
    assert decision.selected_clarifier is not None


def test_candidate_utility_separates_benefit_cost_and_risk_adjustment() -> None:
    utility = compute_candidate_utility(
        _candidate(expected_utility=0.4, cost_tokens=20),
        _inputs(
            ambiguity_score=0.5,
            risk_score=0.5,
            candidate=_candidate(expected_utility=0.4, cost_tokens=20),
        ),
        PolicyConfig(token_cost_weight=0.01, risk_adjustment_weight=0.2),
    )

    assert utility.benefit == 0.4
    assert utility.cost == 0.2
    assert utility.risk_adjustment == 0.05
    assert round(utility.adjusted_utility, 3) == 0.25


def test_clarification_policy_wrapper_updates_schema_output() -> None:
    policy = ClarificationPolicy(PolicyConfig(tau=0.15))

    decision = policy.decide(
        _analysis(
            ambiguity_score=0.8,
            candidate=_candidate(expected_utility=0.2),
        )
    )

    assert decision.decision == Decision.ASK_CLARIFIER
    assert decision.selected_clarifier_id == "q1"
    assert decision.clarifying_question == "Which meaning do you intend?"
    assert decision.decision_threshold == 0.15
