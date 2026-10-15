"""Ponto de entrada da LION API."""

from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel

from app.api import ask_routes, document_routes, feedback_routes
from app.api.errors import register_error_handlers
from app.config import Settings, load_settings
from app.llm.base import LLMProvider
from app.llm.factory import create_provider
from app.repositories.answer_repository import AnswerRepository
from app.repositories.database import connect
from app.repositories.document_repository import DocumentRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.services.ask_service import AskService
from app.services.document_service import DocumentService
from app.services.feedback_service import FeedbackService
from app.services.retriever import BM25Retriever


class HealthResponse(BaseModel):
    """Resposta do health check."""

    status: str
    timestamp: datetime


def create_app(settings: Settings | None = None, provider: LLMProvider | None = None) -> FastAPI:
    """Monta a aplicação com suas dependências (injetáveis nos testes)."""
    settings = settings or load_settings()
    conn = connect(settings.database_path)
    documents = DocumentRepository(conn)
    answers = AnswerRepository(conn)

    app = FastAPI(
        title="LION API",
        description="Assistente RAG para dúvidas de IRPF fundamentado em fontes oficiais da RFB.",
        version="0.1.0",
    )
    app.state.document_service = DocumentService(documents, settings.chunk_max_chars)
    app.state.ask_service = AskService(
        documents,
        answers,
        BM25Retriever(),
        provider or create_provider(settings),
        settings.default_top_k,
    )
    app.state.feedback_service = FeedbackService(answers, FeedbackRepository(conn))

    @app.get("/health", response_model=HealthResponse, tags=["infra"])
    def health() -> HealthResponse:
        """Indica se a API está no ar."""
        return HealthResponse(status="ok", timestamp=datetime.now(UTC))

    register_error_handlers(app)
    app.include_router(document_routes.router)
    app.include_router(ask_routes.router)
    app.include_router(feedback_routes.router)
    return app


app = create_app()
