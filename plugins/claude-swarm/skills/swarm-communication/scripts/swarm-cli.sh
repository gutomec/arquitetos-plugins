#!/bin/bash
# swarm-cli.sh - CLI unificado para comandos do Swarm
# Uso: swarm-cli <comando> [args...]

set -e

REDIS_HOST="${SWARM_REDIS_HOST:-localhost}"
REDIS_PORT="${SWARM_REDIS_PORT:-6379}"
REDIS_CLI="redis-cli -h $REDIS_HOST -p $REDIS_PORT"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Gerar UUID
generate_uuid() {
    cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen || date +%s%N
}

# Comando: publish
cmd_publish() {
    local channel="$1"
    local payload="$2"

    if [ -z "$channel" ] || [ -z "$payload" ]; then
        echo "Uso: swarm-cli publish <channel> '<json_payload>'"
        exit 1
    fi

    # Validar JSON
    if ! echo "$payload" | jq . > /dev/null 2>&1; then
        log_error "Payload nao e JSON valido"
        exit 1
    fi

    # Adicionar metadata se nao existir
    if ! echo "$payload" | jq -e '.id' > /dev/null 2>&1; then
        payload=$(echo "$payload" | jq --arg id "$(generate_uuid)" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '. + {id: $id, timestamp: $ts}')
    fi

    # Publicar
    $REDIS_CLI PUBLISH "swarm:tasks:$channel" "$payload" > /dev/null
    log_success "Publicado em swarm:tasks:$channel"
    echo "$payload" | jq -c '.id'
}

# Comando: subscribe
cmd_subscribe() {
    local channel="$1"
    local timeout="${2:-0}"

    if [ -z "$channel" ]; then
        echo "Uso: swarm-cli subscribe <channel> [timeout_seconds]"
        exit 1
    fi

    log_info "Escutando swarm:$channel..."

    if [ "$timeout" -gt 0 ]; then
        timeout "$timeout" $REDIS_CLI SUBSCRIBE "swarm:$channel" 2>/dev/null | while read -r type; do
            read -r ch
            read -r message
            if [ "$type" = "message" ]; then
                echo "$message"
            fi
        done
    else
        $REDIS_CLI SUBSCRIBE "swarm:$channel" | while read -r type; do
            read -r ch
            read -r message
            if [ "$type" = "message" ]; then
                echo "$message"
            fi
        done
    fi
}

# Comando: collect
cmd_collect() {
    local task_id="$1"
    local timeout="${2:-30}"

    if [ -z "$task_id" ]; then
        echo "Uso: swarm-cli collect <task_id> [timeout_seconds]"
        exit 1
    fi

    log_info "Aguardando resultado de $task_id (timeout: ${timeout}s)..."

    local start_time=$(date +%s)
    while true; do
        # Verificar se resultado existe
        local result=$($REDIS_CLI GET "swarm:results:$task_id")
        if [ -n "$result" ]; then
            echo "$result"
            return 0
        fi

        # Verificar timeout
        local elapsed=$(($(date +%s) - start_time))
        if [ "$elapsed" -ge "$timeout" ]; then
            log_error "Timeout aguardando resultado"
            return 1
        fi

        sleep 0.5
    done
}

# Comando: state
cmd_state() {
    local action="$1"
    local key="$2"
    local value="$3"

    case "$action" in
        set)
            if [ -z "$key" ] || [ -z "$value" ]; then
                echo "Uso: swarm-cli state set <key> '<value>'"
                exit 1
            fi
            $REDIS_CLI SET "swarm:state:$key" "$value" > /dev/null
            log_success "Estado salvo: $key"
            ;;
        get)
            if [ -z "$key" ]; then
                echo "Uso: swarm-cli state get <key>"
                exit 1
            fi
            $REDIS_CLI GET "swarm:state:$key"
            ;;
        del)
            if [ -z "$key" ]; then
                echo "Uso: swarm-cli state del <key>"
                exit 1
            fi
            $REDIS_CLI DEL "swarm:state:$key" > /dev/null
            log_success "Estado deletado: $key"
            ;;
        keys)
            local pattern="${key:-*}"
            $REDIS_CLI KEYS "swarm:state:$pattern"
            ;;
        *)
            echo "Uso: swarm-cli state <set|get|del|keys> [args...]"
            exit 1
            ;;
    esac
}

# Comando: health
cmd_health() {
    log_info "Verificando saude dos workers..."

    local workers=$($REDIS_CLI KEYS "swarm:heartbeat:*")

    if [ -z "$workers" ]; then
        log_warn "Nenhum worker registrado"
        return 1
    fi

    local now=$(date +%s)
    local healthy=0
    local unhealthy=0

    for key in $workers; do
        local worker_name=$(echo "$key" | sed 's/swarm:heartbeat://')
        local last_seen=$($REDIS_CLI GET "$key")
        local age=$((now - last_seen))

        if [ "$age" -lt 30 ]; then
            log_success "$worker_name: alive (last seen: ${age}s ago)"
            ((healthy++))
        else
            log_error "$worker_name: dead (last seen: ${age}s ago)"
            ((unhealthy++))
        fi
    done

    echo ""
    log_info "Total: $healthy healthy, $unhealthy unhealthy"

    [ "$unhealthy" -eq 0 ]
}

# Comando: broadcast
cmd_broadcast() {
    local action="$1"
    local message="$2"

    if [ -z "$action" ]; then
        echo "Uso: swarm-cli broadcast <pause|resume|status|shutdown> [message]"
        exit 1
    fi

    local payload=$(jq -n \
        --arg type "BROADCAST" \
        --arg id "$(generate_uuid)" \
        --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --arg action "$action" \
        --arg msg "$message" \
        '{type: $type, id: $id, timestamp: $ts, from: "orchestrator", to: "*", payload: {action: $action, message: $msg}}'
    )

    $REDIS_CLI PUBLISH "swarm:broadcast" "$payload" > /dev/null
    log_success "Broadcast enviado: $action"
}

# Comando: init
cmd_init() {
    log_info "Inicializando Swarm..."

    # Verificar Redis
    if ! $REDIS_CLI PING > /dev/null 2>&1; then
        log_error "Redis nao esta acessivel em $REDIS_HOST:$REDIS_PORT"
        exit 1
    fi
    log_success "Redis conectado"

    # Limpar estado antigo
    $REDIS_CLI KEYS "swarm:*" | xargs -r $REDIS_CLI DEL > /dev/null 2>&1
    log_success "Estado limpo"

    # Registrar orchestrator
    $REDIS_CLI SET "swarm:heartbeat:orchestrator" "$(date +%s)" > /dev/null
    log_success "Orchestrator registrado"

    log_success "Swarm inicializado!"
}

# Comando: shutdown
cmd_shutdown() {
    log_warn "Encerrando Swarm..."

    # Enviar broadcast de shutdown
    cmd_broadcast "shutdown" "Swarm shutting down"

    # Aguardar workers finalizarem
    sleep 2

    # Limpar estado
    $REDIS_CLI KEYS "swarm:*" | xargs -r $REDIS_CLI DEL > /dev/null 2>&1

    log_success "Swarm encerrado"
}

# Main
case "$1" in
    publish)
        cmd_publish "$2" "$3"
        ;;
    subscribe)
        cmd_subscribe "$2" "$3"
        ;;
    collect)
        cmd_collect "$2" "$3"
        ;;
    state)
        cmd_state "$2" "$3" "$4"
        ;;
    health)
        cmd_health
        ;;
    broadcast)
        cmd_broadcast "$2" "$3"
        ;;
    init)
        cmd_init
        ;;
    shutdown)
        cmd_shutdown
        ;;
    *)
        echo "Claude Swarm CLI"
        echo ""
        echo "Comandos:"
        echo "  publish <channel> <payload>  - Publicar mensagem"
        echo "  subscribe <channel> [timeout] - Escutar canal"
        echo "  collect <task_id> [timeout]  - Coletar resultado"
        echo "  state <set|get|del|keys> ... - Gerenciar estado"
        echo "  health                       - Verificar workers"
        echo "  broadcast <action> [msg]     - Broadcast para todos"
        echo "  init                         - Inicializar swarm"
        echo "  shutdown                     - Encerrar swarm"
        exit 1
        ;;
esac
