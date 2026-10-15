"""Escolha do provedor de LLM a partir da configuração."""

import logging

from app.config import Settings
from app.llm.base import LLMProvider
from app.llm.fake import FakeProvider
from app.llm.groq import GroqProvider

logger = logging.getLogger(__name__)


def create_provider(settings: Settings) -> LLMProvider:
    """Retorna o provedor configurado; sem chave, cai para o `fake`."""
    if settings.llm_provider == "groq":
        if settings.groq_api_key:
            return GroqProvider(
                settings.groq_api_key, settings.groq_model, settings.llm_timeout_seconds
            )
        logger.warning("LLM_PROVIDER=groq sem GROQ_API_KEY; usando provedor fake.")
    elif settings.llm_provider != "fake":
        logger.warning("LLM_PROVIDER=%s não suportado; usando fake.", settings.llm_provider)
    return FakeProvider()
