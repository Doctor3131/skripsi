"""Environment loading and validation for local project services."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str
    neo4j_query_timeout_seconds: float
    log_level: str
    llm_api_key: str | None
    llm_base_url: str
    llm_model: str | None
    llm_temperature: float
    llm_timeout_seconds: float


def load_settings() -> Settings:
    """Load local .env values and fail clearly when required configuration is missing."""
    load_dotenv(dotenv_path=Path.cwd() / ".env")
    required = ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return Settings(
        neo4j_uri=os.environ["NEO4J_URI"],
        neo4j_user=os.environ["NEO4J_USER"],
        neo4j_password=os.environ["NEO4J_PASSWORD"],
        neo4j_database=os.getenv("NEO4J_DATABASE", "neo4j"),
        neo4j_query_timeout_seconds=float(os.getenv("NEO4J_QUERY_TIMEOUT_SECONDS", "5")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        llm_api_key=os.getenv("LLM_API_KEY") or None,
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        llm_model=os.getenv("LLM_MODEL") or None,
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
    )
