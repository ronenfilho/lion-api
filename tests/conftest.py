from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.llm.fake import FakeProvider
from app.main import create_app

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    """API com banco temporário e provedor fake (sem rede)."""
    settings = Settings(database_path=str(tmp_path / "test.sqlite3"))
    with TestClient(create_app(settings, provider=FakeProvider())) as test_client:
        yield test_client


@pytest.fixture
def sample_payloads() -> list[dict[str, str]]:
    """Documentos do corpus de exemplo no formato do `POST /documents`."""
    from scripts.load_sample import parse

    return [parse(path) for path in sorted(SAMPLE_DIR.glob("*.md"))]
