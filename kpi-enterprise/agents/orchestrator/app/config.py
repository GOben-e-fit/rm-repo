from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KPI_", env_file=".env", extra="ignore")

    env: str = "dev"
    auth_mode: str = "demo"  # "demo" bypasses JWT; uses X-Tenant-Id header
    jwt_jwks_url: str | None = None
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    default_tenant: str = "tnt_demo"
    cors_origins: str = "*"


settings = Settings()
