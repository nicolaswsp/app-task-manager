# Task Manager Micro-API

MVP de uma micro-API para gerenciamento de tarefas com sugestao de prioridade assistida por IA. O projeto expoe endpoints REST para criar, listar, consultar, atualizar e remover tarefas, alem de aplicar uma camada simples de recomendacao de status com heuristicas locais e fallback opcional para LLM.

## Visao Geral

A API permite gerenciar tarefas com os seguintes dados principais:

- `title`: titulo da tarefa.
- `description`: descricao opcional.
- `status`: estado atual da tarefa.
- `created_at`: data de criacao.
- `updated_at`: data da ultima atualizacao.

Status suportados:

- `pending`
- `in_progress`
- `completed`

Quando uma tarefa e criada com status `pending`, o servico pode sugerir automaticamente um status mais adequado com base no titulo e na descricao.

## Stack

- Python 3.12+
- FastAPI
- Pydantic
- SQLite
- Pytest
- HTTPX
- uv para gerenciamento de ambiente e dependencias

## Instalacao

### Pre-requisitos

- Python 3.12 ou superior
- uv instalado

Para instalar o `uv`, consulte a documentacao oficial: https://docs.astral.sh/uv/

### Clonar o projeto

```bash
git clone <repo_url>
cd app-task-manager
```

### Instalar dependencias

```bash
uv sync
```

Caso prefira usar o ambiente virtual local diretamente:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

No Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Execucao

### Executar a aplicacao

```bash
uv run fastapi dev app/main.py
```

Alternativamente, usando `uvicorn`:

```bash
uv run uvicorn app.main:app --reload
```

A API ficara disponivel em:

```text
http://127.0.0.1:8000
```

### Health check

```bash
curl http://127.0.0.1:8000/health
```

Resposta esperada:

```json
{
  "status": "ok",
  "timestamp": "2026-05-02T20:00:00.000000"
}
```

## Endpoints

### Criar tarefa

```http
POST /tasks
```

Payload:

```json
{
  "title": "Corrigir bug critico",
  "description": "Falha no fluxo de criacao de tarefas",
  "status": "pending"
}
```

Resposta:

```json
{
  "id": 1,
  "title": "Corrigir bug critico",
  "description": "Falha no fluxo de criacao de tarefas",
  "status": "in_progress",
  "created_at": "2026-05-02T20:00:00+00:00",
  "updated_at": "2026-05-02T20:00:00+00:00"
}
```

### Listar tarefas

```http
GET /tasks
```

Com filtro por status:

```http
GET /tasks?status_filter=pending
```

### Buscar tarefa por ID

```http
GET /tasks/{task_id}
```

### Atualizar tarefa

```http
PUT /tasks/{task_id}
```

Payload:

```json
{
  "title": "Corrigir bug critico no fluxo principal",
  "status": "completed"
}
```

### Remover tarefa

```http
DELETE /tasks/{task_id}
```

Retorna `204 No Content` quando a remocao e concluida.

## Testes

Executar a suite completa:

```bash
uv run pytest
```

Ou usando o Python do ambiente virtual:

```bash
.\.venv\Scripts\python.exe -m pytest
```

No Linux/macOS:

```bash
.venv/bin/python -m pytest
```

Os testes cobrem:

- Regras de negocio do servico de tarefas.
- Persistencia via repositorio SQLite.
- Rotas HTTP com FastAPI `TestClient`.
- Heuristicas e fallback do advisor de prioridade.

## Arquitetura

```text
app/
  api/
    task_routes.py          # Rotas HTTP de tarefas
  models/
    task.py                 # Modelos Pydantic e enum de status
  repositories/
    task_repository.py      # Persistencia SQLite
  services/
    task_service.py         # Regras de negocio
    priority_advisor.py     # Sugestao de prioridade/status
  main.py                   # Aplicacao FastAPI e health check

tests/
  test_task_routes.py       # Testes de API
  test_task_service.py      # Testes da camada de servico
  test_priority_advisor.py  # Testes da sugestao de prioridade
```

### Camadas

- **API**: recebe requisicoes HTTP, valida payloads e converte erros de negocio em respostas HTTP.
- **Service**: centraliza regras de negocio, incluindo criacao, atualizacao, listagem e remocao de tarefas.
- **Repository**: encapsula acesso ao SQLite.
- **Priority Advisor**: sugere status com heuristicas locais e, quando configurado, pode consultar uma LLM.
- **Models**: define contratos de entrada e saida usando Pydantic.

## Uso da IA

O componente `PriorityAdvisor` sugere o status inicial de uma tarefa quando ela e criada como `pending`.

### Heuristicas locais

Sem configuracao externa, o sistema usa regras simples baseadas em palavras-chave:

- Termos como `done`, `completed` e `finished` sugerem `completed`.
- Termos como `urgent`, `asap`, `critical`, `blocker`, `fix`, `bug`, `immediate`, `high priority` e `important` sugerem `in_progress`.
- Caso nenhuma regra seja acionada, o status permanece `pending`.

### Uso opcional de LLM

Quando a variavel `OPENAI_API_KEY` esta configurada, o advisor tenta consultar uma LLM para classificar a tarefa como:

- `pending`
- `in_progress`
- `completed`

Exemplo:

```bash
set OPENAI_API_KEY=<sua_chave>
```

No Linux/macOS:

```bash
export OPENAI_API_KEY=<sua_chave>
```

Se a chamada externa falhar, o sistema usa automaticamente as heuristicas locais como fallback.

## Limitacoes

- O MVP usa SQLite local, sem suporte a concorrencia avancada ou ambiente distribuido.
- Nao ha autenticacao ou autorizacao.
- Nao ha separacao por usuarios ou organizacoes.
- A sugestao de prioridade ainda e simples e baseada em status, nao em uma escala numerica de prioridade.
- A integracao com LLM depende de variavel de ambiente e disponibilidade externa.
- Nao ha migracoes de banco versionadas.
- Nao ha paginacao, ordenacao customizada ou busca textual.
- Nao ha observabilidade estruturada, como logs, metricas e tracing.

## Proximos Passos

- Incluir o router de tarefas na aplicacao principal, caso ainda nao esteja registrado em `app/main.py`.
- Adicionar autenticacao JWT ou OAuth2.
- Criar modelo de usuarios e associar tarefas a usuarios.
- Evoluir `status` e `priority` para conceitos separados.
- Adicionar campo de prazo e considerar deadline na sugestao de prioridade.
- Implementar migracoes com Alembic.
- Adicionar paginacao, filtros avancados e busca.
- Criar configuracao por ambiente com `.env`.
- Adicionar logs estruturados e tratamento padronizado de erros.
- Preparar Dockerfile e docker-compose para execucao local.
- Adicionar pipeline de CI para lint, testes e validacao de build.

## Licenca

MIT
