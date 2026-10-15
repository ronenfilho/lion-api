# 🦁 LION API

[![CI](https://github.com/ronenfilho/lion-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ronenfilho/lion-api/actions/workflows/ci.yml)

API REST que responde dúvidas sobre **IRPF 2026** com base em fontes oficiais da Receita Federal, citando os trechos usados e aplicando guardrails contra alucinação e vazamento de dados pessoais.

MVP derivado do projeto de pesquisa [LION](https://github.com/ronenfilho/lion), desenvolvido como mini-projeto do Módulo 4 da especialização AKCIT/UFG *Engenharia de Software: Automação e Inovação com IA Generativa*.

> Status: **release 0.2 (Qualidade) concluída** — guardrails de entrada (dados pessoais) e de saída (citações), feedback das respostas, erros padronizados e CI. Próxima: 1.0 (Docker, provedor real testado, entrega). Ver [backlog](docs/backlog.md).

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
| POST | `/ask` | Responde com base nos trechos recuperados, com citações (422 se houver dado pessoal) |
| POST | `/answers/{answer_id}/feedback` | Registra se a resposta foi útil (201; 404 se a resposta não existir) |

Sem `GROQ_API_KEY` no `.env`, a API usa o provedor `fake`, que responde com o trecho mais relevante. Com a chave e `LLM_PROVIDER=groq`, a resposta é gerada pelo modelo, que é instruído a citar os trechos como `[n]`. No texto devolvido, `[i]` corresponde a `citations[i-1]`.

### Guardrails e feedback

```bash
# Pergunta com dado pessoal: bloqueada antes de chegar ao LLM ou ao banco (o dado não é ecoado)
curl -s -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "Meu CPF é 123.456.789-09, tenho restituição?"}'
# 422 {"detail": "Bloqueado: o campo 'pergunta' parece conter dado pessoal (CPF). ..."}

# Avaliar uma resposta (use o answer_id devolvido pelo /ask)
curl -s -X POST localhost:8000/answers/1/feedback -H 'content-type: application/json' \
  -d '{"useful": true, "comment": "Resposta clara."}'
# 201 {"id": 1, "answer_id": 1, "useful": true, "comment": "Resposta clara.", "created_at": "..."}
```

Erros de regra de negócio seguem o formato `{"detail": "mensagem"}` (404 para documento ou resposta inexistente, 422 para dado pessoal). Detalhes em [arquitetura](docs/arquitetura.md#tratamento-de-erros).

## Testes e lint

```bash
pytest
ruff check .
ruff format --check .
```

O GitHub Actions ([`ci.yml`](.github/workflows/ci.yml)) roda os três comandos em Python 3.11 e 3.12 a cada push e pull request. Os testes não usam rede, nem o `.env`, nem o banco de `var/`.

## Documentação

- [Escopo do MVP](docs/escopo-mvp.md)
- [Backlog por release](docs/backlog.md)
- [Arquitetura](docs/arquitetura.md)
- [Decisões técnicas](docs/decisoes.md)

## Limites

- **Corpus pequeno e só texto:** a busca BM25 recalcula o índice a cada pergunta (D01) e não entende sinônimos; serve para dezenas de documentos, não milhares. Sem PDF/HTML nem busca semântica.
- **Guardrail de dados pessoais por regex** (D08): cobre CPF, e-mail e telefone brasileiros. Não detecta nome, endereço, RG, CNH, dados bancários. Pode bloquear números longos que só parecem CPF ou telefone.
- **Guardrail de saída confere a citação, não o conteúdo:** garante que cada `[n]` aponta para um trecho recuperado, mas não que a frase citada esteja de fato no trecho. Um LLM pode citar o trecho certo e ainda assim parafrasear errado.
- **Provedor real ainda não validado com chave:** o `GroqProvider` é testado com HTTP simulado; a validação com a API real fica para a 1.0.
- **Sem autenticação nem limite de uso:** qualquer cliente pode indexar, apagar documentos e enviar feedback (inclusive mais de um por resposta).
- **SQLite numa conexão compartilhada:** adequado para uso local e demonstração, não para carga concorrente.
- **Não é orientação fiscal:** respostas se limitam aos trechos indexados, que podem estar desatualizados.

## Como a IA foi usada no desenvolvimento

O código foi escrito com um agente de código (**Claude Code**), sob direção e revisão humana:

- **Ciclos curtos:** cada pedido cobre uma parte pequena (um módulo, uma regra, um conjunto de testes), registrado em [prompts/](prompts/) no formato CO-STAR (contexto, objetivo, estilo, resposta esperada).
- **TDD nas regras novas da 0.2:** os testes dos guardrails, do feedback e do provedor Groq foram escritos antes do código e rodados no vermelho; só então o código foi implementado.
- **Revisão humana de todo diff** antes de cada commit, com `ruff` e `pytest` verdes; refatorações em commits separados das funcionalidades.
- **Revisão crítica do que a IA gerou:** o próprio registro em [prompts/](prompts/) lista os problemas encontrados e corrigidos (ex.: teste de ordenação que não testava ordenação, BM25 que não encontrava nada em corpus de um trecho, payload `null` do Groq que viraria erro 500).
- **Segredos fora do prompt e do repositório:** chaves só no `.env` local; os testes usam o provedor `fake` ou HTTP simulado.
- **IA em runtime com fallback:** se o LLM falhar, a API devolve os trechos encontrados em vez de erro (D03).

## Aviso

Respostas são informativas e baseadas apenas nos documentos indexados; não substituem orientação contábil ou da Receita Federal.
