# Registro de decisões técnicas

## D01 — Busca por BM25, sem embeddings (release 0.1)
- **Contexto:** o LION original usa busca híbrida (densa + BM25) com sentence-transformers, torch e ChromaDB, uma pilha pesada para um MVP de ~30h.
- **Decisão:** usar só BM25 (`rank-bm25`), com tokenização sem acentos e sem stopwords. O índice é recalculado a cada busca.
- **Consequências:** instalação leve, testes rápidos e determinísticos. Recalcular o índice só é viável com corpus pequeno. Busca semântica fica como candidata à 1.0.

## D02 — SQLite como persistência
- **Contexto:** a aula 3.1 recomenda persistência simples. Em memória perderia os documentos ao reiniciar.
- **Decisão:** SQLite com tabelas `documents`, `chunks` (com `ON DELETE CASCADE`) e `answers`, via `sqlite3` da biblioteca padrão.
- **Consequências:** sem ORM nem dependência extra. Para produção real, migrar para Postgres.

## D03 — Camada `llm` com provedor `fake` e fallback
- **Contexto:** a IA em runtime não pode derrubar o fluxo principal (aula 3.1), e os testes não podem depender de rede nem de chave.
- **Decisão:** interface `LLMProvider` com `FakeProvider` (determinístico) e `GroqProvider`.
  - Sem chave configurada, a fábrica cai para o `fake`.
  - Se o provedor falhar (`LLMError`), o `/ask` devolve os trechos recuperados com um aviso, em vez de erro 500.
- **Consequências:** trocar ou adicionar provedor (ex.: Gemini) é só uma nova classe.

## D04 — Groq via `httpx`, sem SDK
- **Decisão:** chamar o endpoint OpenAI-compatível da Groq com `httpx`, que já é dependência dos testes.
- **Consequências:** uma dependência a menos e erro de rede tratado num só lugar. Perde-se a tipagem do SDK.

## D05 — `create_app` com dependências injetáveis
- **Decisão:** a aplicação é montada por `create_app(settings, provider)`. Os serviços ficam em `app.state` e as rotas os obtêm via `Depends`.
- **Consequências:** cada teste usa um banco temporário e o provedor que quiser (inclusive um que falha), sem *monkeypatch*.

## D06 — Citações validadas pelo número do trecho
- **Decisão:** o prompt numera os trechos ([1], [2]…) e exige citação. O serviço mantém só as citações que apontam para trechos realmente recuperados. Sem nenhuma citação válida, `grounded=false`.
- **Consequências:** é a base do guardrail de saída (RF06), completado na 0.2 (ver D09).

## D07 — Exceções de domínio e handler central (release 0.2)
- **Contexto:** as rotas repetiam `try/except` para converter `DocumentNotFoundError` em 404, e novos erros (resposta inexistente, dado pessoal) repetiriam o padrão (aula 4.1).
- **Decisão:** `app/exceptions.py` define `LionError` → `NotFoundError` (`DocumentNotFoundError`, `AnswerNotFoundError`) e `SensitiveDataError`, cada uma com a mensagem pronta para o cliente. `app/api/errors.py` mapeia família → status (404, 422) num só lugar; as rotas não tratam erro.
- **Consequências:** serviços não conhecem HTTP; corpo de erro uniforme (`{"detail": "..."}`); um erro novo é uma classe + uma linha no mapa. Erro de domínio sem mapeamento cai no 500 padrão, de propósito.

## D08 — Guardrail de entrada por expressões regulares, conservador
- **Decisão:** `app/services/guardrails.py` detecta CPF (com ou sem pontuação), e-mail e telefone brasileiro (com DDD/DDI, fixo ou celular; sem DDD, só celular de 9 dígitos). Aplicado no `AskService` **antes** de buscar, gerar ou gravar, e também ao comentário do feedback.
  - A mensagem informa o tipo de dado e o campo, nunca o valor.
  - CPF não tem o dígito verificador conferido: na dúvida, bloqueia.
  - Telefone sem DDD exige o 9 inicial, para não bloquear intervalos como "2025-2026".
- **Consequências:** nada com dado pessoal chega ao LLM, ao banco ou aos logs. Há falsos positivos possíveis (ex.: um número de 10–11 dígitos qualquer); preferível a vazar dado. Não cobre nome, endereço nem outros documentos (RG, CNH).

## D09 — Guardrail de saída: citações renumeradas e resposta sem base
- **Contexto:** na 0.1, a citação inválida era descartada da lista mas ficava no texto, a lista seguia a ordem de citação mas o texto mantinha a numeração do prompt (o `[2]` do texto podia ser o 1º item de `citations`), e uma resposta sem nenhuma citação válida era devolvida como veio, só com `grounded=false`.
- **Decisão:** `check_citations` remove do texto as citações que não apontam para trecho recuperado e renumera as válidas na ordem da primeira ocorrência, de modo que `[i]` no texto é `citations[i-1]`. Sem nenhuma citação válida, a resposta do LLM é substituída pela resposta padrão "não encontrei base" (`grounded=false`, `citations=[]`).
- **Consequências:** o cliente mapeia citação → trecho sem ambiguidade; texto não fundamentado não chega ao usuário. O texto do LLM é alterado (só nos marcadores).

## D10 — BM25 com IDF sempre positivo
- **Contexto:** na revisão dos testes, o IDF do `BM25Okapi` (`log((N - n + 0.5) / (n + 0.5))`) se mostrou negativo ou nulo para termos presentes em metade ou mais dos trechos. Com 1 ou 2 trechos indexados, **nenhuma** busca retornava resultado.
- **Decisão:** subclasse `_PositiveIdfBM25` com o IDF do Lucene, `log(1 + (N - n + 0.5) / (n + 0.5))`.
- **Consequências:** corpus pequeno passa a funcionar; a ordenação em corpus maior muda pouco. Depende de um método interno (`_calc_idf`) da `rank-bm25`, fixada em `0.2.2` no `requirements.txt`.

## D11 — Feedback em tabela própria
- **Decisão:** tabela `feedback` (`answer_id` com chave estrangeira para `answers`, `useful`, `comment` opcional até 500, `created_at`), com `FeedbackRepository` e `FeedbackService`. O serviço confere se a resposta existe (`AnswerNotFoundError` → 404) antes de gravar. Mais de um feedback por resposta é aceito.
- **Consequências:** o `CREATE TABLE IF NOT EXISTS` cria a tabela em bancos da 0.1 sem migração. Sem autenticação, não dá para limitar um feedback por usuário.

## D12 — `GroqProvider` com cliente HTTP injetável
- **Contexto:** testar o provedor sem rede exigia *monkeypatch* de `httpx.post`. Os testes revelaram que `content: null` no payload escapava como `AttributeError` (viraria 500 no `/ask`, pois o serviço só trata `LLMError`).
- **Decisão:** o construtor aceita `client: httpx.Client` (nos testes, com `httpx.MockTransport`). Resposta sem texto ou com estrutura inesperada vira `LLMError`.
- **Consequências:** testes de sucesso, timeout, HTTP 500 e payload inesperado sem rede; o fallback de D03 cobre todos esses casos.

## D13 — Testes isolados do ambiente local e CI
- **Decisão:** `tests/conftest.py` força `DATABASE_PATH=:memory:` e `LLM_PROVIDER=fake` antes de qualquer teste importar `app.main` (que monta a aplicação no import, para o uvicorn). GitHub Actions roda `ruff check`, `ruff format --check` e `pytest` em Python 3.11 e 3.12 a cada push e PR.
- **Consequências:** a suíte não lê o `.env` nem escreve em `var/` do desenvolvedor, e roda igual na máquina e no CI.
