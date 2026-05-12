from ica_core.config import ICAConfig, ICASettings


def test_config_defaults_are_demo_safe() -> None:
    config = ICAConfig()

    assert config.provider == "mock"
    assert config.model_name == "mock-clarifier-v1"
    assert config.tau == 0.15
    assert config.control_temperature == 0.0
    assert config.tracing_enabled is False
    assert config.openai_api_key is None
    assert config.xai_api_key is None


def test_config_reads_standard_provider_api_key_env_names(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    monkeypatch.setenv("XAI_API_KEY", "xai-test-key")
    monkeypatch.setenv("ICA_TAU", "0.25")
    monkeypatch.setenv("ICA_PROVIDER", "openai")

    config = ICAConfig()

    assert config.provider == "openai"
    assert config.tau == 0.25
    assert config.openai_api_key is not None
    assert config.openai_api_key.get_secret_value() == "openai-test-key"
    assert config.xai_api_key is not None
    assert config.xai_api_key.get_secret_value() == "xai-test-key"


def test_ica_settings_alias_preserves_initial_public_api() -> None:
    assert ICASettings is ICAConfig
    assert ICASettings().decision_threshold == ICASettings().tau
