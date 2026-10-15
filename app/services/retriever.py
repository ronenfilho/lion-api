"""Recuperação de trechos por BM25."""

import math
import re
import unicodedata
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from app.repositories.document_repository import StoredChunk

STOPWORDS = frozenset(
    "a o as os de da do das dos e em no na nos nas um uma por para com que se ao aos "
    "ou é como mais sua seu suas seus quando qual quais pelo pela pelos pelas".split()
)


@dataclass(frozen=True)
class ScoredChunk:
    """Trecho recuperado com sua pontuação BM25."""

    chunk: StoredChunk
    score: float


def tokenize(text: str) -> list[str]:
    """Minúsculas, sem acentos, sem pontuação e sem stopwords."""
    normalized = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(c for c in normalized if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9]+", without_accents) if t not in STOPWORDS]


class _PositiveIdfBM25(BM25Okapi):
    """BM25 com o IDF do Lucene, `log(1 + (N - n + 0.5) / (n + 0.5))`, sempre positivo.

    O IDF clássico do `BM25Okapi` fica negativo ou nulo quando o termo aparece em metade
    ou mais dos trechos — com corpus de 1 ou 2 trechos, nenhuma busca encontrava nada.
    """

    def _calc_idf(self, nd: dict[str, int]) -> None:
        for word, freq in nd.items():
            self.idf[word] = math.log(1 + (self.corpus_size - freq + 0.5) / (freq + 0.5))
        self.average_idf = sum(self.idf.values()) / len(self.idf) if self.idf else 0.0


class BM25Retriever:
    """Indexa os trechos a cada busca — suficiente para o corpus pequeno do MVP."""

    def search(self, query: str, chunks: list[StoredChunk], top_k: int) -> list[ScoredChunk]:
        """Retorna até `top_k` trechos com pontuação positiva, do mais ao menos relevante."""
        query_tokens = tokenize(query)
        if not chunks or not query_tokens:
            return []
        index = _PositiveIdfBM25([tokenize(chunk.text) for chunk in chunks])
        scores = index.get_scores(query_tokens)
        ranked = sorted(zip(chunks, scores, strict=True), key=lambda pair: pair[1], reverse=True)
        return [ScoredChunk(chunk, float(score)) for chunk, score in ranked[:top_k] if score > 0]
