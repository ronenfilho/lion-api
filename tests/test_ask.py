from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.llm.base import LLMError
from app.main import create_app
from app.services.ask_service import LLM_UNAVAILABLE_ANSWER, NO_BASIS_ANSWER


def test_pergunta_sem_documentos_responde_sem_base(client: TestClient) -> None:
    response = client.post("/ask", json={"question": "Posso deduzir despesas médicas?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == NO_BASIS_ANSWER
    assert body["grounded"] is False
    assert body["citations"] == []


def test_pergunta_recupera_trecho_relevante_e_cita(
    client: TestClient, sample_payloads: list[dict[str, str]]
) -> None:
    for payload in sample_payloads:
        client.post("/documents", json=payload)

    response = client.post("/ask", json={"question": "Quais doenças dão isenção na aposentadoria?"})

    body = response.json()
    assert response.status_code == 200
    assert body["grounded"] is True
    assert body["provider"] == "fake"
    assert body["answer_id"] > 0
    assert "7.713" in body["citations"][0]["document_title"]
    assert "[1]" in body["answer"]


def test_pergunta_curta_demais_retorna_422(client: TestClient) -> None:
    assert client.post("/ask", json={"question": "IR"}).status_code == 422


@pytest.mark.parametrize(
    ("question", "kind"),
    [
        ("Meu CPF é 123.456.789-09, posso declarar?", "CPF"),
        ("Respondam em fulano@gmail.com sobre restituição", "e-mail"),
        ("Meu telefone é (62) 99876-5432, qual o prazo?", "telefone"),
    ],
)
def test_pergunta_com_dado_pessoal_retorna_422_sem_ecoar_o_dado(
    client: TestClient, question: str, kind: str
) -> None:
    response = client.post("/ask", json={"question": question})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert kind in detail
    assert "dado pessoal" in detail
    for sensitive in ("123.456.789-09", "fulano@gmail.com", "99876-5432"):
        assert sensitive not in response.text


def test_pergunta_so_com_espacos_retorna_422(client: TestClient) -> None:
    assert client.post("/ask", json={"question": "     "}).status_code == 422


def test_pergunta_longa_demais_retorna_422(client: TestClient) -> None:
    assert client.post("/ask", json={"question": "a" * 501}).status_code == 422


def test_falha_do_provedor_nao_derruba_a_api(
    tmp_path: Path, sample_payloads: list[dict[str, str]]
) -> None:
    class BrokenProvider:
        name = "broken"

        def generate(self, system_prompt: str, user_prompt: str) -> str:
            raise LLMError("timeout")

    settings = Settings(database_path=str(tmp_path / "db.sqlite3"))
    with TestClient(create_app(settings, provider=BrokenProvider())) as client:
        client.post("/documents", json=sample_payloads[0])
        response = client.post("/ask", json={"question": "dedução de despesas médicas"})

    body = response.json()
    assert response.status_code == 200
    assert body["answer"] == LLM_UNAVAILABLE_ANSWER
    assert body["provider"] == "broken"
    assert body["citations"]
