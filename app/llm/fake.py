"""Provedor determinístico, sem rede — usado nos testes e como fallback."""

import re

TRECHO_PATTERN = re.compile(r"^\[(\d+)\] (.+)$", re.MULTILINE)


class FakeProvider:
    """Responde com a primeira frase do trecho mais relevante, citando-o."""

    name = "fake"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Extrai o primeiro trecho numerado do prompt e devolve um resumo citado."""
        match = TRECHO_PATTERN.search(user_prompt)
        if match is None:
            return "Não encontrei base nas fontes indexadas para responder."
        number, text = match.groups()
        first_sentence = re.split(r"(?<=[.;:])\s", text.strip(), maxsplit=1)[0]
        return f"Segundo as fontes, {first_sentence} [{number}]"
