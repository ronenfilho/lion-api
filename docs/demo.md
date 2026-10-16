# Roteiro de demonstração — LION API 1.0 (≈ 4 min)

Roteiro de 3 a 5 minutos para avaliadores técnicos: problema → arquitetura → API rodando → guardrail → feedback → testes. Serve para apresentação ao vivo, vídeo ou post no fórum.

## Preparação (antes de começar)

```bash
git clone https://github.com/ronenfilho/lion-api.git && cd lion-api
make install
```

- Dois terminais abertos na pasta do projeto e o navegador no README do GitHub (o diagrama Mermaid renderiza lá).
- Sem `.env`, a API usa o provedor `fake`: respostas determinísticas, sem rede e sem chave. É o modo recomendado para a demo.
- Banco limpo, para os ids baterem com o roteiro: o terminal 1 usa um arquivo temporário.

## 0:00–0:40 — Problema e escopo

- LLM genérico responde sobre IRPF sem dizer a fonte e pode inventar valores e prazos; usuários colam CPF na pergunta.
- A LION API responde **só com base em trechos de fontes oficiais**, cita cada trecho, bloqueia dados pessoais e devolve "não encontrei base" quando não há fundamento.
- Fora de escopo: interface de chat, PDF, busca semântica, autenticação ([escopo](escopo-mvp.md)).

## 0:40–1:20 — Arquitetura

Mostrar o diagrama do README (seção *Arquitetura*):

- Camadas `api` → `services` → `repositories`; LLM atrás de uma interface (`fake` ou `groq`).
- Fluxo do `/ask`: guardrail de entrada → BM25 → LLM → guardrail de saída (citações) → grava a resposta.
- Se o LLM falhar, a API devolve os trechos em vez de erro 500.

## 1:20–2:40 — API rodando: carga do corpus e pergunta com citações

Terminal 1:

```bash
DATABASE_PATH=/tmp/lion-demo.sqlite3 make run
```

Terminal 2:

```bash
curl -s localhost:8000/health
make load-sample
curl -s -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "Qual o limite de dedução com educação?"}' | python3 -m json.tool
```

Destacar na resposta:

- `grounded: true` e o marcador `[1]` no texto, que aponta para `citations[0]`;
- a citação traz documento, trecho (`chunk_id`), excerto e pontuação BM25;
- `provider: "fake"`; com `LLM_PROVIDER=groq` e chave no `.env`, o texto vem do modelo com as mesmas regras.

Opcional (10 s): pergunta fora do corpus devolve a resposta padrão, sem citações.

```bash
curl -s -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "Como declarar criptomoedas?"}' | python3 -m json.tool
```

## 2:40–3:10 — Guardrail bloqueando CPF

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "Meu CPF é 123.456.789-09, tenho restituição?"}'
```

- 422 com o motivo (CPF) e **sem repetir o número**.
- O bloqueio acontece antes da busca, do LLM e do banco: nada é gravado.

## 3:10–3:30 — Feedback

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:8000/answers/1/feedback \
  -H 'content-type: application/json' -d '{"useful": true, "comment": "Resposta clara."}'
curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:8000/answers/999/feedback \
  -H 'content-type: application/json' -d '{"useful": false}'
```

- 201 com o registro; 404 com `{"detail": "Resposta 999 não encontrada."}` para resposta inexistente.

## 3:30–4:10 — Testes verdes

Parar o servidor (Ctrl+C no terminal 1) e rodar:

```bash
make test
make lint
```

- 83 testes em menos de 1 s, sem rede e sem `.env`; Ruff sem erros.
- Mostrar o badge do CI no README: os mesmos comandos rodam em Python 3.11 e 3.12, e um job constrói a imagem Docker e faz smoke test nela.

## Encerramento (opcional, 20 s)

- Docker: `make docker-build && make docker-run` sobe a mesma API em container, com banco em volume.
- Uso de IA no desenvolvimento e bugs encontrados na revisão humana: seção *Como a IA foi usada no desenvolvimento* do README e [prompts/](../prompts/README.md).

## Se algo der errado

| Sintoma | Ação |
|---|---|
| `Address already in use` | `make run PORT=8001` e `make load-sample BASE_URL=http://localhost:8001` |
| `/ask` cita ids diferentes do roteiro | o banco não estava limpo: `rm -f /tmp/lion-demo.sqlite3` e reiniciar |
| `make: .venv/bin/uvicorn: No such file or directory` | rodar `make install` |
