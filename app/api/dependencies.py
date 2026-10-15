"""Acesso aos serviços montados em `create_app` (injeção via FastAPI)."""

from fastapi import Request

from app.services.ask_service import AskService
from app.services.document_service import DocumentService
from app.services.feedback_service import FeedbackService


def get_document_service(request: Request) -> DocumentService:
    """Serviço de documentos da aplicação corrente."""
    return request.app.state.document_service


def get_ask_service(request: Request) -> AskService:
    """Serviço de perguntas da aplicação corrente."""
    return request.app.state.ask_service


def get_feedback_service(request: Request) -> FeedbackService:
    """Serviço de feedback da aplicação corrente."""
    return request.app.state.feedback_service
