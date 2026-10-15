"""Guardrails da LION API.

- Entrada: bloqueia dados pessoais antes de qualquer processamento.
- Saída: mantém só as citações `[n]` que apontam para trechos realmente recuperados.
"""

import re
from dataclasses import dataclass

from app.exceptions import SensitiveDataError

# Ordem importa: 11 dígitos seguidos são tratados como CPF antes de telefone.
PERSONAL_DATA_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("CPF", re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")),
    ("e-mail", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    (
        "telefone",
        re.compile(
            # Com DDD (e DDI opcional): fixo [2-5]xxx-xxxx ou celular 9xxxx-xxxx.
            r"(?<!\d)(?:\+?55[\s-]?)?\(?\d{2}\)?[\s-]?(?:9\d{4}|[2-5]\d{3})[\s-]?\d{4}(?!\d)"
            # Sem DDD, só celular (9 dígitos): evita confundir com intervalos como 2025-2026.
            r"|(?<!\d)9\d{4}[\s-]?\d{4}(?!\d)"
        ),
    ),
)


def detect_personal_data(text: str) -> str | None:
    """Retorna o tipo de dado pessoal encontrado (`CPF`, `e-mail`, `telefone`) ou None."""
    for kind, pattern in PERSONAL_DATA_PATTERNS:
        if pattern.search(text):
            return kind
    return None


def ensure_no_personal_data(text: str, field: str = "pergunta") -> None:
    """Levanta `SensitiveDataError` se o texto contiver dado pessoal."""
    kind = detect_personal_data(text)
    if kind is not None:
        raise SensitiveDataError(kind, field)


CITATION_PATTERN = re.compile(r"(\s*)\[(\d+)\]")


@dataclass(frozen=True)
class CheckedAnswer:
    """Resposta com citações conferidas.

    `sources` traz os índices (base 0) dos trechos citados, na ordem da primeira citação;
    no texto, `[i]` passa a apontar para `sources[i - 1]`.
    """

    text: str
    sources: list[int]


def check_citations(answer: str, available: int) -> CheckedAnswer:
    """Descarta citações inexistentes e renumera as válidas na ordem em que aparecem."""
    renumbered: dict[int, int] = {}

    def replace(match: re.Match[str]) -> str:
        spaces, number = match.group(1), int(match.group(2))
        if not 1 <= number <= available:
            return ""
        new_number = renumbered.setdefault(number, len(renumbered) + 1)
        return f"{spaces}[{new_number}]"

    text = CITATION_PATTERN.sub(replace, answer)
    return CheckedAnswer(text=text, sources=[number - 1 for number in renumbered])
