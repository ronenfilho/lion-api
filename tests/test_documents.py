from fastapi.testclient import TestClient

DOC = {
    "title": "Documento de teste",
    "source": "https://exemplo.gov.br",
    "content": "Primeiro parágrafo com texto suficiente.\n\nSegundo parágrafo do documento.",
}


def test_cria_documento_retorna_201_com_trechos(client: TestClient) -> None:
    response = client.post("/documents", json=DOC)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["title"] == DOC["title"]
    assert body["chunk_count"] == 1


def test_cria_documento_sem_conteudo_retorna_422(client: TestClient) -> None:
    response = client.post("/documents", json={**DOC, "content": ""})

    assert response.status_code == 422


def test_lista_e_consulta_documentos(client: TestClient) -> None:
    created = client.post("/documents", json=DOC).json()

    listed = client.get("/documents").json()
    detail = client.get(f"/documents/{created['id']}")

    assert [d["id"] for d in listed] == [created["id"]]
    assert detail.status_code == 200
    assert detail.json() == created


def test_consulta_documento_inexistente_retorna_404_com_mensagem(client: TestClient) -> None:
    response = client.get("/documents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Documento 999 não encontrado."}


def test_remove_documento_retorna_204_e_tira_trechos_do_indice(client: TestClient) -> None:
    created = client.post("/documents", json=DOC).json()
    question = {"question": "O que diz o segundo parágrafo?"}
    assert client.post("/ask", json=question).json()["grounded"] is True

    response = client.delete(f"/documents/{created['id']}")

    assert response.status_code == 204
    assert client.get("/documents").json() == []
    assert client.post("/ask", json=question).json()["citations"] == []
    assert client.delete(f"/documents/{created['id']}").status_code == 404
