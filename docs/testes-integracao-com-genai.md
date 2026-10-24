# Testes de integração apoiados por GenAI

## Cenário escolhido

O cenário cobre o fluxo de criação e manutenção de tarefas pela API REST. Uma requisição HTTP passa pelas rotas FastAPI, pelo `TaskService` e pelo `TaskRepository`, que persiste os dados em SQLite. Na criação com status `pending`, o serviço também consulta o `PriorityAdvisor`, que sugere um status usando regras locais quando a chave da API externa não está configurada.

O teste usa um banco SQLite temporário e o advisor local. Assim, ele exercita a integração entre os componentes sem depender de rede, credenciais ou de um serviço externo.

## Tipos de prompt usados

### 1. Prompt para gerar cenários de fluxo integrado

**Prompt enviado à LLM:**

> Atue como especialista em testes de integração. Considere uma API FastAPI de tarefas com os endpoints POST /tasks, GET /tasks, GET /tasks/{id}, PUT /tasks/{id} e DELETE /tasks/{id}. A rota chama um serviço, que usa um repositório SQLite. Ao criar uma tarefa com status "pending", o serviço pode sugerir um status pelo título e descrição; a regra local classifica termos como "urgent", "critical" e "bug" como "in_progress". Gere casos de teste ponta a ponta que atravessem API, serviço e banco. Para cada caso, informe pré-condições, requisições, status HTTP e resultado verificável. Considere execução isolada, sem chamadas externas.

**Casos gerados e revisados:**

| ID | Caso de integração | Resultado esperado | Cobertura automatizada |
|---|---|---|---|
| CI-01 | Criar tarefa `pending` com texto urgente e consultar a tarefa criada e a listagem filtrada. | HTTP 201; advisor altera o status para `in_progress`; GET por ID e filtro retornam a tarefa persistida. | `test_create_task_suggests_status_and_persists_for_filtered_list` |
| CI-02 | Atualizar título e status de uma tarefa existente e consultar novamente. | HTTP 200; os campos atualizados são persistidos e retornados pelo GET. | `test_update_and_delete_task_are_reflected_across_api_and_database` |
| CI-03 | Excluir tarefa existente e consultar sua existência e a listagem. | HTTP 204; GET por ID retorna 404 e a listagem fica vazia. | `test_update_and_delete_task_are_reflected_across_api_and_database` |

### 2. Prompt para gerar casos negativos e validar o contrato da API

**Prompt enviado à LLM:**

> Com base no contrato da API FastAPI de tarefas, proponha casos negativos de integração que enviem dados inválidos pela API e verifiquem tanto a resposta HTTP quanto a ausência de gravação no SQLite. O título é obrigatório e deve ter de 1 a 100 caracteres; o status aceita somente "pending", "in_progress" ou "completed". Use o formato: entrada, resposta esperada e verificação no sistema persistente.

**Casos gerados e revisados:**

| ID | Entrada | Resultado esperado | Cobertura automatizada |
|---|---|---|---|
| CI-04 | Criar tarefa com título vazio. | HTTP 422 e nenhuma tarefa gravada. | `test_invalid_task_payload_is_rejected_without_persisting` |
| CI-05 | Criar tarefa com status fora do conjunto permitido. | HTTP 422 e nenhuma tarefa gravada. | `test_invalid_task_payload_is_rejected_without_persisting` |

## Registro e execução

Os prompts e os casos gerados foram revisados em relação às regras implementadas antes de serem convertidos em testes executáveis. Os testes exercitam a API, o serviço e o repositório real com um banco temporário; não substituem componentes internos por mocks.

Execute a cobertura registrada neste repositório com:

```bash
uv run pytest tests/test_task_integration.py
```
