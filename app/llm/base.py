"""Contrato comum dos provedores de LLM."""

from typing import Protocol


class LLMError(Exception):
    """Falha ao gerar resposta no provedor (timeout, HTTP, payload inesperado)."""


class LLMProvider(Protocol):
    """Provedor capaz de gerar texto a partir de um prompt."""

    name: str

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Gera a resposta; deve levantar `LLMError` em caso de falha."""
        ...
