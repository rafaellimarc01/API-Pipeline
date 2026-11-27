# API-Pipeline

[![CI/CD](https://github.com/rafaellimarc01/API-Pipeline/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/rafaellimarc01/API-Pipeline/actions/workflows/ci-cd.yml)

API simples em Python (FastAPI) usada como base para um pipeline de **CI/CD com GitHub Actions**:
a cada push o código é verificado e testado, e a cada alteração na `main` uma imagem Docker é
publicada automaticamente no GitHub Container Registry (GHCR).

## Sumário

- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Endpoints](#endpoints)
- [Rodando localmente](#rodando-localmente)
- [Rodando com Docker](#rodando-com-docker)
- [Testes e lint](#testes-e-lint)
- [Pipeline de CI/CD](#pipeline-de-cicd)
- [Fluxo de contribuição](#fluxo-de-contribuição)

## Tecnologias

| Ferramenta | Uso |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | framework da API |
| [Uvicorn](https://www.uvicorn.org/) | servidor ASGI |
| [pytest](https://docs.pytest.org/) | testes automatizados |
| [Ruff](https://docs.astral.sh/ruff/) | lint e organização de imports |
| Docker | empacotamento da aplicação |
| GitHub Actions | pipeline de CI/CD |
| GHCR | registro da imagem Docker |

## Estrutura do projeto

```
API-Pipeline/
├── .github/workflows/ci-cd.yml   # pipeline de CI/CD
├── app/
│   └── main.py                   # API FastAPI
├── tests/
│   └── test_main.py              # testes da API
├── Dockerfile                    # imagem de produção
├── pyproject.toml                # configuração do ruff e pytest
├── requirements.txt              # dependências da aplicação
└── requirements-dev.txt          # dependências de desenvolvimento (testes/lint)
```

## Endpoints

| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| `GET` | `/health` | verificação de saúde da API | `200` |
| `GET` | `/items` | lista todos os itens | `200` |
| `POST` | `/items` | cria um item (`name`, `price`) | `201`, `422` dados inválidos |
| `GET` | `/items/{id}` | busca um item pelo id | `200`, `404` não encontrado |

> Os itens ficam **em memória**: são perdidos quando a API reinicia.

Documentação interativa (gerada pelo FastAPI) com a API rodando:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

Exemplo:

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Caneta", "price": 2.5}'
# {"name":"Caneta","price":2.5,"id":1}
```

## Rodando localmente

Requer Python 3.12+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

A API sobe em <http://localhost:8000>.

## Rodando com Docker

Usando a imagem publicada pelo pipeline:

```bash
docker run -p 8000:8000 ghcr.io/rafaellimarc01/api-pipeline:latest
```

Ou construindo localmente:

```bash
docker build -t api-pipeline .
docker run -p 8000:8000 api-pipeline
```

## Testes e lint

```bash
ruff check .   # lint
pytest -v      # testes
```

Sem Python instalado, dá para rodar tudo dentro de um container:

```bash
docker run --rm -v "$PWD:/src" -w /src python:3.12-slim \
  sh -c "pip install -q -r requirements-dev.txt && ruff check . && pytest -v"
```

## Pipeline de CI/CD

Definido em [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).

```
push / pull request
        │
        ▼
┌─────────────────────┐     ┌──────────────────────────────────────────────┐
│ CI: Lint e testes   │ ──▶ │ CD: Build e publicação da imagem             │
│  • ruff check       │     │  • docker build                              │
│  • pytest           │     │  • smoke test (sobe o container e chama      │
└─────────────────────┘     │    /health)                                  │
                            │  • push para o GHCR  ← somente na main       │
                            └──────────────────────────────────────────────┘
```

| Evento | Lint e testes | Build + smoke test | Publica no GHCR |
|---|---|---|---|
| push em qualquer branch | ✅ | ✅ | — |
| pull request para `main` | ✅ | ✅ | — |
| push na `main` (merge) | ✅ | ✅ | ✅ |

Se o job de CI falhar, o de CD não roda. A imagem é publicada com duas tags:
`latest` e o SHA do commit (ex.: `ghcr.io/rafaellimarc01/api-pipeline:5c4e63c…`).

A publicação usa o `GITHUB_TOKEN` do próprio Actions (sem segredos extras). O pacote no GHCR
precisa estar ligado a este repositório com permissão de escrita — o `Dockerfile` declara isso
com o label `org.opencontainers.image.source`.

## Fluxo de contribuição

1. Crie uma branch a partir da `main` (`feat/...`, `fix/...`, `docs/...`).
2. Faça um commit por alteração.
3. Envie a branch e abra um pull request para a `main` — o pipeline roda no PR.
4. Com o pipeline verde, faça o merge: a nova imagem é publicada automaticamente.
