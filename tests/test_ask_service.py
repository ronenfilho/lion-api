"""Testes do `AskService` isolado, com repositórios, busca e provedor dublês."""

import pytest

from app.exceptions import SensitiveDataError
from app.llm.base import LLMError
from app.repositories.document_repository import StoredChunk
from app.schemas import AskRequest
from app.services.ask_service import LLM_UNAVAILABLE_ANSWER, NO_BASIS_ANSWER, AskService
from app.services.retriever import ScoredChunk

RETRIEVED = [
    ScoredChunk(StoredChunk(10, 1, "Lei A", "Trecho sobre despesas médicas."), 2.0),
    ScoredChunk(StoredChunk(20, 2, "Lei B", "Trecho sobre educação."), 1.0),
]


class StubDocuments:
    def all_chunks(self) -> list[StoredChunk]:
        return [scored.chunk for scored in RETRIEVED]


class StubRetriever:
    def __init__(self, results: list[ScoredChunk]) -> None:
        self.results = results
        self.calls = 0

    def search(self, query: str, chunks: list[StoredChunk], top_k: int) -> list[ScoredChunk]:
        self.calls += 1
        return self.results[:top_k]


class SpyAnswers:
    def __init__(self) -> None:
        self.saved: list[tuple[str, str, bool, str]] = []

    def save(self, question: str, answer: str, grounded: bool, provider: str) -> int:
        self.saved.append((question, answer, grounded, provider))
        return len(self.saved)


class StubProvider:
    name = "stub"

    def __init__(self, answer: str | None = None, error: Exception | None = None) -> None:
        self.answer = answer
        self.error = error
        self.calls = 0

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if self.error:
            raise self.error
        return self.answer or ""


def make_service(
    provider: StubProvider, results: list[ScoredChunk] = RETRIEVED
) -> tuple[AskService, SpyAnswers, StubRetriever]:
    answers, retriever = SpyAnswers(), StubRetriever(results)
    service = AskService(StubDocuments(), answers, retriever, provider, default_top_k=4)
    return service, answers, retriever


def ask(service: AskService, question: str = "Posso deduzir despesas médicas?"):
    return service.ask(AskRequest(question=question))


def test_citacoes_seguem_ordem_da_resposta_sem_duplicar() -> None:
    service, _, _ = make_service(StubProvider("Educação [2]; saúde [1]; educação de novo [2]."))

    response = ask(service)

    assert [c.chunk_id for c in response.citations] == [20, 10]
    assert response.answer == "Educação [1]; saúde [2]; educação de novo [1]."
    assert response.grounded is True


def test_citacao_invalida_e_descartada() -> None:
    service, _, _ = make_service(StubProvider("Pode deduzir [1], conforme o trecho [3]."))

    response = ask(service)

    assert [c.chunk_id for c in response.citations] == [10]
    assert response.answer == "Pode deduzir [1], conforme o trecho."


def test_resposta_sem_citacao_valida_vira_resposta_sem_base() -> None:
    service, answers, _ = make_service(StubProvider("Pode deduzir tudo, sem limite [9]."))

    response = ask(service)

    assert response.grounded is False
    assert response.citations == []
    assert response.answer == NO_BASIS_ANSWER
    assert answers.saved[0][1:3] == (NO_BASIS_ANSWER, False)


def test_falha_do_provedor_devolve_trechos_recuperados() -> None:
    service, answers, _ = make_service(StubProvider(error=LLMError("timeout")))

    response = ask(service)

    assert response.answer == LLM_UNAVAILABLE_ANSWER
    assert [c.chunk_id for c in response.citations] == [10, 20]
    assert response.provider == "stub"
    assert len(answers.saved) == 1


def test_sem_trechos_recuperados_nao_chama_o_provedor() -> None:
    provider = StubProvider("não deveria ser usado [1]")
    service, _, _ = make_service(provider, results=[])

    response = ask(service)

    assert provider.calls == 0
    assert response.answer == NO_BASIS_ANSWER
    assert response.grounded is False


def test_pergunta_com_dado_pessoal_nao_busca_nao_gera_nem_grava() -> None:
    provider = StubProvider("resposta [1]")
    service, answers, retriever = make_service(provider)

    with pytest.raises(SensitiveDataError):
        ask(service, "Meu CPF é 123.456.789-09, tenho restituição?")

    assert (retriever.calls, provider.calls, answers.saved) == (0, 0, [])
