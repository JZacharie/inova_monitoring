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
    prometheus_endpoints: str = Field(
        default="[]", alias="PROMETHEUS_ENDPOINTS"
    )  # JSON string of endpoints
    metrics_refresh_interval: int = Field(default=30, alias="METRICS_REFRESH_INTERVAL")

    # SSO Configuration
    auth_methods_allowed: str = Field(
        default="google,github,entra,basic", alias="AUTH_METHODS_ALLOWED"
    )

    # Google OAuth
    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")

    # GitHub OAuth
    github_client_id: str | None = Field(default=None, alias="GITHUB_CLIENT_ID")
    github_client_secret: str | None = Field(default=None, alias="GITHUB_CLIENT_SECRET")

    # Microsoft Entra ID
    entra_id_client_id: str | None = Field(default=None, alias="ENTRA_ID_CLIENT_ID")
    entra_id_client_secret: str | None = Field(
        default=None, alias="ENTRA_ID_CLIENT_SECRET"
    )
    entra_id_tenant_id: str | None = Field(default=None, alias="ENTRA_ID_TENANT_ID")

    # Basic Auth Toggle
    enable_basic_auth: bool = Field(default=True, alias="ENABLE_BASIC_AUTH")

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
