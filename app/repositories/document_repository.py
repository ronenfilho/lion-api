"""Persistência de documentos e trechos."""

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from app.schemas import DocumentOut

DOCUMENT_SELECT = """
SELECT d.id, d.title, d.source, d.created_at, COUNT(c.id) AS chunk_count
FROM documents d LEFT JOIN chunks c ON c.document_id = d.id
"""


@dataclass(frozen=True)
class StoredChunk:
    """Trecho indexado com o título do documento de origem."""

    id: int
    document_id: int
    document_title: str
    text: str


class DocumentRepository:
    """CRUD de documentos e leitura dos trechos para a busca."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(self, title: str, source: str, chunks: list[str]) -> DocumentOut:
        """Grava o documento e seus trechos numa única transação."""
        now = datetime.now(UTC).isoformat()
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO documents (title, source, created_at) VALUES (?, ?, ?)",
                (title, source, now),
            )
            document_id = cur.lastrowid
            self._conn.executemany(
                "INSERT INTO chunks (document_id, position, text) VALUES (?, ?, ?)",
                [(document_id, i, text) for i, text in enumerate(chunks)],
            )
        document = self.get(document_id)
        assert document is not None
        return document

    def list_all(self) -> list[DocumentOut]:
        """Lista todos os documentos, do mais antigo ao mais novo."""
        rows = self._conn.execute(DOCUMENT_SELECT + " GROUP BY d.id ORDER BY d.id").fetchall()
        return [DocumentOut.model_validate(dict(row)) for row in rows]

    def get(self, document_id: int) -> DocumentOut | None:
        """Busca um documento pelo id."""
        row = self._conn.execute(
            DOCUMENT_SELECT + " WHERE d.id = ? GROUP BY d.id", (document_id,)
        ).fetchone()
        return DocumentOut.model_validate(dict(row)) if row else None

    def delete(self, document_id: int) -> bool:
        """Remove o documento e seus trechos; retorna False se não existia."""
        with self._conn:
            cur = self._conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return cur.rowcount > 0

    def all_chunks(self) -> list[StoredChunk]:
        """Retorna todos os trechos indexados (insumo do retriever)."""
        rows = self._conn.execute(
            "SELECT c.id, c.document_id, d.title AS document_title, c.text "
            "FROM chunks c JOIN documents d ON d.id = c.document_id ORDER BY c.id"
        ).fetchall()
        return [StoredChunk(**dict(row)) for row in rows]
