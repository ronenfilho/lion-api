from fastapi.testclient import TestClient


def test_health_retorna_ok_com_timestamp(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body
