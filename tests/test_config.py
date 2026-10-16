"""Testes da leitura e validação da configuração por variáveis de ambiente."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import config
from app.config import ConfigError, Settings, load_settings
from app.llm.base import LLMError
from app.main import create_app

VARIABLES = ("DEFAULT_TOP_K", "CHUNK_MAX_CHARS", "LLM_TIMEOUT_SECONDS")


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Ignora o `.env` do desenvolvedor e limpa as variáveis testadas."""
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    for name in VARIABLES:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_sem_variaveis_usa_os_padroes() -> None:
    settings = load_settings()

    assert (settings.default_top_k, settings.chunk_max_chars) == (4, 800)
    assert settings.llm_timeout_seconds == 20.0


def test_variavel_vazia_usa_o_padrao(isolated_env: pytest.MonkeyPatch) -> None:
    isolated_env.setenv("DEFAULT_TOP_K", "  ")

    assert load_settings().default_top_k == 4


def test_le_top_k_e_tamanho_do_trecho_do_ambiente(isolated_env: pytest.MonkeyPatch) -> None:
    isolated_env.setenv("DEFAULT_TOP_K", "6")
    isolated_env.setenv("CHUNK_MAX_CHARS", "1200")

    settings = load_settings()

    assert (settings.default_top_k, settings.chunk_max_chars) == (6, 1200)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("DEFAULT_TOP_K", "quatro", "DEFAULT_TOP_K deve ser um número inteiro"),
        ("DEFAULT_TOP_K", "0", "DEFAULT_TOP_K deve estar entre 1 e 10"),
        ("DEFAULT_TOP_K", "11", "DEFAULT_TOP_K deve estar entre 1 e 10"),
        ("CHUNK_MAX_CHARS", "8.5", "CHUNK_MAX_CHARS deve ser um número inteiro"),
        ("CHUNK_MAX_CHARS", "99", "CHUNK_MAX_CHARS deve estar entre 100 e 4000"),
        ("CHUNK_MAX_CHARS", "4001", "CHUNK_MAX_CHARS deve estar entre 100 e 4000"),
        ("LLM_TIMEOUT_SECONDS", "rápido", "LLM_TIMEOUT_SECONDS deve ser um número"),
        ("LLM_TIMEOUT_SECONDS", "0", "LLM_TIMEOUT_SECONDS deve ser maior que zero"),
    ],
)
def test_valor_invalido_falha_com_o_nome_da_variavel(
    isolated_env: pytest.MonkeyPatch, name: str, value: str, message: str
) -> None:
    isolated_env.setenv(name, value)

    with pytest.raises(ConfigError, match=message):
        load_settings()


class FailingProvider:
    """Provedor que sempre falha: o `/ask` devolve todos os trechos recuperados."""

    name = "failing"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise LLMError("indisponível")


PARAGRAPHS = "\n\n".join(f"Despesas médicas, parágrafo {i}. " + "texto " * 30 for i in range(4))
DOCUMENT = {"title": "Documento", "source": "https://exemplo.gov.br", "content": PARAGRAPHS}


def run(tmp_path: Path, question: str | None = None, **overrides: int) -> dict:
    """Indexa o documento numa API com a configuração dada e, se pedido, pergunta."""
    settings = Settings(database_path=str(tmp_path / f"{overrides}.db"), **overrides)
    with TestClient(create_app(settings, provider=FailingProvider())) as client:
        created = client.post("/documents", json=DOCUMENT).json()
        if question is None:
            return created
        return client.post("/ask", json={"question": question}).json()


def test_top_k_padrao_configurado_limita_os_trechos_recuperados(tmp_path: Path) -> None:
    small = run(tmp_path, "despesas médicas", chunk_max_chars=300, default_top_k=1)
    large = run(tmp_path, "despesas médicas", chunk_max_chars=300, default_top_k=3)

    assert (len(small["citations"]), len(large["citations"])) == (1, 3)


def test_tamanho_do_trecho_configurado_e_usado_na_ingestao(tmp_path: Path) -> None:
    small = run(tmp_path, chunk_max_chars=300)
    large = run(tmp_path, chunk_max_chars=4000)

    assert (small["chunk_count"], large["chunk_count"]) == (4, 1)
