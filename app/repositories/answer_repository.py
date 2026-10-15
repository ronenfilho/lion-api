"""Persistência das respostas geradas (alvo do feedback)."""

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

    def exists(self, answer_id: int) -> bool:
        """Indica se a resposta foi registrada."""
        row = self._conn.execute("SELECT 1 FROM answers WHERE id = ?", (answer_id,)).fetchone()
        return row is not None
