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

- [ ] Provedor real (`groq` já implementado na 0.1, falta testar com chave real; `gemini` opcional) configurável por `.env`, com fallback para `fake` se faltar chave.
- [ ] `Dockerfile` e instrução de execução.
- [ ] README completo (objetivo, stack, como rodar, exemplos `curl`, arquitetura, uso de IA no desenvolvimento).
- [ ] `prompts/` com os prompts usados no desenvolvimento.
- [ ] Repositório público, histórico em Conventional Commits, tag `v1.0.0`.
