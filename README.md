# 🦁 LION API

API REST que responde dúvidas sobre **IRPF 2026** com base em fontes oficiais da Receita Federal, citando os trechos usados e aplicando guardrails contra alucinação e vazamento de dados pessoais.

MVP derivado do projeto de pesquisa [LION](https://github.com/ronenfilho/lion), desenvolvido como mini-projeto do Módulo 4 da especialização AKCIT/UFG *Engenharia de Software: Automação e Inovação com IA Generativa*.

> Status: **release 0.1 (Core) concluída** — documentos, busca BM25 e `/ask` com citações. Próxima: 0.2 (guardrails, feedback, CI). Ver [backlog](docs/backlog.md).

## Stack

FastAPI · Pydantic v2 · SQLite · BM25 · LLM via Groq (ou provedor `fake`, sem rede, para testes e fallback) · pytest + HTTPX · Ruff

## Como rodar localmente

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # preencha as chaves se for usar um LLM real
uvicorn app.main:app --reload
```

Em outro terminal, carregue o corpus de exemplo (trechos das Leis 9.250/1995 e 7.713/1988) e faça uma pergunta:

```bash
python scripts/load_sample.py
curl -s -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "Qual o limite de dedução com educação?"}'
```

- Health check: `curl http://localhost:8000/health`
- Documentação interativa (Swagger): http://localhost:8000/docs

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Status da API |
| POST | `/documents` | Indexa um documento em texto (201) |
| GET | `/documents` | Lista documentos |
| GET | `/documents/{id}` | Detalha um documento (404 se não existir) |
| DELETE | `/documents/{id}` | Remove documento e trechos (204) |
| POST | `/ask` | Responde com base nos trechos recuperados, com citações |

Sem `GROQ_API_KEY` no `.env`, a API usa o provedor `fake`, que responde com o trecho mais relevante. Com a chave e `LLM_PROVIDER=groq`, a resposta é gerada pelo modelo, que é instruído a citar os trechos como `[n]`.

## Testes e lint

```bash
pytest
ruff check .
```

## Documentação

- [Escopo do MVP](docs/escopo-mvp.md)
- [Backlog por release](docs/backlog.md)
- [Arquitetura](docs/arquitetura.md)
- [Decisões técnicas](docs/decisoes.md)

## Uso de IA no desenvolvimento

Desenvolvido com apoio de agente de código (Claude Code), em ciclos curtos com revisão de diff, testes e commits pequenos. Os prompts usados ficam em [prompts/](prompts/).

## Aviso

Respostas são informativas e baseadas apenas nos documentos indexados; não substituem orientação contábil ou da Receita Federal.
