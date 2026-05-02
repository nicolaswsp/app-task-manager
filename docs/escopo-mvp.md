@"
# Escopo MVP - Micro-API de Tarefas

## Objetivo
Desenvolver uma micro-API RESTful para gerenciamento básico de tarefas, destinada ao uso interno da equipe, implementando operações CRUD essenciais e endpoint de saúde, com foco em simplicidade e deploy rápido.

## Requisitos Funcionais
- **Criação de Tarefa**: Endpoint POST para criar nova tarefa com campos obrigatórios (título, descrição, status).
- **Listagem de Tarefas**: Endpoint GET para recuperar lista de tarefas, com suporte a filtros por status.
- **Atualização de Tarefa**: Endpoint PUT/PATCH para modificar tarefa existente.
- **Exclusão de Tarefa**: Endpoint DELETE para remover tarefa por ID.
- **Endpoint de Saúde**: Endpoint GET /health para verificação de disponibilidade da API.

## Requisitos Não Funcionais
- **Performance**: Tempo de resposta < 500ms para operações CRUD sob carga de 100 requisições simultâneas.
- **Segurança**: Autenticação obrigatória via API key em headers; dados em trânsito criptografados via HTTPS.
- **Disponibilidade**: Uptime mínimo de 99% em ambiente de produção.
- **Escalabilidade**: Arquitetura stateless, compatível com containerização (Docker) e orquestração básica (Kubernetes).
- **Manutenibilidade**: Código documentado, com logs estruturados e cobertura de testes unitários > 80%.

## Fora de Escopo
- Interface de usuário (frontend).
- Notificações push ou e-mail para tarefas.
- Integração com sistemas externos (e.g., calendários, ferramentas de projeto).
- Versionamento avançado da API (além de v1).
- Autenticação multiusuário ou RBAC complexo.
- Persistência em bancos de dados relacionais avançados (foco em SQLite ou similar para MVP).
"@ | Out-File -FilePath docs/escopo-mvp.md -Encoding UTF8