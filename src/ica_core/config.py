"""Runtime configuration for ICA core."""

from __future__ import annotations

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ICAConfig(BaseSettings):
    """Environment-backed configuration for the reusable core package."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    provider: str = Field(
        default="mock",
        validation_alias=AliasChoices("ICA_PROVIDER", "PROVIDER"),
    )
    model_name: str = Field(
        default="mock-clarifier-v1",
        validation_alias=AliasChoices("ICA_MODEL_NAME", "ICA_MODEL"),
    )
    tau: float = Field(
        default=0.15,
        validation_alias=AliasChoices("ICA_TAU", "ICA_DECISION_THRESHOLD"),
        allow_inf_nan=False,
    )
    control_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        validation_alias="ICA_CONTROL_TEMPERATURE",
        allow_inf_nan=False,
    )
    tracing_enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("ICA_TRACING_ENABLED", "ICA_TRACE_ENABLED"),
    )
    min_ambiguity_to_ask: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        validation_alias="ICA_MIN_AMBIGUITY_TO_ASK",
        allow_inf_nan=False,
    )
    premise_check_risk_threshold: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        validation_alias="ICA_PREMISE_CHECK_RISK_THRESHOLD",
        allow_inf_nan=False,
    )
    refuse_risk_threshold: float = Field(
        default=0.92,
        ge=0.0,
        le=1.0,
        validation_alias="ICA_REFUSE_RISK_THRESHOLD",
        allow_inf_nan=False,
    )
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    xai_api_key: SecretStr | None = Field(default=None, validation_alias="XAI_API_KEY")

    @property
    def decision_threshold(self) -> float:
        """Backward-compatible alias for ``tau``."""

        return self.tau

    @property
    def trace_enabled(self) -> bool:
        """Backward-compatible alias for ``tracing_enabled``."""

        return self.tracing_enabled


ICASettings = ICAConfig
