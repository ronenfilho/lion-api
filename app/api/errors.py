"""Conversão central das exceções de domínio em respostas HTTP."""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import LionError, NotFoundError

STATUS_BY_ERROR: dict[type[LionError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
}


def register_error_handlers(app: FastAPI) -> None:
    """Registra um handler por família de exceção (subclasses herdam o status)."""
    for error_type, status_code in STATUS_BY_ERROR.items():
        app.add_exception_handler(error_type, _handler_for(status_code))


def _handler_for(status_code: int) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    """Cria o handler que devolve `{"detail": mensagem}` com o status dado."""

    async def handle(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return handle
