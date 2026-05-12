"""Public API for the ICA core package."""

from ica_core.config import ICAConfig, ICASettings
from ica_core.core import ClarifierDecision, ICAController, IntentCompressor
from ica_core.policy import ClarificationPolicy, PolicyConfig
from ica_core.providers.base import IntentProvider, ProviderRequest, ProviderResponse
from ica_core.providers.mock import MockIntentProvider
from ica_core.schemas import (
    AnswerDelta,
    CandidateClarifier,
    ClarifierOutput,
    Decision,
    IntentHypothesis,
)
from ica_core.tracing import JSONLTraceSink, NoOpTraceSink, query_hash, redact_query

__all__ = [
    "AnswerDelta",
    "CandidateClarifier",
    "ClarificationPolicy",
    "ClarifierDecision",
    "ClarifierOutput",
    "Decision",
    "ICAConfig",
    "ICAController",
    "ICASettings",
    "IntentCompressor",
    "IntentHypothesis",
    "JSONLTraceSink",
    "IntentProvider",
    "MockIntentProvider",
    "NoOpTraceSink",
    "PolicyConfig",
    "ProviderRequest",
    "ProviderResponse",
    "query_hash",
    "redact_query",
]

__version__ = "0.1.0"
