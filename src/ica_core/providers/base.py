"""Provider boundary for structured ICA control-layer calls."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeAlias

from pydantic import BaseModel

from ica_core.schemas import ClarifierOutput

ProviderPayload: TypeAlias = Mapping[str, Any] | ClarifierOutput


@dataclass(frozen=True)
class ProviderRequest:
    """Input passed to provider adapters for structured control calls."""

    system_instructions: str
    user_query: str
    trace_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    response_schema: Mapping[str, Any] | None = None
    output_model: type[BaseModel] | None = None


@dataclass(frozen=True)
class ProviderResponse:
    """Raw structured provider response plus optional adapter metadata."""

    payload: ProviderPayload
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ProviderError(RuntimeError):
    """Base class for provider boundary failures."""


class ProviderProtocol(Protocol):
    """Protocol implemented by structured ICA providers."""

    @property
    def name(self) -> str:
        """Stable provider name for traces and metadata."""

    def generate_structured(self, request: ProviderRequest) -> ProviderResponse:
        """Return raw data that can be validated into ICA schemas."""


class IntentProvider(ProviderProtocol, Protocol):
    """Backward-compatible provider protocol name."""

    def analyze(
        self,
        query: str,
        *,
        query_id: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> ClarifierOutput:
        """Return a validated ICA analysis for older integrations."""
