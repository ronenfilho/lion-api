# Arquitetura — LION API

```mermaid
flowchart LR
    Cliente([Cliente HTTP])

    subgraph API["api (FastAPI)"]
        R1["/health"]
        R2["/documents"]
        R3["/ask"]
        R4["/answers/{id}/feedback"]
    end

    subgraph Services["services"]
        DS[DocumentService<br/>chunking]
        AS[AskService]
        GIn[Guardrail de entrada<br/>PII, tamanho]
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
    R4 --> DB
```

## Fluxo de `POST /ask`

1. A rota valida o payload (Pydantic).
2. O guardrail de entrada rejeita pergunta inválida ou com dados pessoais.
3. O retriever BM25 busca os `k` trechos mais relevantes no SQLite.
4. O provider de LLM gera a resposta com um prompt que exige citar os trechos.
5. O guardrail de saída confere as citações; sem base, devolve a resposta padrão.
6. A resposta é gravada (para receber feedback) e devolvida com as citações.
