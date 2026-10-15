"""Persistência do feedback sobre as respostas."""

import sqlite3
from datetime import UTC, datetime

from app.schemas import FeedbackOut


class FeedbackRepository:
    """Grava as avaliações das respostas."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(self, answer_id: int, useful: bool, comment: str | None) -> FeedbackOut:
        """Grava o feedback e devolve o registro criado."""
        created_at = datetime.now(UTC)
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO feedback (answer_id, useful, comment, created_at) VALUES (?, ?, ?, ?)",
                (answer_id, int(useful), comment, created_at.isoformat()),
            )
        return FeedbackOut(
            id=cur.lastrowid,
            answer_id=answer_id,
            useful=useful,
            comment=comment,
            created_at=created_at,
        )
