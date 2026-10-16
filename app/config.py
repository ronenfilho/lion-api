"""Configuração da aplicação lida de variáveis de ambiente (.env)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

TOP_K_RANGE = (1, 10)  # mesmo limite do `top_k` aceito em `AskRequest`
CHUNK_MAX_CHARS_RANGE = (100, 4000)


class ConfigError(ValueError):
    """Valor de configuração em formato inválido ou fora do intervalo aceito."""


@dataclass(frozen=True)
class Settings:
    """Parâmetros de execução da API (validados na criação)."""

    database_path: str = "var/lion.sqlite3"
    llm_provider: str = "fake"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    llm_timeout_seconds: float = 20.0
    chunk_max_chars: int = 800
    default_top_k: int = 4

    def __post_init__(self) -> None:
        _check_range("DEFAULT_TOP_K", self.default_top_k, *TOP_K_RANGE)
        _check_range("CHUNK_MAX_CHARS", self.chunk_max_chars, *CHUNK_MAX_CHARS_RANGE)
        if self.llm_timeout_seconds <= 0:
            raise ConfigError("LLM_TIMEOUT_SECONDS deve ser maior que zero.")


def load_settings() -> Settings:
    """Carrega as configurações do ambiente, lendo o `.env` se existir.

    Variável vazia usa o padrão. Levanta `ConfigError` com o nome da variável se o
    valor for inválido, para a API não subir com configuração errada.
    """
    load_dotenv()
    return Settings(
        database_path=os.getenv("DATABASE_PATH") or Settings.database_path,
        llm_provider=(os.getenv("LLM_PROVIDER") or Settings.llm_provider).lower(),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL") or Settings.groq_model,
        llm_timeout_seconds=_env_float("LLM_TIMEOUT_SECONDS", Settings.llm_timeout_seconds),
        chunk_max_chars=_env_int("CHUNK_MAX_CHARS", Settings.chunk_max_chars),
        default_top_k=_env_int("DEFAULT_TOP_K", Settings.default_top_k),
    )


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"{name} deve ser um número inteiro (recebido: {raw!r}).") from None


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        raise ConfigError(f"{name} deve ser um número (recebido: {raw!r}).") from None


def _check_range(name: str, value: int, minimum: int, maximum: int) -> None:
    if not minimum <= value <= maximum:
        raise ConfigError(f"{name} deve estar entre {minimum} e {maximum} (recebido: {value}).")
