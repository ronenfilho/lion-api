import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def answer_id(client: TestClient) -> int:
    """Id de uma resposta gravada pelo `/ask`."""
    return client.post("/ask", json={"question": "Posso deduzir despesas médicas?"}).json()[
        "answer_id"
    ]


def test_feedback_com_comentario_retorna_201_com_registro(
    client: TestClient, answer_id: int
) -> None:
    response = client.post(
        f"/answers/{answer_id}/feedback", json={"useful": True, "comment": "  Ajudou muito. "}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["answer_id"] == answer_id
    assert body["useful"] is True
    assert body["comment"] == "Ajudou muito."
    assert "created_at" in body


def test_feedback_sem_comentario_retorna_201(client: TestClient, answer_id: int) -> None:
    response = client.post(f"/answers/{answer_id}/feedback", json={"useful": False})

    assert response.status_code == 201
    assert response.json()["comment"] is None


def test_feedback_de_resposta_inexistente_retorna_404(client: TestClient) -> None:
    response = client.post("/answers/999/feedback", json={"useful": True})

    assert response.status_code == 404
    assert response.json() == {"detail": "Resposta 999 não encontrada."}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"useful": "talvez"},
        {"useful": True, "comment": "x" * 501},
    ],
)
def test_feedback_invalido_retorna_422(
    client: TestClient, answer_id: int, payload: dict[str, object]
) -> None:
    assert client.post(f"/answers/{answer_id}/feedback", json=payload).status_code == 422


def test_feedback_com_dado_pessoal_no_comentario_retorna_422(
    client: TestClient, answer_id: int
) -> None:
    response = client.post(
        f"/answers/{answer_id}/feedback",
        json={"useful": False, "comment": "Me liguem no (62) 99876-5432"},
    )

    assert response.status_code == 422
    assert "telefone" in response.json()["detail"]
    assert "99876-5432" not in response.text
