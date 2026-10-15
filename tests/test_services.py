from app.config import Settings
from app.llm.factory import create_provider
from app.llm.fake import FakeProvider
from app.llm.groq import GroqProvider
from app.repositories.document_repository import StoredChunk
from app.services.chunking import split_into_chunks
from app.services.retriever import BM25Retriever, tokenize


def test_chunking_respeita_limite_e_preserva_texto() -> None:
    text = "\n\n".join(f"Parágrafo {i} " + "palavra " * 30 for i in range(10))

    chunks = split_into_chunks(text, max_chars=300)

    assert len(chunks) > 1
    assert all(len(c) <= 300 for c in chunks)
    assert " ".join(" ".join(chunks).split()) == " ".join(text.split())


def test_tokenize_remove_acentos_e_stopwords() -> None:
    assert tokenize("Dedução de Despesas Médicas") == ["deducao", "despesas", "medicas"]


RETRIEVER_CHUNKS = [
    StoredChunk(1, 1, "A", "despesas com instrução e educação"),
    StoredChunk(2, 1, "A", "despesas médicas com hospitais e dentistas"),
    StoredChunk(3, 2, "B", "pensão alimentícia por decisão judicial"),
    StoredChunk(4, 2, "B", "indenizações por acidentes de trabalho"),
    StoredChunk(5, 3, "C", "rendimentos de aposentadoria por moléstia grave"),
]


def test_retriever_ordena_por_relevancia_e_ignora_sem_match() -> None:
    results = BM25Retriever().search("despesas médicas", RETRIEVER_CHUNKS, top_k=5)

    assert [r.chunk.id for r in results] == [2, 1]
    assert results[0].score > results[1].score > 0


def test_retriever_respeita_top_k() -> None:
    results = BM25Retriever().search("despesas médicas", RETRIEVER_CHUNKS, top_k=1)

    assert [r.chunk.id for r in results] == [2]


def test_factory_sem_chave_cai_para_fake() -> None:
    provider = create_provider(Settings(llm_provider="groq", groq_api_key=""))

    assert isinstance(provider, FakeProvider)


def test_factory_com_chave_usa_groq() -> None:
    provider = create_provider(Settings(llm_provider="groq", groq_api_key="chave"))

    assert isinstance(provider, GroqProvider)


def test_retriever_encontra_trecho_em_corpus_com_um_so_trecho() -> None:
    chunks = [StoredChunk(1, 1, "A", "despesas médicas com hospitais e dentistas")]

    results = BM25Retriever().search("despesas médicas", chunks, top_k=3)

    assert [r.chunk.id for r in results] == [1]
