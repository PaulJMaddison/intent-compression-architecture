"""Offline deterministic provider for demos and tests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ica_core.providers.base import ProviderError, ProviderRequest, ProviderResponse
from ica_core.schemas import (
    AnswerDelta,
    CandidateClarifier,
    ClarifierOutput,
    Decision,
    IntentHypothesis,
    entropy_bits,
)


class MockIntentProvider:
    """Heuristic provider that exercises ICA without live API access.

    ``payload_overrides`` can pin exact provider payloads by normalized query,
    which makes validation and policy-override tests deterministic.
    """

    def __init__(
        self,
        *,
        payload_overrides: Mapping[str, Mapping[str, Any] | ClarifierOutput] | None = None,
        fail_on_call: bool = False,
        name: str = "mock",
    ) -> None:
        self._payload_overrides = {
            key.lower().strip(): value for key, value in (payload_overrides or {}).items()
        }
        self._fail_on_call = fail_on_call
        self._name = name
        self.requests: list[ProviderRequest] = []

    @property
    def name(self) -> str:
        return self._name

    def generate_structured(self, request: ProviderRequest) -> ProviderResponse:
        """Return raw structured estimates for a provider request."""

        self.requests.append(request)
        if self._fail_on_call:
            raise ProviderError("mock provider configured to fail")

        normalized = request.user_query.lower().strip()
        if normalized in self._payload_overrides:
            return ProviderResponse(
                payload=self._payload_overrides[normalized],
                metadata={"provider": self.name, "fixture": "override"},
            )

        output = self._route(request.user_query, trace_id=request.trace_id)
        return ProviderResponse(
            payload=output,
            metadata={"provider": self.name, "fixture": "heuristic"},
        )

    def analyze(
        self,
        query: str,
        *,
        query_id: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> ClarifierOutput:
        """Backward-compatible helper returning a validated analysis."""

        request = ProviderRequest(
            system_instructions="Analyze the query for ICA routing.",
            user_query=query,
            trace_id=query_id,
            metadata=context or {},
            response_schema=ClarifierOutput.model_json_schema(),
            output_model=ClarifierOutput,
        )
        response = self.generate_structured(request)
        return ClarifierOutput.model_validate(response.payload)

    def _route(self, query: str, *, trace_id: str | None) -> ClarifierOutput:
        normalized = query.lower().strip()

        if "propaganda" in normalized:
            return self._public_reasoning(trace_id)
        if "nuclear war" in normalized or "offensive act" in normalized:
            return self._false_premise(trace_id)
        if any(term in normalized for term in ("dose", "rash", "contract", "stock")):
            return self._high_risk_context_missing(trace_id, query)
        if self._looks_ambiguous(normalized):
            return self._generic_ambiguous(trace_id)
        return self._direct(trace_id)

    def _public_reasoning(self, trace_id: str | None) -> ClarifierOutput:
        hypotheses = [
            IntentHypothesis(
                label="persuasive political advocacy",
                probability=0.46,
                answer_delta_if_true=AnswerDelta.HIGH,
                notes="The answer should focus on rhetoric, persuasion, and overt ideology.",
            ),
            IntentHypothesis(
                label="coordinated deceptive messaging",
                probability=0.39,
                answer_delta_if_true=AnswerDelta.HIGH,
                notes="The evidence bar is higher and should separate advocacy from deception.",
            ),
            IntentHypothesis(
                label="other",
                probability=0.15,
                answer_delta_if_true=AnswerDelta.MEDIUM,
            ),
        ]
        return ClarifierOutput(
            trace_id=trace_id,
            ambiguity_score=0.74,
            risk_score=0.22,
            intent_entropy_bits=entropy_bits([item.probability for item in hypotheses]),
            risk_labels=["public_reasoning"],
            intent_hypotheses=hypotheses,
            candidate_clarifiers=[
                CandidateClarifier(
                    id="q1",
                    question=(
                        "Do you mean propaganda as in biased or one-sided political "
                        "messaging intended to influence opinion?"
                    ),
                    expected_information_gain_bits=0.88,
                    expected_utility=0.45,
                    estimated_cost_tokens=15,
                    estimated_latency_ms=1000,
                ),
                CandidateClarifier(
                    id="q2",
                    question=(
                        "Do you mean biased political messaging, coordinated "
                        "deception, deliberate misinformation, or something else?"
                    ),
                    expected_information_gain_bits=0.52,
                    expected_utility=0.22,
                    estimated_cost_tokens=17,
                    estimated_latency_ms=1200,
                ),
            ],
            decision=Decision.ANSWER_DIRECT,
            answer_constraints=[
                "avoid loaded framing",
                "define contested terms before conclusion",
                "separate evidence from interpretation",
            ],
        )

    def _false_premise(self, trace_id: str | None) -> ClarifierOutput:
        hypotheses = [
            IntentHypothesis(
                label="accept false dilemma",
                probability=0.35,
                answer_delta_if_true=AnswerDelta.HIGH,
            ),
            IntentHypothesis(
                label="explain why the premise fails",
                probability=0.65,
                answer_delta_if_true=AnswerDelta.HIGH,
            ),
        ]
        return ClarifierOutput(
            trace_id=trace_id,
            ambiguity_score=0.45,
            risk_score=0.78,
            intent_entropy_bits=entropy_bits([item.probability for item in hypotheses]),
            risk_labels=["false_premise"],
            intent_hypotheses=hypotheses,
            candidate_clarifiers=[
                CandidateClarifier(
                    id="premise-q1",
                    question=(
                        "Do you want a factual explanation of why the premise fails, "
                        "or a discussion of the ethical framing without endorsing it?"
                    ),
                    expected_information_gain_bits=0.44,
                    expected_utility=0.24,
                    estimated_cost_tokens=28,
                    estimated_latency_ms=1200,
                )
            ],
            decision=Decision.ANSWER_DIRECT,
            answer_constraints=[
                "do not accept false causal framing",
                "offer safe premise correction",
            ],
            safe_redirect="Explain the premise problem and offer a safer analytical frame.",
        )

    def _high_risk_context_missing(self, trace_id: str | None, query: str) -> ClarifierOutput:
        question = self._context_question(query)
        hypotheses = [
            IntentHypothesis(
                label="missing safety-critical context",
                probability=0.70,
                answer_delta_if_true=AnswerDelta.HIGH,
            ),
            IntentHypothesis(
                label="general educational answer is sufficient",
                probability=0.30,
                answer_delta_if_true=AnswerDelta.MEDIUM,
            ),
        ]
        return ClarifierOutput(
            trace_id=trace_id,
            ambiguity_score=0.68,
            risk_score=0.72,
            intent_entropy_bits=entropy_bits([item.probability for item in hypotheses]),
            risk_labels=["context_missing"],
            intent_hypotheses=hypotheses,
            candidate_clarifiers=[
                CandidateClarifier(
                    id="risk-q1",
                    question=question,
                    expected_information_gain_bits=0.72,
                    expected_utility=0.36,
                    estimated_cost_tokens=24,
                    estimated_latency_ms=1300,
                )
            ],
            decision=Decision.ANSWER_DIRECT,
            answer_constraints=[
                "avoid definitive advice without context",
                "surface safety boundaries",
            ],
        )

    def _generic_ambiguous(self, trace_id: str | None) -> ClarifierOutput:
        hypotheses = [
            IntentHypothesis(
                label="optimize for speed or efficiency",
                probability=0.34,
                answer_delta_if_true=AnswerDelta.HIGH,
            ),
            IntentHypothesis(
                label="optimize for quality or clarity",
                probability=0.33,
                answer_delta_if_true=AnswerDelta.MEDIUM,
            ),
            IntentHypothesis(
                label="optimize for cost or constraints",
                probability=0.33,
                answer_delta_if_true=AnswerDelta.MEDIUM,
            ),
        ]
        return ClarifierOutput(
            trace_id=trace_id,
            ambiguity_score=0.62,
            risk_score=0.08,
            intent_entropy_bits=entropy_bits([item.probability for item in hypotheses]),
            risk_labels=[],
            intent_hypotheses=hypotheses,
            candidate_clarifiers=[
                CandidateClarifier(
                    id="generic-q1",
                    question=(
                        "What outcome matters most here: speed, quality, cost, "
                        "or a specific constraint?"
                    ),
                    expected_information_gain_bits=0.67,
                    expected_utility=0.29,
                    estimated_cost_tokens=18,
                    estimated_latency_ms=900,
                )
            ],
            decision=Decision.ANSWER_DIRECT,
            answer_constraints=["state assumptions if answering directly"],
        )

    def _direct(self, trace_id: str | None) -> ClarifierOutput:
        hypotheses = [
            IntentHypothesis(
                label="plain direct request",
                probability=1.0,
                answer_delta_if_true=AnswerDelta.LOW,
            )
        ]
        return ClarifierOutput(
            trace_id=trace_id,
            ambiguity_score=0.12,
            risk_score=0.03,
            intent_entropy_bits=0.0,
            risk_labels=[],
            intent_hypotheses=hypotheses,
            candidate_clarifiers=[],
            decision=Decision.ANSWER_DIRECT,
            answer_constraints=["answer directly"],
        )

    def _looks_ambiguous(self, normalized: str) -> bool:
        markers = (
            "best",
            "clean up",
            "faster",
            "stronger",
            "should i",
            "should we",
            "why is",
            "rewrite",
            "summarize",
            "launch plan",
        )
        return any(marker in normalized for marker in markers)

    def _context_question(self, query: str) -> str:
        normalized = query.lower()
        if "contract" in normalized:
            return "What jurisdiction, contract type, and risk area matter most?"
        if "stock" in normalized:
            return "What is your time horizon, portfolio context, and risk tolerance?"
        if "dose" in normalized:
            return "What medication, indication, patient age, and prescriber guidance apply?"
        if "rash" in normalized:
            return "How long has it been present, and are there fever, breathing issues, severe pain, or rapid spread?"
        return "What safety-critical context should constrain the answer?"
