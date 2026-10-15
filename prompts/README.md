# Prompts usados no desenvolvimento

Registro dos pedidos feitos ao agente de código (Claude Code), em ordem, no formato CO-STAR quando aplicável.

## 01 — Bootstrap do repositório

- **Contexto:** novo repositório para expor o núcleo do projeto LION (RAG de IRPF) como API FastAPI, mini-projeto do Módulo 4 da especialização AKCIT.
- **Objetivo:** criar `.gitignore`, `.env.example`, `requirements.txt`, `pyproject.toml` (Ruff + pytest), `app/main.py` com `GET /health` (status + timestamp) e teste correspondente.
- **Estilo:** PEP 8, type hints, Pydantic, docstrings curtas.
- **Resposta:** criar os arquivos no repositório (não só mostrar o conteúdo).

## 02 — Documentação de planejamento

- **Contexto:** mesmo projeto; o LION original tem retrieval híbrido, guardrails, múltiplos provedores de LLM e avaliação RAGAS/BERTScore, num repo de 7 GB.
- **Objetivo:** gerar `docs/escopo-mvp.md` (objetivo, RF, RNF e **fora de escopo**), `docs/backlog.md` (releases Core / Qualidade / Final com critérios de aceite e códigos HTTP) e `docs/arquitetura.md` (diagrama Mermaid de componentes + fluxo do `/ask`).
- **Restrição:** escopo cabível em ~30h, sem dependências pesadas (torch/transformers).
- **Resposta:** arquivos Markdown no repositório e README inicial apontando para eles.

## 03 — Schemas Pydantic (aula 3.2, prompt 1)

- **Contexto:** API RAG de IRPF em FastAPI, release 0.1 (Core).
- **Objetivo:** criar `app/schemas.py` com `DocumentCreate`/`DocumentOut`, `AskRequest`/`AskResponse` e `Citation`, com limites de tamanho (pergunta de 3 a 500 caracteres, `top_k` de 1 a 10).
- **Estilo:** Pydantic v2 (`ConfigDict`, sem `class Config`), type hints e docstrings curtas.
- **Resposta:** criar o arquivo.

## 04 — Repositório SQLite (aula 3.2, prompt 2)

- **Contexto:** persistência enxuta para a primeira release.
- **Objetivo:** `app/repositories/` com conexão SQLite, esquema `documents`/`chunks`/`answers` e `DocumentRepository` (create, list_all, get, delete, all_chunks) e `AnswerRepository`.
- **Restrição:** só biblioteca padrão (`sqlite3`), sem ORM.

## 05 — Camada de LLM com fallback (aula 3.1, aula 3.2 prompt 4)

- **Contexto:** a IA em runtime não pode quebrar o fluxo principal. Os testes não podem depender de rede.
- **Objetivo:**
  - Interface `LLMProvider` e `LLMError`.
  - `FakeProvider` determinístico.
  - `GroqProvider` via `httpx`, com chave lida do `.env` e timeout.
  - Fábrica que cai para `fake` sem chave.
- **Observação:** criada **antes** do serviço de perguntas, para evitar a duplicação vista na aula 3.2.

## 06 — Busca e serviços (aula 3.2, prompt 3)

- **Objetivo:**
  - `chunking` por parágrafos (até 800 caracteres).
  - `BM25Retriever` com tokenização sem acentos e sem stopwords.
  - `DocumentService`.
  - `AskService`: recupera, gera, mantém só citações `[n]` válidas, devolve os trechos se o LLM falhar e registra a resposta.
- **Restrição:** regras de negócio fora das rotas.

## 07 — Rotas e montagem da aplicação (aula 3.2, prompt 5)

- **Objetivo:**
  - Routers separados (`/documents`, `/ask`) com 201/204/404/422 corretos.
  - `create_app(settings, provider)` com dependências injetáveis para os testes.

## 08 — Testes, corpus e revisão

- **Objetivo:**
  - Testes com pytest + TestClient (CRUD, ask com `fake`, provedor que falha, chunking, retriever, fábrica).
  - Corpus de exemplo com trechos das Leis 9.250/1995 e 7.713/1988 (textos legais, públicos).
  - Script `scripts/load_sample.py`.
  - Registro de decisões em `docs/decisoes.md`.
- **Revisão feita:**
  - O método `list` do repositório sobrescrevia o tipo `list` nas anotações da própria classe (`TypeError` ao importar). Renomeado para `list_all`.
  - Ruff format/check e 14 testes passando.
