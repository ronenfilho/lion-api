"""Rotas de documentos."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import get_document_service
from app.schemas import DocumentCreate, DocumentOut
from app.services.document_service import DocumentNotFoundError, DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])
Service = Annotated[DocumentService, Depends(get_document_service)]


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, service: Service) -> DocumentOut:
    """Indexa um documento em texto."""
    return service.ingest(payload)


@router.get("", response_model=list[DocumentOut])
def list_documents(service: Service) -> list[DocumentOut]:
    """Lista os documentos indexados."""
    return service.list_all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, service: Service) -> DocumentOut:
    """Detalha um documento."""
    try:
        return service.get(document_id)
    except DocumentNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento não encontrado") from None


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, service: Service) -> Response:
    """Remove o documento e seus trechos."""
    try:
        service.delete(document_id)
    except DocumentNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento não encontrado") from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
