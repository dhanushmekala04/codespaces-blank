from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "PatientCare API"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = True

    # Database
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "patientcare"
    redis_url: str = "redis://localhost:6379/0"

    # Vector Database
    pinecone_api_key: str = ""
    pinecone_index: str = "healthcare_knowledge"

    # LLM — NVIDIA NIM (single key for all models)
    nvidia_api_key: str =

    # Security
    jwt_secret_key: str = "cb6863e2-fc34-4398-9cf6-54d98f169716"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",       # ignore unknown env vars (e.g. LANGFUSE_BASE_URL)
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
