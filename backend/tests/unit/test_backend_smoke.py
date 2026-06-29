from app.create_app import create_app
from app.settings import AppSettings


def test_backend_app_uses_expected_metadata() -> None:
    app = create_app()

    assert app.title == "WSR Creation Agent API"
    assert app.version == "0.1.0"


def test_provider_settings_default_to_stub_mode() -> None:
    settings = AppSettings()

    assert settings.llm_provider_mode == "stub"
    assert settings.uses_real_llm_credentials is False
