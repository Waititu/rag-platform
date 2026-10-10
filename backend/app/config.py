from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    database_url: str = (
        "postgresql+psycopg://rag:ragpassword@localhost:5432/rag"
    )

    ollama_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    generation_model: str = "gemma4:12b"

    cors_origins: str = "http://localhost:5173"

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    request_timeout_seconds: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
