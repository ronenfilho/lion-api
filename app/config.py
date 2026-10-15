"""Configuração da aplicação lida de variáveis de ambiente (.env)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Parâmetros de execução da API."""

    database_path: str = "var/lion.sqlite3"
    llm_provider: str = "fake"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    llm_timeout_seconds: float = 20.0
    chunk_max_chars: int = 800
    default_top_k: int = 4


def load_settings() -> Settings:
    """Carrega as configurações do ambiente, lendo o `.env` se existir."""
    load_dotenv()
    return Settings(
        database_path=os.getenv("DATABASE_PATH", Settings.database_path),
        llm_provider=os.getenv("LLM_PROVIDER", Settings.llm_provider).lower(),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL", Settings.groq_model),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", Settings.llm_timeout_seconds)),
    )
