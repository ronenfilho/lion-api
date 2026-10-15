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

## 09 — Planejamento da release 0.2 (aulas da Unidade 4)

- **Contexto:** release 0.1 concluída (CRUD, BM25, `/ask` com fallback, 14 testes). A Unidade 4 pede TDD, exceções customizadas, revisão crítica de testes, DRY/SRP e CI.
- **Objetivo:** implementar a 0.2 (Qualidade) conforme os critérios de aceite do `docs/backlog.md`: guardrail de entrada (RF05), guardrail de saída (RF06), feedback (RF07), testes que faltam, CI e documentação.
- **Estilo:** o do código existente (docstrings curtas em português, type hints, Pydantic v2, camadas api → services → repositories), sem dependências novas.
- **Resposta:** alterações no working tree, sem commit; ao final, proposta de divisão em commits (Conventional Commits) para revisão humana.

## 10 — Refatoração: exceções de domínio e handler central (aula 4.1)

- **Contexto:** as rotas de documentos repetiam `try/except DocumentNotFoundError` → 404, e a 0.2 traria mais erros do mesmo tipo.
- **Objetivo:** criar `app/exceptions.py` (`LionError`, `NotFoundError`, `DocumentNotFoundError`) e um handler central em `app/api/errors.py`, removendo o tratamento das rotas.
- **Restrição:** refatoração separada de funcionalidade, com os testes verdes antes e depois; só um teste novo para fixar a mensagem do 404.

## 11 — Revisão crítica dos testes existentes

- **Objetivo:** apontar testes que passam sem testar de fato o que prometem e corrigi-los.
- **Revisão feita:**
  - `test_retriever_ordena_por_relevancia…` tinha só um trecho com match: **não testava ordenação**. Agora há dois trechos relevantes com pontuações diferentes, e um teste separado para `top_k`.
  - O teste de remoção não verificava que os trechos **saíam do índice** (critério do RF03). Agora pergunta antes e depois do `DELETE`.
  - Ao escrever esse teste, apareceu um **bug real**: com um único trecho indexado, o IDF do `BM25Okapi` fica negativo e nenhuma busca retorna nada. Corrigido com IDF do Lucene, em TDD (teste vermelho primeiro) e em commit próprio (D10).
  - `test_health` usava a aplicação montada no import de `app.main`, que lia o `.env` e criava `var/lion.sqlite3` do desenvolvedor. Passou a usar a fixture, e o `conftest.py` isola o ambiente (D13).
  - O teste de falha do provedor não conferia status nem provedor; agora confere.

## 12 — RF05: guardrail de entrada em TDD

- **Contexto:** a API não pode processar dados pessoais (LGPD), e a mensagem de bloqueio não pode repetir o dado.
- **Objetivo:** primeiro os testes (CPF com e sem pontuação, e-mail, telefones com e sem DDD/DDI, perguntas limpas com valores, leis e "2025-2026"; API devolvendo 422 sem ecoar o dado), rodados no vermelho; depois `app/services/guardrails.py` e `SensitiveDataError` mapeada para 422.
- **Restrição:** aplicar no serviço, antes de buscar, chamar o LLM ou gravar.
- **Revisão feita:** a pergunta só com espaços passava pelo `min_length=3`; corrigido com `str_strip_whitespace`. Telefone sem DDD passou a exigir o 9 inicial para não bloquear intervalos de anos.

## 13 — RF06: guardrail de saída e testes isolados do `AskService`

- **Objetivo:** testes do `AskService` com dublês (repositórios, busca e provedor) para citação inválida, ordem e deduplicação de citações, resposta sem citação válida, falha do provedor, ausência de trechos e pergunta com dado pessoal.
- **Revisão feita:** os testes mostraram três lacunas da 0.1 (D09): a citação inválida sumia da lista mas ficava no texto; o `[n]` do texto não correspondia à posição na lista `citations`; e resposta sem nenhuma citação válida era devolvida como veio. A conferência saiu do `AskService` para `check_citations` (SRP), que renumera, remove inválidas e permite trocar a resposta não fundamentada pela resposta padrão.

## 14 — RF07: feedback em TDD

- **Objetivo:** testes primeiro para `POST /answers/{answer_id}/feedback` (201 com e sem comentário, 404 para resposta inexistente, 422 para payload inválido, comentário acima de 500 e comentário com dado pessoal); depois tabela `feedback`, `FeedbackRepository`, `FeedbackService`, `AnswerNotFoundError` e a rota.
- **Restrição:** regra de existência da resposta no serviço, não na rota; erro via handler central.

## 15 — Testes do `GroqProvider` com HTTP simulado

- **Objetivo:** cobrir sucesso (cabeçalho de autenticação, modelo e mensagens enviados), timeout, HTTP 500, corpo não JSON, payload sem `choices`, `choices` vazio, `content` nulo e vazio — todos como `LLMError` — sem rede, com `httpx.MockTransport`.
- **Revisão feita:** o provedor chamava `httpx.post` direto, sem ponto de injeção; passou a aceitar um `httpx.Client`. Os testes revelaram que `content: null` gerava `AttributeError` fora do `except`, que viraria **500** no `/ask` em vez do fallback. Corrigido (D12).

## 16 — CI e documentação

- **Objetivo:** `.github/workflows/ci.yml` com `ruff check`, `ruff format --check` e `pytest` em Python 3.11 e 3.12 a cada push/PR; atualizar backlog, decisões (D07–D13), arquitetura (fluxo e tabela de erros) e README (endpoints, exemplos, **Limites** e **Como a IA foi usada no desenvolvimento**).
- **Revisão feita:** suíte rodada também em Python 3.11 localmente antes de publicar o workflow; smoke test com `uvicorn` cobrindo 422 por dado pessoal e feedback 201/404.
