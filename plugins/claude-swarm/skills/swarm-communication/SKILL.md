---
name: swarm-communication
description: Skill para comunicacao entre agentes Claude em containers. Permite enviar mensagens, broadcasts, coletar resultados e gerenciar estado compartilhado via Redis. Use quando precisar que agentes conversem entre si.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Swarm Communication Skill

Sistema de comunicacao inter-agente para Claude Swarm usando Redis como message broker.

## Quick Start

```bash
# Verificar se Redis esta rodando
redis-cli ping

# Publicar mensagem para um worker
swarm-publish worker-analyst '{"task": "analyze code", "files": ["src/"]}'

# Coletar resultado
swarm-collect task-123 --timeout 30
```

## Arquitetura de Canais

```
swarm:tasks:{worker}     - Canal para enviar tarefas (orchestrator -> worker)
swarm:results:{agent}    - Canal para receber resultados (worker -> orchestrator)
swarm:broadcast          - Canal para mensagens globais (orchestrator -> todos)
swarm:status             - Canal para heartbeat e status
swarm:state:{key}        - Chaves para estado compartilhado
```

## Comandos Disponiveis

### swarm-publish
Publica mensagem em um canal.

```bash
# Sintaxe
swarm-publish <canal> '<json_payload>'

# Exemplos
swarm-publish worker-analyst '{"type":"TASK","payload":{"instruction":"Analyze security"}}'
swarm-publish broadcast '{"type":"STATUS","action":"pause"}'
```

### swarm-subscribe
Escuta mensagens de um canal.

```bash
# Sintaxe
swarm-subscribe <canal> [--timeout <seconds>]

# Exemplos
swarm-subscribe results --timeout 60
swarm-subscribe broadcast
```

### swarm-collect
Coleta resultado de uma tarefa especifica.

```bash
# Sintaxe
swarm-collect <task_id> [--timeout <seconds>]

# Exemplo
swarm-collect task-abc123 --timeout 30
```

### swarm-state
Gerencia estado compartilhado.

```bash
# Salvar estado
swarm-state set checkpoint '{"step": 3, "partial": [...]}'

# Recuperar estado
swarm-state get checkpoint

# Listar chaves
swarm-state keys "swarm:state:*"

# Deletar estado
swarm-state del checkpoint
```

### swarm-health
Verifica saude dos workers.

```bash
# Verificar todos os workers
swarm-health check

# Output esperado:
# worker-analyst: alive (last seen: 2s ago)
# worker-coder: alive (last seen: 1s ago)
# worker-reviewer: dead (last seen: 120s ago)
```

## Protocolo de Mensagens

### Estrutura Base
```json
{
  "type": "TASK|RESULT|BROADCAST|STATUS|ERROR",
  "id": "uuid-da-mensagem",
  "timestamp": "2026-01-16T12:00:00Z",
  "from": "agent-origem",
  "to": "agent-destino|*",
  "payload": { ... },
  "metadata": {
    "priority": "high|medium|low",
    "ttl": 60000,
    "retry_count": 0
  }
}
```

### Tipos de Mensagem

#### TASK
```json
{
  "type": "TASK",
  "id": "task-123",
  "from": "orchestrator",
  "to": "worker-analyst",
  "payload": {
    "instruction": "Analyze the authentication module for security issues",
    "context": {
      "files": ["src/auth/"],
      "focus": ["sql-injection", "xss"]
    },
    "constraints": {
      "max_files": 10,
      "timeout_ms": 30000
    },
    "expected_output": "structured-report"
  }
}
```

#### RESULT
```json
{
  "type": "RESULT",
  "id": "task-123",
  "from": "worker-analyst",
  "to": "orchestrator",
  "payload": {
    "status": "success|partial|failed",
    "result": { ... },
    "metrics": {
      "duration_ms": 5000,
      "tokens_used": 1500
    }
  }
}
```

#### BROADCAST
```json
{
  "type": "BROADCAST",
  "id": "bc-456",
  "from": "orchestrator",
  "to": "*",
  "payload": {
    "action": "pause|resume|status|shutdown",
    "message": "Optional human-readable message"
  }
}
```

## Padroes de Comunicacao

### Fan-Out (Distribuir tarefa para multiplos workers)
```bash
# Orchestrator envia para todos os workers em paralelo
for worker in analyst coder reviewer tester; do
  swarm-publish "worker-$worker" "$TASK_JSON" &
done
wait
```

### Fan-In (Coletar resultados de multiplos workers)
```bash
# Aguardar resultados com timeout
RESULTS=""
for i in $(seq 1 $NUM_WORKERS); do
  RESULT=$(swarm-subscribe results --timeout 60)
  RESULTS="$RESULTS$RESULT\n"
done
echo "$RESULTS"
```

### Pipeline (Encadear workers)
```bash
# Worker 1 -> Worker 2 -> Worker 3
RESULT1=$(swarm-publish worker-analyst "$TASK" && swarm-collect $TASK_ID)
TASK2=$(echo "$RESULT1" | jq '. + {stage: 2}')
RESULT2=$(swarm-publish worker-coder "$TASK2" && swarm-collect $TASK_ID)
# ...
```

## Estado Compartilhado

### Checkpoints
```bash
# Salvar checkpoint
swarm-state set "checkpoint:$TASK_ID" '{
  "step": 2,
  "completed_workers": ["analyst", "coder"],
  "pending_workers": ["reviewer", "tester"],
  "partial_results": [...]
}'

# Recuperar para retry
CHECKPOINT=$(swarm-state get "checkpoint:$TASK_ID")
```

### Locks
```bash
# Adquirir lock
swarm-state setnx "lock:resource" "$AGENT_ID"

# Liberar lock
swarm-state del "lock:resource"
```

## Tratamento de Erros

### Timeout
```bash
RESULT=$(swarm-collect $TASK_ID --timeout 30)
if [ $? -ne 0 ]; then
  echo "Task timeout - retrying..."
  # Re-enviar tarefa
fi
```

### Worker Morto
```bash
if ! swarm-health check worker-analyst; then
  echo "Worker down - reallocating task..."
  swarm-publish worker-coder "$TASK"  # Fallback para outro worker
fi
```

## Seguranca

- Nunca incluir credenciais em mensagens
- Validar JSON antes de publicar
- Usar TTL para evitar mensagens orfas
- Implementar rate limiting se necessario
- Logar todas as mensagens para auditoria

## Scripts Auxiliares

Os scripts estao em `scripts/`:
- `swarm-publish.sh` - Publicar mensagem
- `swarm-subscribe.sh` - Escutar canal
- `swarm-collect.sh` - Coletar resultado
- `swarm-state.sh` - Gerenciar estado
- `swarm-health.sh` - Health check

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| Mensagem nao chega | Verificar se Redis esta rodando |
| Timeout frequente | Aumentar TTL ou verificar worker |
| Estado inconsistente | Limpar chaves e reiniciar |
| Worker nao responde | Verificar logs do container |
