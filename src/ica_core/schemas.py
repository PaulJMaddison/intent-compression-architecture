"""Pydantic models for the ICA structured decision contract.

The canonical contract lives in ``spec/clarifier_output.schema.json``. These
models follow that shape and add only practical package-level extensions:
``trace_id``, ``estimated_token_savings``, and small ``metadata`` maps.
"""

from __future__ import annotations

from enum import Enum
from math import log2
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Score = Annotated[float, Field(ge=0.0, le=1.0)]
Probability = Annotated[float, Field(ge=0.0, le=1.0)]
EntropyBits = Annotated[float, Field(ge=0.0)]
ExpectedUtility = float
DecisionThreshold = float
TokenCount = Annotated[float, Field(ge=0.0)]
LatencyMs = Annotated[float, Field(ge=0.0)]
MetadataValue = Any


class AnswerDelta(str, Enum):
    """How much the final answer would change if a hypothesis is true."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Decision(str, Enum):
    """Control-layer route selected before generation."""

    ANSWER_DIRECT = "answer_direct"
    ASK_CLARIFIER = "ask_clarifier"
    PREMISE_CHECK = "premise_check"
    REFUSE_REDIRECT = "refuse_redirect"


class IntentHypothesis(BaseModel):
    """A plausible interpretation of the user's request."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1)
    probability: Probability
    answer_delta_if_true: AnswerDelta
    notes: str | None = None
    metadata: dict[str, MetadataValue] | None = None

    @field_validator("label", "notes")
    @classmethod
    def _strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class CandidateClarifier(BaseModel):
    """A clarification question considered by the control layer."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_information_gain_bits: float
    expected_utility: ExpectedUtility
    estimated_cost_tokens: TokenCount
    estimated_latency_ms: LatencyMs | None = None
    estimated_token_savings: float | None = None
    metadata: dict[str, MetadataValue] | None = None

    @field_validator("id", "question")
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped


class ClarifierOutput(BaseModel):
    """Structured ICA decision object emitted before answer generation.

    ``rationale`` is a concise audit/debug explanation. It is intentionally not
    a chain-of-thought capture field.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    query_id: str | None = None
    trace_id: str | None = None
    ambiguity_score: Score
    risk_score: Score
    intent_entropy_bits: EntropyBits
    risk_labels: list[str] = Field(default_factory=list)
    intent_hypotheses: list[IntentHypothesis] = Field(min_length=1)
    candidate_clarifiers: list[CandidateClarifier] = Field(default_factory=list)
    decision: Decision
    selected_clarifier_id: str | None = None
    clarifying_question: str | None = None
    expected_utility: ExpectedUtility | None = None
    decision_threshold: DecisionThreshold | None = None
    answer_constraints: list[str]
    safe_redirect: str | None = None
    rationale: str = ""
    estimated_token_savings: float | None = None
    metadata: dict[str, MetadataValue] | None = None

    @field_validator("query_id", "trace_id", "selected_clarifier_id", "clarifying_question", "safe_redirect", "rationale")
    @classmethod
    def _strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("risk_labels", "answer_constraints")
    @classmethod
    def _strip_list_values(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]

    @model_validator(mode="after")
    def _validate_selected_clarifier(self) -> "ClarifierOutput":
        if self.selected_clarifier_id is None:
            return self

        known_ids = {candidate.id for candidate in self.candidate_clarifiers}
        if self.selected_clarifier_id not in known_ids:
            raise ValueError("selected_clarifier_id must reference a candidate clarifier")
        return self

    @model_validator(mode="after")
    def _validate_clarifying_question(self) -> "ClarifierOutput":
        if self.decision == Decision.ASK_CLARIFIER and self.selected_clarifier_id is not None:
            selected = self.selected_candidate()
            if selected is not None and self.clarifying_question is None:
                self.clarifying_question = selected.question
        return self

    @property
    def tau(self) -> DecisionThreshold | None:
        """Alias for the decision threshold used in the repo's formula."""

        return self.decision_threshold

    def best_candidate(self) -> CandidateClarifier | None:
        """Return the highest declared-utility candidate clarifier, if any."""

        if not self.candidate_clarifiers:
            return None
        return max(self.candidate_clarifiers, key=lambda candidate: candidate.expected_utility)

    def selected_candidate(self) -> CandidateClarifier | None:
        """Return the selected candidate clarifier, if one is referenced."""

        if self.selected_clarifier_id is None:
            return None
        for candidate in self.candidate_clarifiers:
            if candidate.id == self.selected_clarifier_id:
                return candidate
        return None


def entropy_bits(probabilities: list[float]) -> float:
    """Calculate Shannon entropy in bits for a probability distribution."""

    total = sum(probabilities)
    if total <= 0:
        return 0.0

    normalized = [probability / total for probability in probabilities if probability > 0]
    return -sum(probability * log2(probability) for probability in normalized)
