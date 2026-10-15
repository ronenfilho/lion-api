"""Rota de feedback sobre as respostas."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_feedback_service
from app.schemas import FeedbackCreate, FeedbackOut
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/answers", tags=["feedback"])


@router.post(
    "/{answer_id}/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED
)
def create_feedback(
    answer_id: int,
    payload: FeedbackCreate,
    service: Annotated[FeedbackService, Depends(get_feedback_service)],
) -> FeedbackOut:
    """Registra se a resposta foi útil (404 se a resposta não existir)."""
    return service.register(answer_id, payload)
