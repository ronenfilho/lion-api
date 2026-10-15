"""Prompts do RAG."""

from app.repositories.document_repository import StoredChunk

SYSTEM_PROMPT = (
    "Você é o LION, assistente sobre Imposto de Renda da Pessoa Física (IRPF). "
    "Responda em português, de forma objetiva, usando APENAS os trechos fornecidos. "
    "Cite cada afirmação com o número do trecho entre colchetes, por exemplo [1]. "
    "Se os trechos não bastarem para responder, diga que não encontrou base nas fontes. "
    "Não invente valores, prazos ou artigos."
)


def build_user_prompt(question: str, chunks: list[StoredChunk]) -> str:
    """Monta o prompt com os trechos numerados a partir de 1."""
    trechos = "\n".join(
        f"[{i}] {chunk.text} (Fonte: {chunk.document_title})"
        for i, chunk in enumerate(chunks, start=1)
    )
    return f"Trechos:\n{trechos}\n\nPergunta: {question}"
