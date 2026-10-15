# Escopo do MVP — LION API

## Objetivo

Expor como **API REST** o núcleo do assistente LION: responder dúvidas sobre IRPF 2026 com base em um conjunto pequeno de documentos oficiais da Receita Federal (RFB), **citando os trechos usados** e aplicando guardrails para reduzir alucinação e bloquear dados pessoais.

Projeto derivado do repositório de pesquisa [`ronenfilho/lion`](https://github.com/ronenfilho/lion). Aqui entra só o que é necessário para um serviço enxuto e testável; os experimentos de pesquisa ficam lá.

## Público

Desenvolvedores e avaliadores da disciplina (AKCIT, Módulo 4) e, em segundo plano, contribuintes com dúvidas pontuais de IRPF. A API não substitui orientação profissional.

## Requisitos funcionais

| ID | Requisito |
|---|---|
| RF01 | `GET /health` informa que a API está no ar. |
| RF02 | `POST /documents` recebe um documento em texto (título, fonte, conteúdo), divide em trechos (chunks) e indexa. |
| RF03 | `GET /documents` lista documentos indexados; `GET /documents/{id}` detalha; `DELETE /documents/{id}` remove o documento e seus trechos. |
| RF04 | `POST /ask` recebe uma pergunta e devolve resposta gerada por LLM **apenas com base nos trechos recuperados**, com a lista de citações (documento + trecho). |
| RF05 | Guardrail de entrada: rejeitar perguntas vazias, longas demais ou com dados pessoais (CPF, e-mail, telefone). |
| RF06 | Guardrail de saída: se a resposta não citar nenhum trecho recuperado, ou nada relevante for encontrado, responder que não há base suficiente. |
| RF07 | `POST /answers/{id}/feedback` registra avaliação (útil / não útil + comentário opcional) de uma resposta. |

## Requisitos não funcionais

- Python 3.11+, FastAPI, Pydantic v2, SQLite como persistência local.
- Arquitetura em camadas: `api` (rotas) → `services` (regras) → `repositories` (persistência), com `schemas` (entrada/saída) e um componente `llm` com provedores intercambiáveis (`fake`, `groq`, `gemini`).
- Recuperação por **BM25** (sem GPU, sem dependências pesadas como torch).
- Testes com pytest + HTTPX; o provedor `fake` torna os testes determinísticos e sem rede.
- Lint com Ruff; Conventional Commits; segredos só em `.env` (nunca no repo nem no prompt).
- Corpus de exemplo pequeno e público (trechos de normas/perguntas oficiais da RFB), versionado em `data/sample/`.

## Fora de escopo

- Interface web/chat (o LION já tem front Gradio separado).
- Upload de PDF/HTML e conversão de documentos (só texto no MVP).
- Busca densa/embeddings, reranker e busca híbrida.
- Avaliação com RAGAS/BERTScore e os experimentos de pesquisa do LION.
- Autenticação, multiusuário, histórico de conversa.
- Deploy em nuvem gerenciada além de um container Docker.
