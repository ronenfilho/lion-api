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

## 17 — Planejamento da release 1.0 (aulas da Unidade 5)

- **Contexto:** release 0.2 publicada (tag `v0.2.0`, 65 testes, CI em 3.11/3.12). A Unidade 5 pede entrega reprodutível em máquina limpa, Makefile, README final orientado ao desenvolvedor, checklist de submissão e roteiro de demo de 3–5 min.
- **Objetivo:** implementar a 1.0 (Entrega final): versão em fonte única, configuração por ambiente, teste de rotas registradas, Makefile, Docker, varredura de segredos, README, CHANGELOG, LICENSE, demo, checklist e atualização dos docs.
- **Estilo:** o do código existente, sem dependências novas salvo indispensável.
- **Resposta:** alterações no working tree, sem commit, tag nem push; proposta de commits (Conventional Commits) com a árvore de cada passo verificada (`ruff` + `pytest`).

## 18 — Versão única e configuração validada

- **Objetivo:** `app.__version__` como fonte única (FastAPI, `pyproject.toml` dinâmico, Makefile) e teste de que o `/openapi.json` a expõe; `DEFAULT_TOP_K` e `CHUNK_MAX_CHARS` por ambiente com validação; remover o `assert` de `DocumentRepository.create`.
- **Revisão feita:**
  - `importlib.metadata` foi descartado: o projeto não é instalado como pacote, e a leitura dependeria de um `pip install -e .` que ninguém roda (D14). A versão dinâmica do `pyproject.toml` foi conferida gerando o *wheel* num ambiente separado.
  - O `assert` não foi trocado por um `if ... raise`: o registro criado passou a ser montado direto (como no `FeedbackRepository`), o que elimina o caminho de erro e uma consulta.
  - O primeiro teste de `DEFAULT_TOP_K` passava por acaso: o provedor `fake` cita só um trecho, então `citations` teria 1 item com qualquer `top_k`. Refeito com um provedor que falha (o fallback devolve todos os trechos recuperados), comparando `top_k` 1 e 3.
  - `LLM_TIMEOUT_SECONDS` vazio derrubava a API com `ValueError` cru; agora vazio usa o padrão e valor inválido gera `ConfigError` com o nome da variável (D15).

## 19 — Teste da aplicação montada (lição da aula 5.2)

- **Contexto:** na aula, os testes passavam com o router fora do `main`. Aqui, todos os testes usavam `create_app` com banco temporário; nenhum olhava o `app.main.app`.
- **Objetivo:** teste que compara as rotas de `app.main.app` com a lista esperada e chama `/health` e `/openapi.json` nessa aplicação.
- **Revisão feita:** conferido que o teste falha removendo `include_router(feedback_routes.router)` do `main` (os dois testes novos ficaram vermelhos), e restaurado em seguida (D19).

## 20 — Dependências e Makefile

- **Objetivo:** separar `requirements.txt` (execução) de `requirements-dev.txt` (pytest e Ruff) e **criar o arquivo** `Makefile` no repositório com `help` (padrão), `install`, `run`, `test`, `lint`, `format`, `load-sample`, `docker-build`, `docker-run` e `clean`, usando `.venv` e só ferramentas POSIX (macOS e Linux).
- **Revisão feita:** o `help` imprimia `$(HOST):$(PORT)` literalmente, porque o texto vem dos comentários `##` lidos pelo `awk`, sem expansão do make; as descrições passaram a ter texto fixo. O README dizia `pip install -r requirements.txt` seguido de `pytest`, o que deixaria de funcionar com a separação; ajustado no mesmo passo.

## 21 — Docker

- **Objetivo:** `Dockerfile` com `python:3.12-slim`, usuário sem privilégios, só dependências de execução, `HEALTHCHECK` no `/health` e `DATABASE_PATH` em volume; `.dockerignore`; job de CI com build e smoke test.
- **Revisão feita:** a imagem slim não tem `curl`, então o `HEALTHCHECK` usa `urllib`. No smoke test, o `curl --retry-connrefused` não cobre a conexão resetada pelo proxy do Docker enquanto o uvicorn sobe (`curl: (56) Recv failure`, visto na validação); o CI usa `--retry-all-errors` (D18).

## 22 — Validação em máquina limpa e da imagem

- **Objetivo:** copiar a árvore de trabalho para um diretório temporário num servidor Linux (Ubuntu, Python 3.12.3, sem `.venv`), seguir só o README (`make install`, `make test`, `make lint`, `make run` + `make load-sample`) e validar a imagem (`make docker-build`, `make docker-run`, smoke test com `curl`), removendo container, imagem, volume e diretório no fim.
- **Resultado:** 83 testes verdes e Ruff sem erros no ambiente novo; API respondendo `/health`, `/ask` com citação, "não encontrei base" para pergunta fora do corpus e 404 de feedback. No container: `/health` ok, `HEALTHCHECK` `healthy`, processo como `lion` (uid 10001), banco em `/data` e documentos preservados após reiniciar o container com o mesmo volume; `/openapi.json` com versão `1.0.0`; CPF bloqueado com 422.

## 23 — Varredura de segredos

- **Objetivo:** procurar no histórico (todas as refs, reflog e objetos inalcançáveis) e na árvore padrões de chave (`gsk_`, `AIza`, `sk-`, `AKIA`, chaves privadas, `api_key=`/`token=`/`secret=` com valor, `Bearer`) e conferir se algum `.env` foi versionado.
- **Resultado:** nenhuma ocorrência; o único arquivo `.env*` no histórico é o `.env.example`, sem valores.

## 24 — README final, CHANGELOG, licença, demo e checklist

- **Objetivo:** README orientado ao desenvolvedor (problema e solução, Mermaid embutido, stack, como rodar com Makefile e Docker, testes, endpoints com `curl`, configuração, limites e próximos passos, uso de IA com os bugs reais encontrados na revisão), `CHANGELOG.md` (Keep a Changelog + SemVer), `LICENSE` MIT, `docs/demo.md` (3–5 min), `docs/entrega.md` e atualização de backlog, decisões (D14–D20) e arquitetura.
- **Restrição:** texto objetivo, exemplos copiados de uma execução real (não inventados), sem criar tag nem release.
