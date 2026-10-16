# LION API — atalhos de desenvolvimento (macOS e Linux). `make` sem alvo mostra a ajuda.
.DEFAULT_GOAL := help
.PHONY: help install run test lint format load-sample docker-build docker-run clean

PYTHON  ?= python3
VENV    ?= .venv
BIN     := $(VENV)/bin
HOST    ?= 127.0.0.1
PORT    ?= 8000
BASE_URL ?= http://localhost:$(PORT)
IMAGE   ?= lion-api
VERSION := $(shell sed -n 's/^__version__ = "\(.*\)"/\1/p' app/__init__.py)
# Passa o .env ao container só se ele existir
ENV_FILE := $(if $(wildcard .env),--env-file .env,)

help: ## Lista os alvos disponíveis
	@echo "LION API $(VERSION) — uso: make <alvo>"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-13s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

$(BIN)/python:
	$(PYTHON) -m venv $(VENV)

install: $(BIN)/python ## Cria o .venv e instala dependências de execução e de desenvolvimento
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -r requirements-dev.txt

run: ## Sobe a API com reload (padrão http://127.0.0.1:8000; docs em /docs)
	$(BIN)/uvicorn app.main:app --reload --host $(HOST) --port $(PORT)

test: ## Roda a suíte de testes (sem rede, sem .env, sem o banco de var/)
	$(BIN)/pytest -q

lint: ## Confere lint e formatação com Ruff (o mesmo que o CI)
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

format: ## Formata o código e aplica correções automáticas do Ruff
	$(BIN)/ruff format .
	$(BIN)/ruff check --fix .

load-sample: ## Carrega o corpus de exemplo na API em execução (BASE_URL=...)
	$(BIN)/python scripts/load_sample.py $(BASE_URL)

docker-build: ## Constrói a imagem lion-api:<versão> (e :latest)
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

docker-run: ## Sobe o container na porta 8000 (PORT=...), banco no volume lion-data
	docker run --rm --name $(IMAGE) -p $(PORT):8000 $(ENV_FILE) -v lion-data:/data $(IMAGE):$(VERSION)

clean: ## Remove caches e bytecode (mantém .venv e o banco de var/)
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find . -path ./$(VENV) -prune -o -type d -name __pycache__ -exec rm -rf {} +
