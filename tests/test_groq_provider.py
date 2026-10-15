"""Testes do `GroqProvider` com HTTP simulado (`httpx.MockTransport`), sem rede."""

import json
from collections.abc import Callable

import httpx
import pytest

from app.llm.base import LLMError
from app.llm.groq import GROQ_URL, GroqProvider

Handler = Callable[[httpx.Request], httpx.Response]


def make_provider(handler: Handler) -> GroqProvider:
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return GroqProvider("chave-de-teste", "modelo-x", timeout_seconds=5, client=client)


def chat_response(content: object) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})


def test_sucesso_envia_prompt_autenticado_e_devolve_texto() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return chat_response("  Pode deduzir [1].  ")

    answer = make_provider(handler).generate("sistema", "usuário")

    assert answer == "Pode deduzir [1]."
    sent = requests[0]
    body = json.loads(sent.content)
    assert str(sent.url) == GROQ_URL
    assert sent.headers["Authorization"] == "Bearer chave-de-teste"
    assert body["model"] == "modelo-x"
    assert body["messages"] == [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "usuário"},
    ]


def raise_timeout(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("demorou", request=request)


@pytest.mark.parametrize(
    "handler",
    [
        pytest.param(raise_timeout, id="timeout"),
        pytest.param(lambda request: httpx.Response(500, text="erro"), id="http-500"),
        pytest.param(lambda request: httpx.Response(200, text="<html>"), id="nao-json"),
        pytest.param(lambda request: httpx.Response(200, json={"foo": 1}), id="sem-choices"),
        pytest.param(lambda request: httpx.Response(200, json={"choices": []}), id="choices-vazio"),
        pytest.param(lambda request: chat_response(None), id="content-nulo"),
        pytest.param(lambda request: chat_response("   "), id="content-vazio"),
    ],
)
def test_falhas_viram_llm_error(handler: Handler) -> None:
    with pytest.raises(LLMError, match="Groq"):
        make_provider(handler).generate("sistema", "usuário")
