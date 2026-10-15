"""Contratos de entrada e saída da API (Pydantic v2)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    """Documento a ser indexado (texto já extraído)."""

    title: str = Field(..., min_length=3, max_length=200, description="Título do documento")
    source: str = Field(
        ..., min_length=3, max_length=300, description="Origem oficial (URL ou referência)"
    )
    content: str = Field(..., min_length=20, description="Texto integral do documento")


class DocumentOut(BaseModel):
    """Documento indexado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str
    chunk_count: int
    created_at: datetime


class AskRequest(BaseModel):
    """Pergunta do usuário (espaços nas pontas são removidos antes de validar)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(..., min_length=3, max_length=500, description="Pergunta sobre IRPF")
    top_k: int | None = Field(None, ge=1, le=10, description="Quantidade de trechos recuperados")


class Citation(BaseModel):
    """Trecho de documento usado como base da resposta."""

    document_id: int
    document_title: str
    chunk_id: int
    excerpt: str
    score: float


class AskResponse(BaseModel):
    """Resposta gerada com as citações que a fundamentam."""

    answer_id: int
    answer: str
    grounded: bool = Field(..., description="Se a resposta se apoia em trechos recuperados")
    citations: list[Citation]
    provider: str
