# Backlog por release — LION API

## Release 0.1 — Core

- [x] **RF01 — Health check**
  - `GET /health` retorna 200 com `status: "ok"` e `timestamp`.
- [x] **RF02 — Ingerir documento**
  - `POST /documents` com `title`, `source` e `content` retorna **201** com `id` e `chunk_count`.
  - Conteúdo vazio ou ausente retorna **422**.
- [x] **RF03 — Listar, consultar e remover documentos**
  - `GET /documents` retorna lista JSON.
  - `GET /documents/{id}` inexistente retorna **404**.
  - `DELETE /documents/{id}` retorna **204** e remove os trechos do índice.
- [x] **RF04 — Perguntar**
  - `POST /ask` com `question` retorna **200** com `answer_id`, `answer` e `citations` (`document_id`, `chunk_id`, `excerpt`).
  - Usa só os `k` trechos mais relevantes (BM25); `k` configurável.
- [x] **Corpus de exemplo** em `data/sample/` e script de carga (`scripts/load_sample.py`).

## Release 0.2 — Qualidade

- [x] **RF05 — Guardrail de entrada**
  - Pergunta vazia (ou só com espaços) ou com mais de 500 caracteres retorna **422**.
  - Pergunta com CPF (com ou sem pontuação), e-mail ou telefone retorna **422** com mensagem explicando o bloqueio, sem ecoar o dado (D08).
- [x] **RF06 — Guardrail de saída** (D09)
  - Sem trechos relevantes, retorna resposta padrão "não encontrei base nas fontes" e `citations: []`.
  - Citação que não corresponde a um trecho recuperado é descartada (e removida do texto).
  - Resposta sem nenhuma citação válida vira a resposta padrão, com `grounded: false`.
- [x] **RF07 — Feedback** (D11)
  - `POST /answers/{id}/feedback` com `useful` e `comment` opcional (até 500) retorna **201** com o registro; `answer_id` inexistente retorna **404**; comentário com dado pessoal retorna **422**.
- [x] Exceções de domínio com handler central e mensagens de erro claras (D07).
- [x] Suíte pytest cobrindo CRUD, ask (provedor `fake`), guardrails, feedback, `AskService` isolado, `GroqProvider` com HTTP simulado e cenários de erro (65 testes).
- [x] Ruff sem erros (lint + formatação); GitHub Actions rodando lint + testes em Python 3.11 e 3.12 a cada push/PR (`.github/workflows/ci.yml`).

## Release 1.0 — Entrega final

- [x] **Reprodutibilidade**
  - `Makefile` com `install`, `run`, `test`, `lint`, `format`, `load-sample`, `docker-build`, `docker-run`, `clean` e `help` (padrão), em macOS e Linux (D17).
  - Dependências de execução (`requirements.txt`) separadas das de desenvolvimento (`requirements-dev.txt`) (D16).
  - Setup validado em máquina limpa (servidor Linux, sem `.venv` prévio), seguindo só o README.
- [x] **Docker** (D18)
  - `Dockerfile` com `python:3.12-slim`, usuário sem privilégios, só dependências de execução, `HEALTHCHECK` no `/health` e banco em volume (`DATABASE_PATH=/data/lion.sqlite3`); `.dockerignore`.
  - Build e smoke test da imagem no CI (`/health`, carga do corpus e `/ask`).
- [x] **Configuração**
  - Versão em fonte única (`app.__version__`), exposta no `/openapi.json` (D14).
  - `DEFAULT_TOP_K` (1 a 10) e `CHUNK_MAX_CHARS` (100 a 4000) por ambiente; valor inválido impede a API de subir com `ConfigError` nomeando a variável (D15).
  - `DocumentRepository.create` sem `assert`.
- [x] **Aplicação montada:** teste que confere as rotas registradas em `app.main.app`, o objeto do uvicorn (D19).
- [x] **Documentação de entrega**
  - README final orientado ao desenvolvedor (problema e solução, Mermaid, como rodar e testar, endpoints com `curl`, configuração, limites e próximos passos, uso de IA no desenvolvimento).
  - `CHANGELOG.md` (Keep a Changelog), `LICENSE` (MIT), [roteiro de demo](demo.md) e [checklist de entrega](entrega.md) (D20).
  - `prompts/` com os prompts usados no desenvolvimento (01–24).
- [x] Varredura de segredos no histórico e na árvore, sem ocorrências.
- [x] Suíte com 83 testes; Ruff sem erros.
- [ ] Provedor real (`groq`) validado com chave real — implementado e testado com HTTP simulado; a validação com chave fica como próximo passo (`gemini` segue opcional).
- [ ] Tag `v1.0.0` no commit de entrega (repositório público e histórico em Conventional Commits já atendidos).
