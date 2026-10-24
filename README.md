# Task Manager Micro-API

MVP de uma micro-API para gerenciamento de tarefas com sugestao assistida por IA. A API permite criar, listar, consultar, atualizar e remover tarefas, com uma camada de recomendacao que sugere o `status` inicial da tarefa a partir do titulo e da descricao.

> Observacao: neste MVP, a IA sugere `status` (`pending`, `in_progress`, `completed`). Uma prioridade separada, como `low`, `medium` ou `high`, ainda nao foi implementada.

## Visao Geral

A API gerencia tarefas com os seguintes campos:

- `id`: identificador da tarefa.
- `title`: titulo da tarefa.
- `description`: descricao opcional.
- `status`: estado atual da tarefa.
- `created_at`: data de criacao.
- `updated_at`: data da ultima atualizacao.

Status suportados:

- `pending`
- `in_progress`
- `completed`

Quando uma tarefa e criada com status `pending`, o servico pode sugerir automaticamente um status mais adequado com base no conteudo informado.

## Stack

- Python 3.12+
- FastAPI
- Pydantic
- SQLite
- Pytest
- HTTPX
- Uvicorn
- uv para gerenciamento de ambiente e dependencias

## Instalacao

### Pre-requisitos

- Python 3.12 ou superior
- uv instalado
- Git

Para instalar o `uv`, consulte: https://docs.astral.sh/uv/

### Clonar o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd app-task-manager
```

Substitua `<URL_DO_REPOSITORIO>` pela URL real do repositorio.

### Instalar dependencias

Com `make`:

```bash
make install
```

Ou diretamente com `uv`:

```bash
uv sync
```

## Configuracao

Crie um arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Variaveis disponiveis:

```env
OPENAI_API_KEY=your_openai_api_key_here
HOST=127.0.0.1
PORT=8000
```

`OPENAI_API_KEY` e opcional. Sem essa chave, a API continua funcionando com heuristicas locais.

## Execucao

Com `make`:

```bash
make run
```

Ou diretamente com `uv`:

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

A API ficara disponivel em:

```text
http://127.0.0.1:8000
```

Documentacao interativa:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
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

## Uso Da API

### Criar tarefa

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Corrigir bug critico no login",
    "description": "Erro blocker impedindo usuarios de acessar o sistema",
    "status": "pending"
  }'
```

Resposta esperada:

```json
{
  "id": 1,
  "title": "Corrigir bug critico no login",
  "description": "Erro blocker impedindo usuarios de acessar o sistema",
  "status": "in_progress",
  "created_at": "2026-05-02T20:00:00+00:00",
  "updated_at": "2026-05-02T20:00:00+00:00"
}
```

No PowerShell:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/tasks" `
  -ContentType "application/json" `
  -Body '{"title":"Comprar material de escritorio","description":"Reposicao mensal","status":"pending"}'
```

### Listar tarefas

```bash
curl http://127.0.0.1:8000/tasks
```

### Filtrar tarefas por status

```bash
curl "http://127.0.0.1:8000/tasks?status_filter=in_progress"
```

### Buscar tarefa por ID

```bash
curl http://127.0.0.1:8000/tasks/1
```

### Atualizar tarefa

```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Corrigir bug critico no fluxo principal",
    "status": "completed"
  }'
```

### Remover tarefa

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

Retorna `204 No Content` quando a remocao e concluida.

## Testes

Com `make`:

```bash
make test
```

Ou diretamente com `uv`:

```bash
uv run pytest
```

Saida esperada:

```text
32 passed
```

Os testes cobrem:

- Regras de negocio do servico de tarefas.
- Persistencia via repositorio SQLite.
- Rotas HTTP com FastAPI `TestClient`.
- Heuristicas e fallback do advisor de status.
- Fluxos integrados entre API, servico e banco SQLite.

Os prompts usados e os casos de integracao gerados estao registrados em [docs/testes-integracao-com-genai.md](./docs/testes-integracao-com-genai.md).

## Persistencia

O MVP usa SQLite local. Por padrao, o arquivo `tasks.db` e criado automaticamente na raiz do projeto na primeira operacao que acessa o repositorio.

Para resetar os dados locais:

1. Pare a API.
2. Remova o arquivo `tasks.db`.
3. Inicie a API novamente.

No PowerShell:

```powershell
Remove-Item .\tasks.db
```

No Linux/macOS:

```bash
rm tasks.db
```

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
    priority_advisor.py     # Sugestao de status
  main.py                   # Aplicacao FastAPI

tests/
  test_task_integration.py  # Fluxos integrados entre API, servico e SQLite
  test_task_routes.py       # Testes de API
  test_task_service.py      # Testes da camada de servico
  test_priority_advisor.py  # Testes da sugestao de status
```

Fluxo principal:

```text
Cliente HTTP
  -> FastAPI route
  -> TaskService
  -> PriorityAdvisor
  -> TaskRepository
  -> SQLite
```

### Camadas

- **API**: recebe requisicoes HTTP, valida payloads e converte erros em respostas HTTP.
- **Service**: centraliza regras de negocio de criacao, atualizacao, listagem e remocao.
- **Priority Advisor**: sugere o status inicial da tarefa.
- **Repository**: encapsula acesso ao SQLite.
- **Models**: define contratos de entrada e saida com Pydantic.

### Desenvolvimento local

- Para alterar endpoints, edite `app/api/task_routes.py`.
- Para alterar regras de negocio, edite `app/services/task_service.py`.
- Para alterar a sugestao de IA/heuristicas, edite `app/services/priority_advisor.py`.
- Para alterar persistencia, edite `app/repositories/task_repository.py`.
- Para alterar contratos da API, edite `app/models/task.py`.
- Para adicionar cobertura, crie ou atualize testes em `tests/`.

## Uso Da IA

O componente `PriorityAdvisor` sugere o `status` inicial de uma tarefa quando ela e criada como `pending`.

### Comportamento

1. Se `OPENAI_API_KEY` nao estiver configurada, o sistema usa heuristicas locais.
2. Se `OPENAI_API_KEY` estiver configurada, o sistema tenta consultar uma LLM.
3. Se a chamada para a LLM falhar, o sistema usa heuristicas locais como fallback.

O modelo configurado atualmente no codigo e `gpt-3.5-turbo`.

### Heuristicas locais

Sem configuracao externa, o sistema aplica regras por palavras-chave:

- `done`, `completed`, `finished`: sugere `completed`.
- `urgent`, `asap`, `critical`, `blocker`, `fix`, `bug`, `immediate`, `high priority`, `important`: sugere `in_progress`.
- Caso nenhuma regra seja acionada, mantem `pending`.

### Exemplos

Entrada:

```json
{
  "title": "Corrigir bug critico no login",
  "description": "Erro blocker impedindo usuarios",
  "status": "pending"
}
```

Status sugerido:

```json
{
  "status": "in_progress"
}
```

Entrada:

```json
{
  "title": "Documentacao completed",
  "description": "Guia inicial finished",
  "status": "pending"
}
```

Status sugerido:

```json
{
  "status": "completed"
}
```

Entrada:

```json
{
  "title": "Comprar material de escritorio",
  "description": "Reposicao mensal",
  "status": "pending"
}
```

Status sugerido:

```json
{
  "status": "pending"
}
```

### Configurar LLM

Adicione a chave no arquivo `.env` ou exporte a variavel no terminal:

```bash
export OPENAI_API_KEY=<sua_chave>
```

No Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="<sua_chave>"
```

Nunca versione chaves reais no repositorio.

### Limitacoes da IA neste MVP

- A classificacao e simples e limitada a tres status.
- O advisor nao usa historico de tarefas.
- O advisor nao considera deadline, impacto, esforco ou usuario responsavel.
- Nao ha score de confianca.
- A chamada para LLM depende de rede e disponibilidade externa.
- A resposta da LLM nao retorna justificativa estruturada.

## Troubleshooting

### Porta 8000 ocupada

Execute a API em outra porta:

```bash
PORT=8001 make run
```

Ou:

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### uv nao encontrado

Instale o `uv` seguindo a documentacao oficial:

```text
https://docs.astral.sh/uv/
```

### Dependencias ausentes

Execute novamente:

```bash
uv sync
```

### Banco local com dados antigos

Remova `tasks.db` com a API parada e inicie novamente.

## Limitacoes

- O MVP usa SQLite local, sem suporte a concorrencia avancada ou ambiente distribuido.
- Nao ha autenticacao ou autorizacao.
- Nao ha separacao por usuarios ou organizacoes.
- `status` e sugestao de prioridade ainda estao acoplados.
- A integracao com LLM depende de variavel de ambiente, rede e disponibilidade externa.
- Nao ha migracoes de banco versionadas.
- Nao ha paginacao, ordenacao customizada ou busca textual.
- Nao ha observabilidade estruturada, como logs, metricas e tracing.

## Proximos Passos

- Separar `status` de `priority`.
- Adicionar campos como `deadline`, `impact`, `effort` e `assignee`.
- Retornar `reason` junto da sugestao de IA.
- Adicionar score de confianca para sugestoes.
- Adicionar autenticacao JWT ou OAuth2.
- Criar modelo de usuarios e associar tarefas a usuarios.
- Implementar migracoes com Alembic.
- Adicionar paginacao, filtros avancados e busca.
- Carregar configuracoes automaticamente a partir de `.env`.
- Adicionar logs estruturados e tratamento padronizado de erros.
- Preparar Dockerfile e docker-compose para execucao local.
- Adicionar pipeline de CI para lint, testes e validacao de build.

## Licenca

MIT
