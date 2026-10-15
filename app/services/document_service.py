"""Regras de negócio de documentos."""

from app.repositories.document_repository import DocumentRepository
from app.schemas import DocumentCreate, DocumentOut
from app.services.chunking import split_into_chunks


class DocumentNotFoundError(Exception):
    """Documento inexistente."""


class DocumentService:
    """Ingestão, consulta e remoção de documentos."""

    def __init__(self, repository: DocumentRepository, chunk_max_chars: int = 800) -> None:
        self._repository = repository
        self._chunk_max_chars = chunk_max_chars

    def ingest(self, payload: DocumentCreate) -> DocumentOut:
        """Divide o conteúdo em trechos e persiste o documento."""
        chunks = split_into_chunks(payload.content, self._chunk_max_chars)
        return self._repository.create(payload.title, payload.source, chunks)

    def list_all(self) -> list[DocumentOut]:
        """Lista os documentos indexados."""
        return self._repository.list_all()

    def get(self, document_id: int) -> DocumentOut:
        """Retorna o documento ou levanta `DocumentNotFoundError`."""
        document = self._repository.get(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        return document

    def delete(self, document_id: int) -> None:
        """Remove o documento ou levanta `DocumentNotFoundError`."""
        if not self._repository.delete(document_id):
            raise DocumentNotFoundError(document_id)
