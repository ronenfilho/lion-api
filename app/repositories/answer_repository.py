"""Persistência das respostas geradas (base para o feedback da release 0.2)."""

import sqlite3
from datetime import UTC, datetime


class AnswerRepository:
    """Registra cada resposta devolvida pelo `/ask`."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, question: str, answer: str, grounded: bool, provider: str) -> int:
        """Grava a resposta e devolve o id gerado."""
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO answers (question, answer, grounded, provider, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (question, answer, int(grounded), provider, datetime.now(UTC).isoformat()),
            )
        return cur.lastrowid
