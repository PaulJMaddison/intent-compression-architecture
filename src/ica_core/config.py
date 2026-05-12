"""Runtime configuration for ICA core."""

from __future__ import annotations

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ICAConfig(BaseSettings):
    """Environment-backed configuration for the reusable core package.

    Provider API keys use their providers' standard environment variable names
    such as ``OPENAI_API_KEY`` and ``XAI_API_KEY``. The core remains
    provider-agnostic; these fields merely make adapter construction convenient.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    provider: str = Field(
        default="mock",
        validation_alias=AliasChoices("ICA_PROVIDER", "PROVIDER"),
        description="Provider adapter name to use when building demos or CLIs.",
    )
    model_name: str = Field(
        default="mock-clarifier-v1",
        validation_alias=AliasChoices("ICA_MODEL_NAME", "ICA_MODEL"),
        description="Provider model name for control-layer analysis.",
    )
    tau: float = Field(
        default=0.15,
        validation_alias=AliasChoices("ICA_TAU", "ICA_DECISION_THRESHOLD"),
        description="Ask iff the best candidate utility is greater than tau.",
    )
    control_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        validation_alias="ICA_CONTROL_TEMPERATURE",
        description="Temperature for model-backed control calls.",
    )
    tracing_enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("ICA_TRACING_ENABLED", "ICA_TRACE_ENABLED"),
        description="Enable tracing for local orchestration.",
    )
    min_ambiguity_to_ask: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        validation_alias="ICA_MIN_AMBIGUITY_TO_ASK",
        description="Minimum ambiguity required for ordinary clarification.",
    )
    premise_check_risk_threshold: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        validation_alias="ICA_PREMISE_CHECK_RISK_THRESHOLD",
        description="Risk threshold for premise-check routing.",
    )
    refuse_risk_threshold: float = Field(
        default=0.92,
        ge=0.0,
        le=1.0,
        validation_alias="ICA_REFUSE_RISK_THRESHOLD",
        description="Risk threshold where refusal or redirection dominates.",
    )
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
        description="Optional OpenAI API key for future provider adapters.",
    )
    xai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="XAI_API_KEY",
        description="Optional xAI API key for future provider adapters.",
    )

    @property
    def decision_threshold(self) -> float:
        """Backward-compatible alias for ``tau``."""

        return self.tau

    @property
    def trace_enabled(self) -> bool:
        """Backward-compatible alias for ``tracing_enabled``."""

        return self.tracing_enabled


ICASettings = ICAConfig
