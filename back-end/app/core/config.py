"""
Application configuration using pydantic-settings.
Loads from environment variables or .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+psycopg2://rpgchat:rpgchat@localhost:5433/rpgchat"

    # Application
    app_name: str = "RPGChat.AI"
    debug: bool = True
    secret_key: str = "change-this-to-a-random-secret-key"

    # Optional: Default LLM API provider settings
    default_api_base_url: str | None = None
    default_api_key: str | None = None
    default_chat_model_id: str | None = None
    default_embedding_model_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()

