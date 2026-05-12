"""Deterministic ask-vs-answer policy for ICA.

The repo's ideal rule is:

    ask iff max_q U(q | x) > tau

In a live system, estimating U(q | x) may require model calls, calibration data,
or domain-specific loss models. This module deliberately avoids those calls. It
uses the provider's structured candidate estimates plus local deterministic
adjustments for interaction cost and risk. That keeps the orchestration
auditable and unit-testable.
"""

from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from ica_core.config import ICAConfig
from ica_core.schemas import CandidateClarifier, ClarifierOutput, Decision


class PolicyConfig(BaseModel):
    """Domain-tunable knobs for deterministic routing."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tau: float = Field(
        default=0.15,
        validation_alias=AliasChoices("tau", "decision_threshold"),
        description="Ask iff the best adjusted candidate utility is greater than tau.",
    )
    min_ambiguity_to_ask: float = Field(default=0.35, ge=0.0, le=1.0)
    min_candidate_information_gain_bits: float = Field(default=0.0, ge=0.0)
    token_cost_weight: float = Field(default=0.0, ge=0.0)
    latency_cost_weight: float = Field(default=0.0, ge=0.0)
    clarification_turn_cost: float = Field(default=0.0, ge=0.0)
    risk_adjustment_weight: float = Field(
        default=0.0,
        ge=0.0,
        description="Optional bonus when ambiguity and risk both make clarification valuable.",
    )
    premise_check_risk_threshold: float = Field(default=0.60, ge=0.0, le=1.0)
    refuse_risk_threshold: float = Field(default=0.92, ge=0.0, le=1.0)
    false_premise_labels: tuple[str, ...] = ("false_premise", "impossible_premise")
    refusal_labels: tuple[str, ...] = ("malicious_or_exploitative_intent",)

    @property
    def decision_threshold(self) -> float:
        """Backward-compatible alias for ``tau``."""

        return self.tau

    @classmethod
    def from_config(cls, config: ICAConfig) -> "PolicyConfig":
        """Build policy configuration from package settings."""

        return cls(
            tau=config.tau,
            min_ambiguity_to_ask=config.min_ambiguity_to_ask,
            premise_check_risk_threshold=config.premise_check_risk_threshold,
            refuse_risk_threshold=config.refuse_risk_threshold,
        )

    @classmethod
    def from_settings(cls, settings: ICAConfig) -> "PolicyConfig":
        """Backward-compatible constructor for older ``ICASettings`` imports."""

        return cls.from_config(settings)


class PolicyInputs(BaseModel):
    """Pure policy input extracted from provider analysis."""

    model_config = ConfigDict(frozen=True)

    ambiguity_score: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    intent_entropy_bits: float = Field(ge=0.0)
    risk_labels: tuple[str, ...] = ()
    candidates: tuple[CandidateClarifier, ...] = ()

    @classmethod
    def from_output(cls, output: ClarifierOutput) -> "PolicyInputs":
        """Extract deterministic policy inputs from a structured analysis."""

        return cls(
            ambiguity_score=output.ambiguity_score,
            risk_score=output.risk_score,
            intent_entropy_bits=output.intent_entropy_bits,
            risk_labels=tuple(output.risk_labels),
            candidates=tuple(output.candidate_clarifiers),
        )


class UtilityBreakdown(BaseModel):
    """Auditable components of the practical utility approximation."""

    model_config = ConfigDict(frozen=True)

    candidate_id: str
    benefit: float
    cost: float
    risk_adjustment: float
    adjusted_utility: float


class PolicyDecision(BaseModel):
    """Deterministic route selected by the policy."""

    model_config = ConfigDict(frozen=True, use_enum_values=True)

    decision: Decision
    selected_clarifier: CandidateClarifier | None = None
    utility: UtilityBreakdown | None = None
    tau: float
    rationale: str


def compute_candidate_utility(
    candidate: CandidateClarifier,
    inputs: PolicyInputs,
    config: PolicyConfig | None = None,
) -> UtilityBreakdown:
    """Compute the practical utility approximation for one clarifier.

    ``candidate.expected_utility`` is treated as the provider-estimated benefit
    of resolving intent before generation. Local policy can subtract explicit
    token/latency/friction costs and optionally add a risk adjustment when the
    same ambiguity could alter safe handling.
    """

    policy_config = config or PolicyConfig()
    latency_ms = candidate.estimated_latency_ms or 0.0
    benefit = candidate.expected_utility
    cost = (
        candidate.estimated_cost_tokens * policy_config.token_cost_weight
        + latency_ms * policy_config.latency_cost_weight
        + policy_config.clarification_turn_cost
    )
    risk_adjustment = (
        inputs.risk_score
        * inputs.ambiguity_score
        * policy_config.risk_adjustment_weight
    )
    adjusted_utility = benefit + risk_adjustment - cost

    return UtilityBreakdown(
        candidate_id=candidate.id,
        benefit=benefit,
        cost=cost,
        risk_adjustment=risk_adjustment,
        adjusted_utility=adjusted_utility,
    )


def candidate_is_usable(
    candidate: CandidateClarifier,
    config: PolicyConfig | None = None,
) -> bool:
    """Return whether a candidate is concrete enough for routing."""

    policy_config = config or PolicyConfig()
    return (
        bool(candidate.question.strip())
        and candidate.expected_information_gain_bits
        >= policy_config.min_candidate_information_gain_bits
    )


def select_best_candidate(
    inputs: PolicyInputs,
    config: PolicyConfig | None = None,
) -> tuple[CandidateClarifier | None, UtilityBreakdown | None]:
    """Select the usable candidate with the highest adjusted utility."""

    policy_config = config or PolicyConfig()
    best_candidate: CandidateClarifier | None = None
    best_utility: UtilityBreakdown | None = None

    for candidate in inputs.candidates:
        if not candidate_is_usable(candidate, policy_config):
            continue
        utility = compute_candidate_utility(candidate, inputs, policy_config)
        if best_utility is None or utility.adjusted_utility > best_utility.adjusted_utility:
            best_candidate = candidate
            best_utility = utility

    return best_candidate, best_utility


def decide_policy(
    inputs: PolicyInputs,
    config: PolicyConfig | None = None,
) -> PolicyDecision:
    """Apply the ICA routing rule deterministically.

    Normal clarification follows the repo rule exactly after local adjustment:
    ask iff ``max_q U(q | x) > tau``. High-risk low-ambiguity cases are handled
    separately: false premises route to premise checks, and clearly unsafe
    requests route to refusal/redirection rather than clarification-by-default.
    """

    policy_config = config or PolicyConfig()
    labels = set(inputs.risk_labels)
    best_candidate, best_utility = select_best_candidate(inputs, policy_config)

    if _should_refuse(inputs, labels, policy_config):
        return PolicyDecision(
            decision=Decision.REFUSE_REDIRECT,
            selected_clarifier=None,
            utility=None,
            tau=policy_config.tau,
            rationale=(
                "Risk is high and clarification is unlikely to make literal "
                "compliance safe; route to constrained assistance."
            ),
        )

    if _should_premise_check(inputs, labels, policy_config):
        return PolicyDecision(
            decision=Decision.PREMISE_CHECK,
            selected_clarifier=best_candidate,
            utility=best_utility,
            tau=policy_config.tau,
            rationale=(
                "The request appears to contain a risky or false premise; "
                "check the premise before generation."
            ),
        )

    if inputs.ambiguity_score < policy_config.min_ambiguity_to_ask:
        return PolicyDecision(
            decision=Decision.ANSWER_DIRECT,
            selected_clarifier=None,
            utility=best_utility,
            tau=policy_config.tau,
            rationale="Ambiguity is below the clarification threshold.",
        )

    if best_candidate is not None and best_utility is not None:
        if best_utility.adjusted_utility > policy_config.tau:
            return PolicyDecision(
                decision=Decision.ASK_CLARIFIER,
                selected_clarifier=best_candidate,
                utility=best_utility,
                tau=policy_config.tau,
                rationale=(
                    "The best clarifier clears tau under the practical "
                    "expected-utility approximation."
                ),
            )

    return PolicyDecision(
        decision=Decision.ANSWER_DIRECT,
        selected_clarifier=None,
        utility=best_utility,
        tau=policy_config.tau,
        rationale=(
            "No usable candidate clarification has enough expected utility to "
            "beat tau."
        ),
    )


class ClarificationPolicy:
    """Compatibility wrapper that applies pure policy functions to outputs."""

    def __init__(self, config: PolicyConfig | None = None) -> None:
        self.config = config or PolicyConfig()

    def decide(self, analysis: ClarifierOutput) -> ClarifierOutput:
        """Return a finalized decision object for an analyzed query."""

        policy_decision = decide_policy(PolicyInputs.from_output(analysis), self.config)
        candidate = policy_decision.selected_clarifier
        utility = policy_decision.utility

        return analysis.model_copy(
            update={
                "decision": policy_decision.decision,
                "selected_clarifier_id": candidate.id if candidate else None,
                "clarifying_question": candidate.question if candidate else None,
                "expected_utility": (
                    utility.adjusted_utility if utility is not None else None
                ),
                "decision_threshold": policy_decision.tau,
                "rationale": policy_decision.rationale,
            }
        )


def _should_premise_check(
    inputs: PolicyInputs,
    labels: set[str],
    config: PolicyConfig,
) -> bool:
    return (
        inputs.risk_score >= config.premise_check_risk_threshold
        and bool(labels.intersection(config.false_premise_labels))
    )


def _should_refuse(
    inputs: PolicyInputs,
    labels: set[str],
    config: PolicyConfig,
) -> bool:
    return (
        inputs.risk_score >= config.refuse_risk_threshold
        or bool(labels.intersection(config.refusal_labels))
    )
