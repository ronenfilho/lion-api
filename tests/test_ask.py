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


def test_falha_do_provedor_nao_derruba_a_api(tmp_path, sample_payloads) -> None:
    class BrokenProvider:
        name = "broken"

        def generate(self, system_prompt: str, user_prompt: str) -> str:
            raise LLMError("timeout")

    settings = Settings(database_path=str(tmp_path / "db.sqlite3"))
    with TestClient(create_app(settings, provider=BrokenProvider())) as client:
        client.post("/documents", json=sample_payloads[0])
        body = client.post("/ask", json={"question": "dedução de despesas médicas"}).json()

    assert body["answer"] == LLM_UNAVAILABLE_ANSWER
    assert body["citations"]
