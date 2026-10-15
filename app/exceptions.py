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


class SensitiveDataError(LionError):
    """Texto com dado pessoal (CPF, e-mail ou telefone); a mensagem não ecoa o dado."""

    def __init__(self, kind: str, field: str = "pergunta") -> None:
        super().__init__(
            f"Bloqueado: o campo '{field}' parece conter dado pessoal ({kind}). "
            "A LION API não processa CPF, e-mail ou telefone; remova o dado e envie novamente."
        )
        self.kind = kind
        self.field = field


class AnswerNotFoundError(NotFoundError):
    """Resposta inexistente (ex.: feedback para um `answer_id` que não foi gerado)."""

    def __init__(self, answer_id: int) -> None:
        super().__init__(f"Resposta {answer_id} não encontrada.")
        self.answer_id = answer_id
