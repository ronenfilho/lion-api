"""Fluxo de pergunta e resposta (RAG)."""

import logging

from app.llm.base import LLMError, LLMProvider
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.repositories.answer_repository import AnswerRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas import AskRequest, AskResponse, Citation
from app.services.guardrails import check_citations, ensure_no_personal_data
from app.services.retriever import BM25Retriever, ScoredChunk

logger = logging.getLogger(__name__)

NO_BASIS_ANSWER = "Não encontrei base nas fontes indexadas para responder a essa pergunta."
LLM_UNAVAILABLE_ANSWER = (
    "O serviço de geração está indisponível no momento. "
    "Seguem os trechos mais relevantes encontrados nas fontes."
)
EXCERPT_MAX_CHARS = 300


class AskService:
    """Recupera trechos, gera a resposta e registra o resultado."""

    def __init__(
        self,
        documents: DocumentRepository,
        answers: AnswerRepository,
        retriever: BM25Retriever,
        provider: LLMProvider,
        default_top_k: int = 4,
    ) -> None:
        self._documents = documents
        self._answers = answers
        self._retriever = retriever
        self._provider = provider
        self._default_top_k = default_top_k

    def ask(self, request: AskRequest) -> AskResponse:
        """Responde à pergunta com base nos trechos recuperados.

        Levanta `SensitiveDataError` (sem gravar nada) se a pergunta tiver dado pessoal.
        """
        ensure_no_personal_data(request.question)
        top_k = request.top_k or self._default_top_k
        retrieved = self._retriever.search(request.question, self._documents.all_chunks(), top_k)

        if not retrieved:
            return self._finish(request.question, NO_BASIS_ANSWER, [], grounded=False)

        user_prompt = build_user_prompt(request.question, [r.chunk for r in retrieved])
        try:
            answer = self._provider.generate(SYSTEM_PROMPT, user_prompt)
        except LLMError:
            logger.exception("Falha no provedor %s; devolvendo só os trechos.", self._provider.name)
            return self._finish(request.question, LLM_UNAVAILABLE_ANSWER, retrieved, grounded=True)

        checked = check_citations(answer, len(retrieved))
        if not checked.sources:
            return self._finish(request.question, NO_BASIS_ANSWER, [], grounded=False)
        cited = [retrieved[i] for i in checked.sources]
        return self._finish(request.question, checked.text, cited, grounded=True)

    def _finish(
        self, question: str, answer: str, chunks: list[ScoredChunk], grounded: bool
    ) -> AskResponse:
        answer_id = self._answers.save(question, answer, grounded, self._provider.name)
        citations = [
            Citation(
                document_id=c.chunk.document_id,
                document_title=c.chunk.document_title,
                chunk_id=c.chunk.id,
                excerpt=c.chunk.text[:EXCERPT_MAX_CHARS],
                score=round(c.score, 4),
            )
            for c in chunks
        ]
        return AskResponse(
            answer_id=answer_id,
            answer=answer,
            grounded=grounded,
            citations=citations,
            provider=self._provider.name,
        )
