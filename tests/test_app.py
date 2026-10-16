"""Testes da aplicação montada em `app.main` (a mesma servida pelo uvicorn)."""

import re
import tomllib
from pathlib import Path

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app import __version__

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def test_openapi_expoe_a_versao_do_pacote(client: TestClient) -> None:
    info = client.get("/openapi.json").json()["info"]

    assert info["version"] == __version__
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)


def test_pyproject_le_a_versao_de_app_sem_duplicar() -> None:
    config = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    assert "version" not in config["project"]
    assert "version" in config["project"]["dynamic"]
    assert config["tool"]["setuptools"]["dynamic"]["version"] == {"attr": "app.__version__"}


EXPECTED_ROUTES = {
    ("GET", "/health"),
    ("POST", "/documents"),
    ("GET", "/documents"),
    ("GET", "/documents/{document_id}"),
    ("DELETE", "/documents/{document_id}"),
    ("POST", "/ask"),
    ("POST", "/answers/{answer_id}/feedback"),
}


def test_aplicacao_do_uvicorn_registra_todas_as_rotas() -> None:
    """Confere `app.main.app`, não uma app de teste: router esquecido no `main` falha aqui."""
    from app.main import app

    registered = {
        (method, route.path)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    }

    assert registered == EXPECTED_ROUTES


def test_aplicacao_do_uvicorn_responde_health_e_openapi() -> None:
    from app.main import app

    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        paths = client.get("/openapi.json").json()["paths"]

    assert {path for _, path in EXPECTED_ROUTES} == set(paths)
