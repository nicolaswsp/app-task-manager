# Task Management Micro-API

Micro-API MVP para gestão de tarefas com priorização assistida por IA.

## Objetivo

Fornecer uma API leve e eficiente para gerenciamento de tarefas com sugestões inteligentes de priorização usando inteligência artificial, permitindo otimizar fluxos de trabalho pessoais e em equipe.

## Stack Tecnológico

- **Runtime**: Node.js / Python
- **Framework**: Express.js / FastAPI
- **Banco de Dados**: PostgreSQL / MongoDB
- **IA/ML**: OpenAI API / Hugging Face
- **Containerização**: Docker
- **Orquestração**: Docker Compose

## Como Rodar Localmente

### Pré-requisitos

- Docker e Docker Compose instalados
- Variáveis de ambiente configuradas (`.env`)

### Instalação

```sh
git clone {repositorio_url}
cd task-api
cp .env.example .env
docker-compose up -d