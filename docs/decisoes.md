# Registro de decisões técnicas

## D01 — Busca por BM25, sem embeddings (release 0.1)
- **Contexto:** o LION original usa busca híbrida (densa + BM25) com sentence-transformers, torch e ChromaDB, uma pilha pesada para um MVP de ~30h.
- **Decisão:** usar só BM25 (`rank-bm25`), com tokenização sem acentos e sem stopwords. O índice é recalculado a cada busca.
- **Consequências:** instalação leve, testes rápidos e determinísticos. Recalcular o índice só é viável com corpus pequeno. Busca semântica fica como candidata à 1.0.

## D02 — SQLite como persistência
- **Contexto:** a aula 3.1 recomenda persistência simples. Em memória perderia os documentos ao reiniciar.
- **Decisão:** SQLite com tabelas `documents`, `chunks` (com `ON DELETE CASCADE`) e `answers`, via `sqlite3` da biblioteca padrão.
- **Consequências:** sem ORM nem dependência extra. Para produção real, migrar para Postgres.

## D03 — Camada `llm` com provedor `fake` e fallback
- **Contexto:** a IA em runtime não pode derrubar o fluxo principal (aula 3.1), e os testes não podem depender de rede nem de chave.
- **Decisão:** interface `LLMProvider` com `FakeProvider` (determinístico) e `GroqProvider`.
  - Sem chave configurada, a fábrica cai para o `fake`.
  - Se o provedor falhar (`LLMError`), o `/ask` devolve os trechos recuperados com um aviso, em vez de erro 500.
- **Consequências:** trocar ou adicionar provedor (ex.: Gemini) é só uma nova classe.

## D04 — Groq via `httpx`, sem SDK
- **Decisão:** chamar o endpoint OpenAI-compatível da Groq com `httpx`, que já é dependência dos testes.
- **Consequências:** uma dependência a menos e erro de rede tratado num só lugar. Perde-se a tipagem do SDK.

## D05 — `create_app` com dependências injetáveis
- **Decisão:** a aplicação é montada por `create_app(settings, provider)`. Os serviços ficam em `app.state` e as rotas os obtêm via `Depends`.
- **Consequências:** cada teste usa um banco temporário e o provedor que quiser (inclusive um que falha), sem *monkeypatch*.

## D06 — Citações validadas pelo número do trecho
- **Decisão:** o prompt numera os trechos ([1], [2]…) e exige citação. O serviço mantém só as citações que apontam para trechos realmente recuperados. Sem nenhuma citação válida, `grounded=false`.
- **Consequências:** é a base do guardrail de saída (RF06), que será completado na 0.2.
