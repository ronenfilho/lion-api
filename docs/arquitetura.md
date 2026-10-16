# Arquitetura — LION API

```mermaid
flowchart LR
    Cliente([Cliente HTTP])

    subgraph API["api (FastAPI)"]
        R1["/health"]
        R2["/documents"]
        R3["/ask"]
        R4["/answers/{id}/feedback"]
        ERR[[errors.py<br/>exceção → HTTP]]
    end

    subgraph Services["services"]
        DS[DocumentService<br/>chunking]
        AS[AskService]
        FS[FeedbackService]
        GIn[Guardrail de entrada<br/>CPF, e-mail, telefone]
        GOut[Guardrail de saída<br/>citações]
        RET[Retriever BM25]
    end

    subgraph LLM["llm"]
        P{{Provider}}
        F[fake]
        G[groq]
    end

    subgraph Repo["repositories"]
        DB[(SQLite<br/>documentos, chunks,<br/>respostas, feedback)]
    end

    Cliente --> API
    R2 --> DS --> DB
    R3 --> AS
    AS --> GIn
    AS --> RET --> DB
    AS --> P
    P --> F & G
    AS --> GOut
    AS --> DB
    R4 --> FS
    FS --> GIn
    FS --> DB
```

## Fluxo de `POST /ask`

1. A rota valida o payload (Pydantic): pergunta de 3 a 500 caracteres, sem contar espaços nas pontas.
2. O guardrail de entrada rejeita pergunta com CPF, e-mail ou telefone (`SensitiveDataError` → 422), antes de buscar, gerar ou gravar.
3. O retriever BM25 busca os `k` trechos mais relevantes no SQLite.
4. O provider de LLM gera a resposta com um prompt que exige citar os trechos. Se falhar (`LLMError`), devolve os trechos com um aviso.
5. O guardrail de saída descarta citações inexistentes e renumera as válidas; sem nenhuma, devolve a resposta padrão "não encontrei base".
6. A resposta é gravada (para receber feedback) e devolvida com as citações.

## Tratamento de erros

Os serviços levantam exceções de domínio (`app/exceptions.py`) sem conhecer HTTP. A camada de API converte cada família num só lugar (`app/api/errors.py`):

| Exceção | Status | Exemplo de `detail` |
|---|---|---|
| `DocumentNotFoundError` | 404 | `Documento 7 não encontrado.` |
| `AnswerNotFoundError` | 404 | `Resposta 7 não encontrada.` |
| `SensitiveDataError` | 422 | `Bloqueado: o campo 'pergunta' parece conter dado pessoal (CPF). …` |

Erros de validação do payload continuam no formato padrão do FastAPI (422 com a lista de campos).

## Montagem e execução

- `app.main.create_app(settings, provider)` monta conexão SQLite, repositórios, serviços (em `app.state`), handlers de erro e routers. `app.main.app = create_app()` é o objeto servido pelo uvicorn; um teste confere as rotas registradas nele (D19).
- `load_settings()` lê o ambiente e o `.env` e valida os valores (`ConfigError` impede a API de subir com configuração inválida — D15). A versão vem de `app.__version__` (D14).
- Execução local: `make run` (uvicorn com reload). Container: `Dockerfile` com `python:3.12-slim`, usuário sem privilégios, banco em `/data` (volume) e `HEALTHCHECK` no `/health` (D18).

```mermaid
flowchart LR
    Dev([make run / docker run]) --> U[uvicorn app.main:app]
    U --> CA["create_app()"]
    CA --> S[load_settings<br/>ambiente + .env]
    CA --> C[(SQLite<br/>DATABASE_PATH)]
    CA --> PR[create_provider<br/>fake ou groq]
    CA --> RT[routers + handlers de erro]
```
