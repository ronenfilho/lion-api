"""Exceções de domínio da LION API.

As camadas de serviço levantam estas exceções; a camada de API as converte em
respostas HTTP num único lugar (`app/api/errors.py`).
"""


class LionError(Exception):
    """Base das falhas de regra de negócio, com mensagem pronta para o cliente."""


class NotFoundError(LionError):
    """Recurso inexistente."""


class DocumentNotFoundError(NotFoundError):
    """Documento inexistente."""

    def __init__(self, document_id: int) -> None:
        super().__init__(f"Documento {document_id} não encontrado.")
        self.document_id = document_id
