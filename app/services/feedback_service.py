"""Regras de negócio do feedback."""

from app.exceptions import AnswerNotFoundError
from app.repositories.answer_repository import AnswerRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas import FeedbackCreate, FeedbackOut
from app.services.guardrails import ensure_no_personal_data


class FeedbackService:
    """Registra a avaliação de uma resposta existente."""

    def __init__(self, answers: AnswerRepository, feedback: FeedbackRepository) -> None:
        self._answers = answers
        self._feedback = feedback

    def register(self, answer_id: int, payload: FeedbackCreate) -> FeedbackOut:
        """Grava o feedback.

        Levanta `SensitiveDataError` se o comentário tiver dado pessoal e
        `AnswerNotFoundError` se a resposta não existir.
        """
        comment = payload.comment or None
        if comment:
            ensure_no_personal_data(comment, field="comment")
        if not self._answers.exists(answer_id):
            raise AnswerNotFoundError(answer_id)
        return self._feedback.create(answer_id, payload.useful, comment)
