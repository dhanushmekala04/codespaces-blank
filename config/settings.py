from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PatientCare API"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = True

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "patientcare"
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    PINECONE_API_KEY: str
    PINECONE_INDEX: str

    MONGODB_URI: str
    REDIS_URL: str

settings = Settings()

settings = get_settings()
