"""Divisão de documentos em trechos."""


def split_into_chunks(text: str, max_chars: int = 800) -> list[str]:
    """Agrupa parágrafos em trechos de até `max_chars` caracteres.

    Parágrafos maiores que o limite são quebrados por palavras.
    """
    paragraphs = [" ".join(p.split()) for p in text.split("\n\n")]
    pieces: list[str] = []
    for paragraph in filter(None, paragraphs):
        pieces.extend(_split_long(paragraph, max_chars))

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current}\n{piece}" if current else piece
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = piece
    if current:
        chunks.append(current)
    return chunks


def _split_long(paragraph: str, max_chars: int) -> list[str]:
    if len(paragraph) <= max_chars:
        return [paragraph]
    parts: list[str] = []
    current = ""
    for word in paragraph.split(" "):
        candidate = f"{current} {word}" if current else word
        if len(candidate) <= max_chars:
            current = candidate
        else:
            parts.append(current)
            current = word
    if current:
        parts.append(current)
    return parts
