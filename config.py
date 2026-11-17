from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DB: str = "blogicum_alembic"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432

    JWT_SECRET_KEY: SecretStr
    ACCESS_TOKEN_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
