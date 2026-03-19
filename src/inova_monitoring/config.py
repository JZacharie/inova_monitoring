from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings managed via environment variables or .env file.
    """

    # PostgreSQL Configuration
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="password", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="inova_monitoring", alias="POSTGRES_DB")

    # Prometheus Configuration
    prometheus_url: str = Field(default="http://localhost:9090", alias="PROMETHEUS_URL")

    # SSO Configuration
    sso_client_id: str | None = Field(default=None, alias="SSO_CLIENT_ID")
    sso_client_secret: str | None = Field(default=None, alias="SSO_CLIENT_SECRET")
    sso_auth_url: str | None = Field(default=None, alias="SSO_AUTH_URL")
    sso_token_url: str | None = Field(default=None, alias="SSO_TOKEN_URL")

    # Application Settings
    debug: bool = Field(default=True, alias="DEBUG")
    api_secret_key: str = Field(
        default="change-me-in-production", alias="API_SECRET_KEY"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
