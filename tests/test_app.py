"""Testes da aplicação montada em `app.main` (a mesma servida pelo uvicorn)."""

import re
import tomllib
from pathlib import Path

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
