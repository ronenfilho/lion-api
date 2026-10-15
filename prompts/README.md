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
