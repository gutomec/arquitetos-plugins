---
description: Cria e gerencia swarms de agentes Claude em containers Docker. Use para orquestrar multiplos agentes que trabalham em paralelo e se comunicam entre si.
argument-hint: <action> [options] - Actions: create, status, execute, broadcast, shutdown
---

# /swarm - Claude Swarm Orchestration

Comando principal para criar e gerenciar swarms de agentes Claude containerizados.

## Parsing dos Argumentos

```
Input: $ARGUMENTS

Acoes disponiveis:
- create: Criar novo swarm
- status: Ver status do swarm atual
- execute: Executar tarefa distribuida
- broadcast: Enviar mensagem para todos workers
- shutdown: Encerrar swarm
```

## Execucao por Acao

### /swarm create

Cria um novo swarm de agentes.

**Sintaxe:**
```
/swarm create --workers <tipos> --name <nome>
```

**Exemplo:**
```
/swarm create --workers analyst,coder,reviewer,tester --name code-review-swarm
```

**Passos:**
1. Verificar se Docker esta rodando
2. Verificar se Redis esta acessivel
3. Inicializar infraestrutura do swarm
4. Criar containers para cada worker
5. Registrar workers no message broker
6. Confirmar swarm ativo

### /swarm status

Mostra status de todos os agentes do swarm.

**Sintaxe:**
```
/swarm status [--verbose]
```

**Output:**
```
SWARM STATUS: code-review-swarm
================================
Orchestrator: ACTIVE (uptime: 15m)
Workers:
  - analyst:  ACTIVE (tasks: 3, idle: 2m)
  - coder:    ACTIVE (tasks: 5, idle: 30s)
  - reviewer: ACTIVE (tasks: 2, idle: 1m)
  - tester:   BUSY   (current: task-abc123)

Message Broker: Redis @ localhost:6379 (connected)
Shared State: 12 keys
Pending Tasks: 2
Completed Tasks: 15
```

### /swarm execute

Executa uma tarefa distribuida entre os workers.

**Sintaxe:**
```
/swarm execute "<descricao da tarefa>" --strategy <estrategia>
```

**Estrategias:**
- `fan-out`: Distribuir para todos workers em paralelo
- `pipeline`: Encadear workers sequencialmente
- `map-reduce`: Dividir dados, processar em paralelo, agregar
- `auto`: Deixar orchestrator decidir

**Exemplo:**
```
/swarm execute "Review and improve the authentication module" --strategy fan-out
```

**Passos:**
1. Analisar tarefa e identificar workers necessarios
2. Escolher estrategia de execucao
3. Distribuir subtarefas para workers
4. Monitorar progresso
5. Coletar e sintetizar resultados
6. Apresentar resultado final

### /swarm broadcast

Envia mensagem para todos os workers.

**Sintaxe:**
```
/swarm broadcast <action> [message]
```

**Actions:**
- `pause`: Pausar todos workers
- `resume`: Retomar workers pausados
- `status`: Solicitar status de todos
- `context`: Atualizar contexto compartilhado

**Exemplo:**
```
/swarm broadcast context "Focus on security vulnerabilities"
```

### /swarm shutdown

Encerra o swarm graciosamente.

**Sintaxe:**
```
/swarm shutdown [--force]
```

**Passos:**
1. Enviar broadcast de shutdown
2. Aguardar tarefas em progresso (timeout: 30s)
3. Salvar estado final
4. Parar containers
5. Limpar recursos

## Workflow Interno

```yaml
name: swarm-orchestration
trigger: manual

steps:
  - id: parse_command
    action: parse_arguments
    extract: [action, options]

  - id: validate
    action: validate_prerequisites
    check: [docker, redis, permissions]

  - id: execute_action
    action: route_to_handler
    based_on: action
    handlers:
      create: handle_create
      status: handle_status
      execute: handle_execute
      broadcast: handle_broadcast
      shutdown: handle_shutdown

  - id: report
    action: format_output
    include: [status, metrics, errors]
```

## Configuracao

Variaveis de ambiente:
```bash
SWARM_REDIS_HOST=localhost
SWARM_REDIS_PORT=6379
SWARM_MAX_WORKERS=10
SWARM_TASK_TIMEOUT=300000
SWARM_CHECKPOINT_INTERVAL=60000
```

## Exemplos de Uso

### Criar swarm para code review
```
/swarm create --workers analyst,reviewer --name review-team
/swarm execute "Review PR #123 for security issues" --strategy fan-out
```

### Criar swarm para desenvolvimento
```
/swarm create --workers researcher,coder,tester --name dev-team
/swarm execute "Implement user authentication with JWT" --strategy pipeline
```

### Criar swarm para analise
```
/swarm create --workers analyst,researcher --name analysis-team
/swarm execute "Analyze codebase architecture and suggest improvements" --strategy fan-out
```

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| Docker nao encontrado | Instalar Docker e iniciar daemon |
| Redis nao conecta | Executar `docker-compose up redis` |
| Worker nao responde | Verificar logs: `docker logs swarm-worker-X` |
| Timeout frequente | Aumentar SWARM_TASK_TIMEOUT |
| Memoria insuficiente | Reduzir numero de workers |

## Seguranca

- Nunca executar como root
- Credenciais via Docker secrets
- Network isolation entre swarms
- Audit log de todas as operacoes
