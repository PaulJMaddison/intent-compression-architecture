"""Core orchestration engine for ICA."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeAlias

from pydantic import ValidationError

from ica_core.policy import ClarificationPolicy, PolicyConfig
from ica_core.providers.base import (
    IntentProvider,
    ProviderError,
    ProviderRequest,
    ProviderResponse,
)
from ica_core.schemas import AnswerDelta, ClarifierOutput, Decision, IntentHypothesis
from ica_core.tracing import NoOpTraceSink, TraceSink, decision_trace_payload

ClarifierDecision: TypeAlias = ClarifierOutput

CONTROL_SYSTEM_PROMPT = """You are an intent-resolution control layer.
Estimate ambiguity and risk before answer generation.
Keep ambiguity_score separate from risk_score.
List plausible intent hypotheses and concise candidate clarifiers.
Ask only when the best expected utility of clarification is greater than tau.
Prefer direct answers when clarification would not materially change the answer.
Use rationale only for a concise audit note; do not include hidden reasoning."""


class IntentCompressionError(RuntimeError):
    """Base exception for ICA engine failures."""


class ProviderCallError(IntentCompressionError):
    """Raised when the provider call fails in strict mode."""


class StructuredOutputValidationError(IntentCompressionError):
    """Raised when provider data cannot validate into ICA schemas."""


class IntentCompressor:
    """Provider-agnostic ICA engine.

    Strict mode is enabled by default: provider and validation failures raise
    explicit exceptions. With ``strict=False``, failures return a conservative
    ``answer_direct`` fallback whose metadata marks the fallback source and
    reason so downstream systems can audit it.
    """

    def __init__(
        self,
        provider: IntentProvider,
        *,
        policy: ClarificationPolicy | None = None,
        policy_config: PolicyConfig | None = None,
        system_instructions: str = CONTROL_SYSTEM_PROMPT,
        strict: bool = True,
        trace_sink: TraceSink | None = None,
    ) -> None:
        if policy is not None and policy_config is not None:
            raise ValueError("pass either policy or policy_config, not both")
        self.provider = provider
        self.policy = policy or ClarificationPolicy(policy_config)
        self.system_instructions = system_instructions
        self.strict = strict
        self.trace_sink = trace_sink or NoOpTraceSink()

    def process(
        self,
        user_query: str,
        trace_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ClarifierDecision:
        """Resolve whether the system should answer, clarify, premise-check, or redirect."""

        query = user_query.strip()
        if not query:
            raise ValueError("user_query must not be blank")

        request = self._build_request(query, trace_id=trace_id, metadata=metadata)
        self.trace_sink.record(
            "ica.process.start",
            {
                "trace_id": trace_id,
                "provider": self._provider_name(),
                "query": query,
                "request_metadata": dict(metadata or {}),
            },
        )

        try:
            response = self.provider.generate_structured(request)
        except Exception as exc:
            if self.strict:
                raise ProviderCallError("ICA provider call failed") from exc
            decision = self._fallback_decision(
                query,
                trace_id=trace_id,
                metadata=metadata,
                reason="provider_error",
                detail=str(exc),
            )
            self._trace_decision(decision)
            return decision

        try:
            analysis = self._validate_response(response, trace_id=trace_id)
        except ValidationError as exc:
            if self.strict:
                raise StructuredOutputValidationError(
                    "provider response failed ICA schema validation"
                ) from exc
            decision = self._fallback_decision(
                query,
                trace_id=trace_id,
                metadata=metadata,
                reason="validation_error",
                detail=str(exc),
            )
            self._trace_decision(decision)
            return decision

        provider_decision = analysis.decision
        normalized = self.policy.decide(analysis)
        final = self._attach_engine_metadata(
            normalized,
            provider_response=response,
            provider_decision=provider_decision,
            trace_id=trace_id,
            metadata=metadata,
            fallback=False,
        )
        self._trace_decision(final)
        return final

    def resolve(
        self,
        query: str,
        *,
        query_id: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> ClarifierDecision:
        """Backward-compatible alias for the first scaffold's controller API."""

        return self.process(query, trace_id=query_id, metadata=dict(context or {}))

    def _build_request(
        self,
        query: str,
        *,
        trace_id: str | None,
        metadata: dict[str, Any] | None,
    ) -> ProviderRequest:
        return ProviderRequest(
            system_instructions=self.system_instructions,
            user_query=query,
            trace_id=trace_id,
            metadata=metadata or {},
            response_schema=ClarifierOutput.model_json_schema(),
            output_model=ClarifierOutput,
        )

    def _validate_response(
        self,
        response: ProviderResponse,
        *,
        trace_id: str | None,
    ) -> ClarifierOutput:
        analysis = ClarifierOutput.model_validate(response.payload)
        if trace_id is not None and analysis.trace_id is None:
            analysis = analysis.model_copy(update={"trace_id": trace_id})
        return analysis

    def _attach_engine_metadata(
        self,
        decision: ClarifierOutput,
        *,
        provider_response: ProviderResponse,
        provider_decision: str,
        trace_id: str | None,
        metadata: dict[str, Any] | None,
        fallback: bool,
    ) -> ClarifierOutput:
        merged_metadata = dict(decision.metadata or {})
        merged_metadata.update(
            {
                "source": "provider",
                "fallback": fallback,
                "provider_name": self._provider_name(),
                "provider_metadata": dict(provider_response.metadata),
                "provider_proposed_decision": provider_decision,
                "policy_applied": True,
            }
        )
        if metadata:
            merged_metadata["request_metadata"] = dict(metadata)

        return decision.model_copy(
            update={
                "trace_id": decision.trace_id or trace_id,
                "metadata": merged_metadata,
            }
        )

    def _fallback_decision(
        self,
        query: str,
        *,
        trace_id: str | None,
        metadata: dict[str, Any] | None,
        reason: str,
        detail: str,
    ) -> ClarifierOutput:
        del query
        fallback_metadata: dict[str, Any] = {
            "source": "fallback",
            "fallback": True,
            "fallback_reason": reason,
            "fallback_detail": detail,
            "provider_name": self._provider_name(),
            "policy_applied": False,
        }
        if metadata:
            fallback_metadata["request_metadata"] = dict(metadata)

        return ClarifierOutput(
            trace_id=trace_id,
            ambiguity_score=0.0,
            risk_score=0.0,
            intent_entropy_bits=0.0,
            risk_labels=[],
            intent_hypotheses=[
                IntentHypothesis(
                    label="provider analysis unavailable",
                    probability=1.0,
                    answer_delta_if_true=AnswerDelta.LOW,
                )
            ],
            candidate_clarifiers=[],
            decision=Decision.ANSWER_DIRECT,
            selected_clarifier_id=None,
            clarifying_question=None,
            expected_utility=None,
            decision_threshold=self.policy.config.tau,
            answer_constraints=[
                "provider analysis failed",
                "avoid relying on unstated intent assumptions",
            ],
            safe_redirect=None,
            rationale=(
                "Provider analysis was unavailable or invalid; returned an "
                "explicit conservative fallback."
            ),
            metadata=fallback_metadata,
        )

    def _trace_decision(self, decision: ClarifierOutput) -> None:
        self.trace_sink.record(
            "ica.process.decision",
            decision_trace_payload(decision),
        )

    def _provider_name(self) -> str:
        return getattr(self.provider, "name", self.provider.__class__.__name__)


class ICAController(IntentCompressor):
    """Backward-compatible name for ``IntentCompressor``."""
