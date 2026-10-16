# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adota o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [1.0.0] - 2026-10-15

Entrega final: empacotamento, reprodutibilidade e documentação.

### Adicionado

- `Makefile` com os alvos `help` (padrão), `install`, `run`, `test`, `lint`, `format`, `load-sample`, `docker-build`, `docker-run` e `clean`, para macOS e Linux.
- `Dockerfile` (`python:3.12-slim`, usuário sem privilégios, só dependências de execução, `HEALTHCHECK` no `/health`, banco em volume `/data`) e `.dockerignore`.
- Job de CI que constrói a imagem Docker e faz smoke test (`/health`, carga do corpus e `/ask`).
- Variáveis `DEFAULT_TOP_K` (1 a 10) e `CHUNK_MAX_CHARS` (100 a 4000), validadas na inicialização com `ConfigError`, que nomeia a variável inválida.
- Teste que confere as rotas registradas em `app.main.app` (a aplicação servida pelo uvicorn) e testes de configuração e de versão no OpenAPI.
- `LICENSE` (MIT), este `CHANGELOG.md`, roteiro de demonstração (`docs/demo.md`) e checklist de entrega (`docs/entrega.md`).

### Alterado

- Versão em fonte única (`app.__version__`), lida pelo FastAPI, pelo `pyproject.toml` (versão dinâmica) e pelo Makefile.
- Dependências separadas em `requirements.txt` (execução) e `requirements-dev.txt` (testes e lint); CI e README ajustados.
- `DocumentRepository.create` monta o registro criado sem depender de `assert`.
- Variável de ambiente vazia passa a usar o valor padrão; `LLM_TIMEOUT_SECONDS` inválido ou não positivo gera `ConfigError`.
- README final orientado ao desenvolvedor: problema e solução, arquitetura em Mermaid, execução com Makefile e Docker, configuração, limites, próximos passos e uso de IA no desenvolvimento.

## [0.2.0] - 2026-10-15

Qualidade: guardrails, feedback, erros padronizados e CI.

### Adicionado

- Guardrail de entrada (RF05): bloqueia CPF, e-mail e telefone na pergunta e no comentário do feedback com 422, sem ecoar o dado.
- Guardrail de saída (RF06): remove citações inexistentes, renumera as válidas (`[i]` no texto é `citations[i-1]`) e troca resposta sem citação válida pela resposta padrão "não encontrei base".
- Feedback das respostas (RF07): `POST /answers/{answer_id}/feedback`.
- Exceções de domínio com handler central (`{"detail": "..."}`, 404 e 422).
- Testes do `AskService` com dublês e do `GroqProvider` com HTTP simulado (65 testes no total).
- GitHub Actions com `ruff check`, `ruff format --check` e `pytest` em Python 3.11 e 3.12.

### Corrigido

- BM25 sem resultado em corpus de 1 ou 2 trechos (IDF negativo); passa a usar o IDF do Lucene.
- Resposta do Groq com `content: null` gerava erro 500 em vez do fallback.
- Pergunta só com espaços passava pela validação de tamanho mínimo.
- Testes de ordenação e de remoção que não verificavam o que prometiam; testes passam a ser isolados do `.env` e do banco local.

## [0.1.0] - 2026-10-15

Core: primeira versão funcional da API.

### Adicionado

- `GET /health`.
- CRUD de documentos (`POST`, `GET` e `DELETE /documents`), com divisão em trechos e persistência em SQLite.
- `POST /ask`: busca BM25, geração por LLM com citações `[n]` e fallback para os trechos se o provedor falhar.
- Provedores de LLM `fake` (determinístico, sem rede) e `groq` (via `httpx`), com escolha por `.env`.
- Corpus de exemplo (Leis 9.250/1995 e 7.713/1988) e `scripts/load_sample.py`.
- Documentação de escopo, backlog, arquitetura, decisões técnicas e registro de prompts.

[Unreleased]: https://github.com/ronenfilho/lion-api/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ronenfilho/lion-api/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/ronenfilho/lion-api/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ronenfilho/lion-api/releases/tag/v0.1.0
