#!/bin/bash
# =============================================================================
# HYBRID-KB - Script de Deploy para VPS
# =============================================================================
# Uso: ./deploy.sh [comando]
# Comandos: install, start, stop, restart, logs, status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker nao instalado. Instale com: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose nao instalado."
        exit 1
    fi
}

# Verificar .env
check_env() {
    if [ ! -f .env ]; then
        log_warn ".env nao encontrado. Criando a partir do exemplo..."
        cp .env.example .env
        log_warn "Configure o arquivo .env com suas credenciais antes de iniciar!"
        exit 1
    fi
}

# Comandos
install() {
    log_info "Instalando Hybrid-KB..."
    check_docker
    check_env

    log_info "Baixando imagens..."
    docker compose -f docker-compose.prod.yml pull

    log_info "Construindo MCP server..."
    docker compose -f docker-compose.prod.yml build hybrid-kb

    log_info "Instalacao concluida!"
    log_info "Execute: ./deploy.sh start"
}

start() {
    log_info "Iniciando servicos..."
    check_env
    docker compose -f docker-compose.prod.yml up -d

    log_info "Aguardando health checks..."
    sleep 10

    status
}

stop() {
    log_info "Parando servicos..."
    docker compose -f docker-compose.prod.yml down
    log_info "Servicos parados."
}

restart() {
    stop
    start
}

logs() {
    local service="${2:-}"
    if [ -n "$service" ]; then
        docker compose -f docker-compose.prod.yml logs -f "$service"
    else
        docker compose -f docker-compose.prod.yml logs -f
    fi
}

status() {
    log_info "Status dos servicos:"
    echo ""
    docker compose -f docker-compose.prod.yml ps
    echo ""

    # Verificar endpoints
    log_info "Endpoints:"
    echo "  - Milvus:      http://localhost:19530"
    echo "  - Neo4j:       http://localhost:7474 (browser)"
    echo "  - Neo4j Bolt:  bolt://localhost:7687"
    echo "  - Attu (UI):   http://localhost:8000"
}

# Menu principal
case "${1:-}" in
    install)
        install
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$@"
        ;;
    status)
        status
        ;;
    *)
        echo "Uso: $0 {install|start|stop|restart|logs|status}"
        echo ""
        echo "Comandos:"
        echo "  install  - Baixar imagens e construir containers"
        echo "  start    - Iniciar todos os servicos"
        echo "  stop     - Parar todos os servicos"
        echo "  restart  - Reiniciar todos os servicos"
        echo "  logs     - Ver logs (opcional: logs <servico>)"
        echo "  status   - Ver status dos servicos"
        exit 1
        ;;
esac
