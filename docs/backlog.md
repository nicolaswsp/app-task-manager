@"
# Backlog MVP - Micro-API de Tarefas

## Release Core
- [ ] RF001: Implementar endpoint POST /tasks para criação de tarefa
  - Critérios de aceite: Receber JSON com título, descrição, status; retornar 201 com ID gerado; validar campos obrigatórios.
- [ ] RF002: Implementar endpoint GET /tasks para listagem de tarefas
  - Critérios de aceite: Retornar lista JSON de tarefas; suportar filtro por status via query param; retornar 200.
- [ ] RF003: Implementar endpoint PUT /tasks/{id} para atualização de tarefa
  - Critérios de aceite: Receber JSON com campos a atualizar; retornar 200 se sucesso; 404 se ID inexistente.
- [ ] RF004: Implementar endpoint DELETE /tasks/{id} para exclusão de tarefa
  - Critérios de aceite: Remover tarefa por ID; retornar 204 se sucesso; 404 se ID inexistente.
- [ ] RF005: Implementar endpoint GET /health para verificação de saúde
  - Critérios de aceite: Retornar 200 com status "ok"; sem dependências externas.
- [ ] RT001: Configurar autenticação básica via API key
  - Critérios de aceite: Validar header X-API-Key; retornar 401 se inválido; armazenar key em variável de ambiente.
- [ ] RT002: Implementar persistência em SQLite
  - Critérios de aceite: Criar tabela tasks; operações CRUD funcionais; dados persistidos entre restarts.

## Release Qualidade
- [ ] RT003: Adicionar logs estruturados
  - Critérios de aceite: Logs em JSON para requests/responses; níveis info/error; integrável com ferramentas como ELK.
- [ ] RT004: Implementar testes unitários para endpoints
  - Critérios de aceite: Cobertura > 80%; usar pytest; testes para cenários de sucesso e erro.
- [ ] RT005: Adicionar validação de entrada com Pydantic
  - Critérios de aceite: Schemas para requests; retornar 400 para dados inválidos; mensagens de erro claras.
- [ ] RT006: Configurar containerização com Docker
  - Critérios de aceite: Dockerfile funcional; imagem buildável; app rodando em container.
- [ ] RF006: Adicionar paginação em GET /tasks
  - Critérios de aceite: Suporte a limit/offset; retornar metadados de paginação; performance mantida.

## Release Entrega Final
- [ ] RT007: Implementar métricas de performance com Prometheus
  - Critérios de aceite: Endpoint /metrics; métricas de latência e erros; compatível com monitoramento.
- [ ] RT008: Configurar CI/CD básico com GitHub Actions
  - Critérios de aceite: Pipeline para build, test e deploy; deploy automático em staging; notificações de falha.
- [ ] RT009: Adicionar documentação OpenAPI
  - Critérios de aceite: Swagger UI acessível; specs completas para todos endpoints; auto-gerada via FastAPI.
- [ ] RF007: Implementar cache básico para listagem
  - Critérios de aceite: Cache em memória para GET /tasks; TTL configurável; redução de latência em 20%.
- [ ] RT010: Otimizar para produção (Gunicorn + Uvicorn)
  - Critérios de aceite: Configuração para múltiplos workers; suporte a HTTPS; escalabilidade horizontal.
"@ | Out-File -FilePath docs/backlog.md -Encoding UTF8