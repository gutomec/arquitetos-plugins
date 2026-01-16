# Claude Swarm - Multi-Agent Container Orchestration

O plugin definitivo para criar e orquestrar multiplos agentes Claude Agent SDK que vivem em containers Docker e conversam entre si em tempo real.

## Arquitetura

```
+------------------------------------------------------------------+
|                         SWARM NETWORK                             |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+     +-------------------+                  |
|  |   ORCHESTRATOR    |     |   MESSAGE BROKER  |                  |
|  |   (Opus 4.5)      |<--->|   (Redis)         |                  |
|  |   Container       |     |   Container       |                  |
|  +-------------------+     +-------------------+                  |
|           |                        ^                              |
|           v                        |                              |
|  +--------+--------+--------+------+------+--------+             |
|  |        |        |        |             |        |             |
|  v        v        v        v             v        v             |
| +------+ +------+ +------+ +------+  +--------+ +----------+     |
| |Analyst| |Coder | |Review| |Tester|  |Research| | Custom   |    |
| +------+ +------+ +------+ +------+  +--------+ +----------+     |
|  Sonnet   Sonnet   Sonnet   Sonnet    Sonnet     Sonnet          |
|                                                                   |
+------------------------------------------------------------------+
|                    SHARED VOLUMES                                 |
|  /workspace (code) | /state (checkpoints) | /output (results)    |
+------------------------------------------------------------------+
```

## Estrutura do Plugin

```
claude-swarm/
├── README.md
├── .claude/
│   ├── agents/
│   │   ├── swarm-orchestrator.md     # Agente lider (Opus 4.5)
│   │   ├── swarm-worker-analyst.md   # Worker: analise
│   │   ├── swarm-worker-coder.md     # Worker: codificacao
│   │   ├── swarm-worker-reviewer.md  # Worker: revisao
│   │   ├── swarm-worker-tester.md    # Worker: testes
│   │   └── swarm-worker-researcher.md # Worker: pesquisa
│   ├── skills/
│   │   └── swarm-communication/
│   │       ├── SKILL.md              # Skill de comunicacao
│   │       └── scripts/
│   │           └── swarm-cli.sh      # CLI helper
│   ├── commands/
│   │   └── swarm.md                  # Comando /swarm
│   └── workflows/
│       ├── fan-out.yml               # Estrategia paralela
│       ├── pipeline.yml              # Estrategia sequencial
│       └── map-reduce.yml            # Estrategia map-reduce
├── python/                           # SDK Python
│   ├── requirements.txt
│   ├── config.py
│   ├── message_broker.py
│   ├── agents.py
│   ├── orchestrator.py
│   ├── process_task.py
│   ├── main.py
│   └── swarm_mcp_server.py           # MCP Server
├── typescript/                       # SDK TypeScript
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── config.ts
│       ├── types.ts
│       ├── message-broker.ts
│       ├── agents.ts
│       ├── orchestrator.ts
│       └── index.ts
└── docker/
    ├── docker-compose.yml            # Infraestrutura completa
    ├── Dockerfile.agent              # Imagem dos agentes
    └── entrypoint.sh                 # Entrypoint com message loop
```

## Componentes

| Componente | Descricao |
|------------|-----------|
| **Orchestrator** | Agente lider (Opus 4.5) que coordena todos os workers |
| **Workers** | 5 agentes especializados (Sonnet 4) que executam tarefas |
| **Message Broker** | Redis para comunicacao pub/sub entre agentes |
| **MCP Server** | Servidor de ferramentas para inter-agent communication |
| **Workflows** | 3 estrategias de orquestracao (fan-out, pipeline, map-reduce) |
| **SDK Python** | Implementacao completa em Python |
| **SDK TypeScript** | Implementacao completa em TypeScript |

## Workers Especializados

| Worker | Especialidade | Ferramentas |
|--------|--------------|-------------|
| **Analyst** | Analise de codigo e arquitetura | read_file, search_code, swarm_state |
| **Coder** | Implementacao e codificacao | read_file, write_file, edit_file |
| **Reviewer** | Revisao de codigo e seguranca | read_file, search_code |
| **Tester** | Criacao e execucao de testes | read_file, write_file, run_command |
| **Researcher** | Pesquisa e coleta de informacoes | web_search, web_fetch |

## Instalacao

### 1. Copiar Plugin para Claude Code

```bash
# Clonar ou copiar plugin
cp -r plugins/claude-swarm/.claude/* ~/.claude/

# Ou para projeto especifico
cp -r plugins/claude-swarm/.claude/* seu-projeto/.claude/
```

### 2. Iniciar Infraestrutura Docker

```bash
cd plugins/claude-swarm/docker

# Configurar API key
export ANTHROPIC_API_KEY=sua-chave-aqui

# Iniciar swarm completo
docker-compose up -d

# Verificar status
docker-compose ps
```

### 3. Usar via Python SDK

```bash
cd plugins/claude-swarm/python
pip install -r requirements.txt

# Iniciar worker standalone
python main.py worker analyst

# Executar tarefa
python main.py execute "Analyze the codebase architecture"

# Ver status
python main.py status
```

### 4. Usar via TypeScript SDK

```bash
cd plugins/claude-swarm/typescript
npm install
npm run build

# Iniciar worker
npm run worker -- analyst

# Executar tarefa
npm start -- execute "Review security vulnerabilities"
```

## Comandos

| Comando | Descricao |
|---------|-----------|
| `/swarm create` | Criar novo swarm de agentes |
| `/swarm status` | Ver status dos agentes ativos |
| `/swarm execute` | Executar tarefa distribuida |
| `/swarm broadcast` | Enviar mensagem para todos os agentes |
| `/swarm shutdown` | Encerrar swarm graciosamente |

### Exemplos

```bash
# Criar swarm para code review
/swarm create --workers analyst,coder,reviewer,tester --name review-team

# Executar tarefa com estrategia especifica
/swarm execute "Review PR #123 for security issues" --strategy fan-out

# Executar tarefa com estrategia automatica
/swarm execute "Implement user authentication with JWT" --strategy auto

# Verificar status
/swarm status --verbose

# Broadcast para pausar todos
/swarm broadcast pause "Taking a break"

# Encerrar
/swarm shutdown
```

## Estrategias de Orquestracao

### 1. Fan-Out (Paralelo)
Distribui tarefa para todos os workers simultaneamente e agrega resultados.

```
Orchestrator --[TASK]--+--> Analyst   --+
                       +--> Coder     --+--> [SYNTHESIZE] --> Result
                       +--> Reviewer  --+
                       +--> Tester    --+
```

**Ideal para**: Tarefas independentes, code review multiperspectiva, analises paralelas.

### 2. Pipeline (Sequencial)
Encadeia workers, cada um recebendo o output do anterior.

```
Researcher --> Analyst --> Coder --> Reviewer --> Tester --> Result
```

**Ideal para**: Desenvolvimento de features, workflows com dependencias.

### 3. Map-Reduce (Dividir e Agregar)
Divide dados em chunks, processa em paralelo, e agrega resultados.

```
       +--> Worker [chunk 1] --+
Data --+--> Worker [chunk 2] --+--> [REDUCE] --> Result
       +--> Worker [chunk 3] --+
```

**Ideal para**: Processamento de grandes volumes, analise de codebases extensas.

## Uso Programatico

### Python

```python
import asyncio
from orchestrator import Orchestrator, ExecutionStrategy

async def main():
    # Criar orchestrator
    orch = Orchestrator()

    # Executar com estrategia automatica
    result = await orch.execute(
        "Review and improve the authentication module",
        strategy=ExecutionStrategy.AUTO
    )

    print(result["synthesis"])

    # Executar pipeline especifico
    result = await orch.execute(
        "Implement feature X",
        strategy=ExecutionStrategy.PIPELINE
    )

    # Verificar saude do swarm
    health = await orch.health_check()
    print(f"Workers ativos: {health['healthy']}/{health['total']}")

    # Encerrar
    await orch.shutdown()

asyncio.run(main())
```

### TypeScript

```typescript
import { Orchestrator, ExecutionStrategy } from 'claude-swarm';

async function main() {
  const orch = new Orchestrator();

  // Executar tarefa
  const result = await orch.execute(
    'Review and improve the authentication module',
    ExecutionStrategy.FAN_OUT
  );

  console.log(result.synthesis);

  // Verificar saude
  const health = await orch.healthCheck();
  console.log(`Workers: ${health.healthy}/${health.total}`);

  await orch.shutdown();
}

main();
```

## MCP Server Tools

O servidor MCP fornece as seguintes ferramentas para comunicacao entre agentes:

| Tool | Descricao |
|------|-----------|
| `swarm_publish` | Publica mensagem para um worker ou canal |
| `swarm_collect` | Coleta resultado de uma tarefa |
| `swarm_broadcast` | Envia broadcast para todos workers |
| `swarm_health_check` | Verifica saude de todos workers |
| `swarm_heartbeat` | Envia heartbeat de atividade |
| `swarm_state_set` | Salva estado compartilhado |
| `swarm_state_get` | Recupera estado compartilhado |
| `swarm_store_result` | Armazena resultado de tarefa |
| `swarm_list_pending` | Lista tarefas pendentes |
| `swarm_subscribe_once` | Aguarda mensagem em canal |

## Protocolo de Mensagens

### Formato de Mensagem

```json
{
  "type": "TASK|RESULT|BROADCAST|STATUS|ERROR",
  "id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "from": "orchestrator",
  "to": "worker-analyst",
  "payload": {
    "instruction": "Analyze the authentication module",
    "context": {}
  },
  "metadata": {
    "priority": "high|medium|low",
    "ttl": 300000
  }
}
```

### Canais Redis

| Canal | Uso |
|-------|-----|
| `swarm:tasks:{worker}` | Tarefas para worker especifico |
| `swarm:results:{task_id}` | Resultados de tarefas |
| `swarm:results:orchestrator` | Notificacoes para orchestrator |
| `swarm:broadcast` | Mensagens para todos workers |
| `swarm:heartbeat:{agent}` | Heartbeats de agentes |
| `swarm:state:{key}` | Estado compartilhado |

## Configuracao

### Variaveis de Ambiente

```bash
# Redis
SWARM_REDIS_HOST=localhost
SWARM_REDIS_PORT=6379
SWARM_REDIS_PASSWORD=
SWARM_REDIS_DB=0

# Agent
SWARM_AGENT_ID=worker-analyst
SWARM_AGENT_TYPE=analyst

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-20250514
ORCHESTRATOR_MODEL=claude-opus-4-5-20251101

# Timeouts
SWARM_TASK_TIMEOUT=300000
SWARM_COLLECT_TIMEOUT=30
SWARM_HEARTBEAT_INTERVAL=10
SWARM_HEARTBEAT_TTL=60

# Swarm
SWARM_MAX_WORKERS=10
SWARM_CHECKPOINT_INTERVAL=60000
SWARM_LOG_LEVEL=INFO
```

## Seguranca

- Cada container roda com usuario nao-root (`agent:swarm`)
- Network isolation via bridge network
- Credenciais via variaveis de ambiente (usar Docker secrets em producao)
- Resource limits por container (CPU e memoria)
- Health checks automaticos
- Heartbeat monitoring para detectar workers mortos
- TTL em mensagens para evitar acumulo

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| Docker nao encontrado | Instalar Docker e iniciar daemon |
| Redis nao conecta | `docker-compose up redis` |
| Worker nao responde | `docker logs swarm-worker-X` |
| Timeout frequente | Aumentar `SWARM_TASK_TIMEOUT` |
| Memoria insuficiente | Reduzir numero de workers |
| Heartbeat failing | Verificar conectividade Redis |

## Limitacoes Conhecidas

1. **Single Redis Instance**: Para alta disponibilidade, usar Redis Cluster
2. **Sem Persistencia de Tarefas**: Tarefas em andamento sao perdidas em restart
3. **Sem Auto-scaling**: Numero de workers e fixo no docker-compose
4. **Sem TLS**: Comunicacao Redis nao e encriptada por padrao

## Roadmap

- [ ] Suporte a Redis Cluster
- [ ] Auto-scaling baseado em carga
- [ ] TLS para comunicacao Redis
- [ ] Dashboard de monitoramento
- [ ] Persistencia de tarefas em andamento
- [ ] Rate limiting por worker
- [ ] Suporte a webhooks

## Licenca

MIT

---

Criado por Ultra Arquiteto de Plugins v1.0
