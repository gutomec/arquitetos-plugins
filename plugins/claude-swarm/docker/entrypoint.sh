#!/bin/bash
# Claude Swarm Agent Entrypoint
# Inicializa o agente e conecta ao message broker

set -e

# =============================================================================
# CONFIGURATION
# =============================================================================

AGENT_ID="${SWARM_AGENT_ID:-unknown}"
AGENT_TYPE="${SWARM_AGENT_TYPE:-worker}"
REDIS_HOST="${SWARM_REDIS_HOST:-localhost}"
REDIS_PORT="${SWARM_REDIS_PORT:-6379}"

echo "========================================"
echo "  Claude Swarm Agent"
echo "========================================"
echo "  Agent ID:   $AGENT_ID"
echo "  Agent Type: $AGENT_TYPE"
echo "  Redis:      $REDIS_HOST:$REDIS_PORT"
echo "========================================"

# =============================================================================
# WAIT FOR REDIS
# =============================================================================

echo "[INFO] Aguardando Redis..."
until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; do
    echo "[WAIT] Redis nao disponivel, aguardando..."
    sleep 2
done
echo "[OK] Redis conectado"

# =============================================================================
# REGISTER AGENT
# =============================================================================

echo "[INFO] Registrando agente..."
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SET "swarm:heartbeat:$AGENT_ID" "$(date +%s)" EX 60
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET "swarm:agents:$AGENT_ID" \
    "type" "$AGENT_TYPE" \
    "status" "starting" \
    "started_at" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[OK] Agente registrado"

# =============================================================================
# HEARTBEAT BACKGROUND TASK
# =============================================================================

heartbeat_loop() {
    while true; do
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SET "swarm:heartbeat:$AGENT_ID" "$(date +%s)" EX 60 > /dev/null
        sleep 10
    done
}

heartbeat_loop &
HEARTBEAT_PID=$!
echo "[OK] Heartbeat iniciado (PID: $HEARTBEAT_PID)"

# =============================================================================
# SIGNAL HANDLERS
# =============================================================================

cleanup() {
    echo "[INFO] Encerrando agente..."

    # Parar heartbeat
    kill $HEARTBEAT_PID 2>/dev/null || true

    # Atualizar status
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET "swarm:agents:$AGENT_ID" "status" "stopped"
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" DEL "swarm:heartbeat:$AGENT_ID"

    echo "[OK] Agente encerrado"
    exit 0
}

trap cleanup SIGTERM SIGINT SIGQUIT

# =============================================================================
# MAIN LOOP
# =============================================================================

# Atualizar status para running
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET "swarm:agents:$AGENT_ID" "status" "running"

echo "[INFO] Agente ativo, escutando tarefas em swarm:tasks:$AGENT_ID..."

# Determinar canal baseado no tipo
if [ "$AGENT_TYPE" = "orchestrator" ]; then
    CHANNEL="swarm:results:orchestrator"
else
    CHANNEL="swarm:tasks:$AGENT_ID"
fi

# Subscribe e processar mensagens
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SUBSCRIBE "$CHANNEL" "swarm:broadcast" | while read -r type; do
    read -r channel
    read -r message

    if [ "$type" = "message" ]; then
        MSG_TYPE=$(echo "$message" | jq -r '.type // empty')
        MSG_ID=$(echo "$message" | jq -r '.id // empty')

        echo "[RECV] $MSG_TYPE from $channel (ID: $MSG_ID)"

        case "$MSG_TYPE" in
            "TASK")
                echo "[TASK] Processando tarefa $MSG_ID..."

                # Atualizar status
                redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET "swarm:agents:$AGENT_ID" \
                    "status" "busy" \
                    "current_task" "$MSG_ID" > /dev/null

                # Extrair instrucao
                INSTRUCTION=$(echo "$message" | jq -r '.payload.instruction // empty')

                # Processar com Claude Agent SDK
                RESULT=$(python3 /app/python/process_task.py "$AGENT_TYPE" "$INSTRUCTION" 2>&1) || RESULT='{"error": "Processing failed"}'

                # Armazenar resultado
                RESULT_MSG=$(jq -n \
                    --arg type "RESULT" \
                    --arg id "$MSG_ID" \
                    --arg from "$AGENT_ID" \
                    --arg to "orchestrator" \
                    --argjson result "$RESULT" \
                    '{type: $type, id: $id, from: $from, to: $to, payload: {status: "success", result: $result}}'
                )

                redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SETEX "swarm:results:$MSG_ID" 300 "$RESULT_MSG" > /dev/null
                redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PUBLISH "swarm:results:orchestrator" "$RESULT_MSG" > /dev/null

                # Atualizar status
                redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET "swarm:agents:$AGENT_ID" \
                    "status" "running" \
                    "current_task" "" \
                    "last_task" "$MSG_ID" > /dev/null

                echo "[DONE] Tarefa $MSG_ID completada"
                ;;

            "BROADCAST")
                ACTION=$(echo "$message" | jq -r '.payload.action // empty')
                echo "[BROADCAST] Acao recebida: $ACTION"

                case "$ACTION" in
                    "shutdown")
                        echo "[SHUTDOWN] Recebido comando de shutdown"
                        cleanup
                        ;;
                    "pause")
                        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET "swarm:agents:$AGENT_ID" "status" "paused" > /dev/null
                        echo "[PAUSED] Agente pausado"
                        ;;
                    "resume")
                        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HSET "swarm:agents:$AGENT_ID" "status" "running" > /dev/null
                        echo "[RESUMED] Agente retomado"
                        ;;
                    "status")
                        # Responder com status
                        STATUS=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" HGETALL "swarm:agents:$AGENT_ID")
                        echo "[STATUS] $STATUS"
                        ;;
                esac
                ;;
        esac
    fi
done

# Manter processo vivo
wait
