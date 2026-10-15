# 🦁 LION API

API REST que responde dúvidas sobre **IRPF 2026** com base em fontes oficiais da Receita Federal, citando os trechos usados e aplicando guardrails contra alucinação e vazamento de dados pessoais.

MVP derivado do projeto de pesquisa [LION](https://github.com/ronenfilho/lion), desenvolvido como mini-projeto do Módulo 4 da especialização AKCIT/UFG *Engenharia de Software: Automação e Inovação com IA Generativa*.

> Status: **release 0.1 em andamento** — por enquanto só o `GET /health`. Ver [backlog](docs/backlog.md).

## Stack

FastAPI · Pydantic v2 · SQLite · BM25 · LLM via Groq/Gemini (ou provedor `fake` para testes) · pytest + HTTPX · Ruff

## Como rodar localmente

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # preencha as chaves se for usar um LLM real
uvicorn app.main:app --reload
```

- Health check: `curl http://localhost:8000/health`
- Documentação interativa: http://localhost:8000/docs

## Testes e lint

```bash
pytest
ruff check .
```

## Documentação

- [Escopo do MVP](docs/escopo-mvp.md)
- [Backlog por release](docs/backlog.md)
- [Arquitetura](docs/arquitetura.md)

## Uso de IA no desenvolvimento

Desenvolvido com apoio de agente de código (Claude Code), em ciclos curtos com revisão de diff, testes e commits pequenos. Os prompts usados ficam em [prompts/](prompts/).

## Aviso

Respostas são informativas e baseadas apenas nos documentos indexados; não substituem orientação contábil ou da Receita Federal.
