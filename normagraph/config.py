"""Application configuration, loaded from environment variables (prefix ``NG_``)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NG_", env_file=".env", extra="ignore")

    environment: str = "local"

    # Retrieval: how many norms to return, and how many graph hops to expand.
    top_k: int = 3
    expand_hops: int = 1

    # LLM provider cascade for the explain/answer layer. Each reads its own key
    # from the env; when all fail, the service returns the retrieved norm text.
    llm_spec: str = "anthropic,openai,gemini,deepseek,ollama"
    llm_max_tokens: int = 400


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
