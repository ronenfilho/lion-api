"""Provedor Groq (API compatível com OpenAI) via httpx, sem SDK."""

import httpx

from app.llm.base import LLMError

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider:
    """Chama o endpoint de chat completions da Groq."""

    name = "groq"

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 20.0) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_seconds

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Envia o prompt e devolve o texto gerado; erros viram `LLMError`."""
        payload = {
            "model": self._model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        try:
            response = httpx.post(
                GROQ_URL,
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=self._timeout,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise LLMError(f"Falha no provedor Groq: {exc.__class__.__name__}") from exc
