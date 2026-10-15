"""Ponto de entrada da LION API."""

from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="LION API",
    description="Assistente RAG para dúvidas de IRPF fundamentado em fontes oficiais da RFB.",
    version="0.1.0",
)


class HealthResponse(BaseModel):
    """Resposta do health check."""

    status: str
    timestamp: datetime


@app.get("/health", response_model=HealthResponse, tags=["infra"])
def health() -> HealthResponse:
    """Indica se a API está no ar."""
    return HealthResponse(status="ok", timestamp=datetime.now(UTC))
