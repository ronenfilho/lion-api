# Checklist de entrega — LION API 1.0.0

Checklist final de submissão (aula 5.1), conferido em 2026-10-15. Itens desmarcados são os que ainda dependem de ação antes de publicar.

## Submissão

- [x] **Repositório público e acessível:** [github.com/ronenfilho/lion-api](https://github.com/ronenfilho/lion-api).
- [x] **README completo e claro:** problema e solução, arquitetura (Mermaid), stack, como rodar (Makefile e Docker) e testar, endpoints com `curl`, configuração, limites e próximos passos, uso de IA no desenvolvimento e licença.
- [x] **Todos os testes passando:** 83 testes (`make test`) e Ruff sem erros (`make lint`); CI em Python 3.11 e 3.12, mais build e smoke test da imagem Docker.
- [x] **Nenhuma credencial exposta:** histórico (todas as refs, reflog e objetos inalcançáveis) e árvore varridos por padrões de chave (`gsk_`, `AIza`, `sk-`, `AKIA`, chave privada, `api_key=`/`token=`/`secret=` com valor, `Bearer`), sem ocorrências; `.env` ignorado e só o `.env.example`, sem valores, versionado.
- [x] **Histórico de commits consistente:** Conventional Commits em português desde o primeiro commit; refatorações separadas de funcionalidades.
- [ ] **Tag da versão final:** criar `v1.0.0` no commit de entrega, depois que os commits da 1.0 forem revisados e enviados (`v0.1.0` e `v0.2.0` já existem).

## Reprodutibilidade

- [x] Dependências declaradas e fixadas: `requirements.txt` (execução) e `requirements-dev.txt` (testes e lint).
- [x] `.env.example` com todas as variáveis e seus limites; `git check-ignore .env.example` não retorna nada.
- [x] `Makefile` com `install`, `run`, `test`, `lint`, `format`, `load-sample`, `docker-build`, `docker-run`, `clean` e `help`.
- [x] `Dockerfile` (`python:3.12-slim`, usuário sem privilégios, `HEALTHCHECK`, banco em volume) e `.dockerignore`.
- [x] **Máquina limpa:** árvore copiada para um servidor Linux (Ubuntu, Python 3.12.3) sem `.venv`; seguindo só o README, `make install`, `make test` (83 verdes), `make lint`, `make run` e `make load-sample` funcionaram.
- [x] **Imagem validada:** `make docker-build` e `make docker-run` no mesmo servidor; `/health`, carga do corpus via `docker exec`, `/ask` com citação, CPF bloqueado com 422, `HEALTHCHECK` `healthy`, processo como `lion` (uid 10001) e dados preservados no volume após reiniciar.
- [x] Versão única (`app.__version__` = `1.0.0`), exposta no `/openapi.json` e usada na tag da imagem.

## Documentação

- [x] [CHANGELOG](../CHANGELOG.md) com 1.0.0, 0.2.0 e 0.1.0 e links de comparação.
- [x] [LICENSE](../LICENSE) MIT.
- [x] [Roteiro de demo](demo.md) de cerca de 4 minutos, com comandos prontos.
- [x] [Backlog](backlog.md), [decisões](decisoes.md) (D01–D20), [arquitetura](arquitetura.md) e [prompts](../prompts/README.md) (01–24) atualizados.

## Pendências conhecidas (não bloqueiam a entrega)

- [ ] Validar o `GroqProvider` com chave real (hoje coberto por testes com HTTP simulado).
- [ ] Primeira execução do job `docker` no GitHub Actions, depois do push.

## Antes de publicar

```bash
git status                      # working tree limpo
make lint test                  # verde
git log --oneline v0.2.0..HEAD  # commits da 1.0 legíveis
git tag -a v1.0.0 -m "LION API 1.0.0 — entrega final"
git push origin main --follow-tags
```

## Post do fórum (modelo)

> **LION API 1.0.0** — API REST de RAG que responde dúvidas de IRPF com base em fontes oficiais, citando os trechos usados, bloqueando CPF/e-mail/telefone e respondendo "não encontrei base" quando não há fundamento.
>
> - Repositório: https://github.com/ronenfilho/lion-api (tag `v1.0.0`)
> - Rodar: `make install && make run`, depois `make load-sample` (ou `make docker-build && make docker-run`)
> - Testar: `make test` (83 testes, sem rede)
> - Arquitetura, exemplos `curl`, limites e uso de IA no desenvolvimento: README
> - Roteiro de demo: `docs/demo.md`
