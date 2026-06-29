from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Runtime settings for the backend API."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "WSR Creation Agent API"
    app_version: str = "0.1.0"
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./wsr_creation_agent.db"
    llm_provider_mode: str = "stub"
    grok_api_key: str | None = None
    deepseek_api_key: str | None = None

    @property
    def uses_real_llm_credentials(self) -> bool:
        """Return whether runtime settings require real provider credentials."""
        return self.llm_provider_mode.lower() != "stub"
