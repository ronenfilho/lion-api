"""Rota de perguntas."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_ask_service
from app.schemas import AskRequest, AskResponse
from app.services.ask_service import AskService

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest, service: Annotated[AskService, Depends(get_ask_service)]
) -> AskResponse:
    """Responde a uma pergunta sobre IRPF citando os trechos usados."""
    return service.ask(payload)
