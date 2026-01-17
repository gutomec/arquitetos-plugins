#!/bin/bash
# Hook: daily-report
# Trigger: Scheduled (08:00)
# Descricao: Gera e envia relatorio diario automatico

# Este hook deve ser executado via cron ou scheduler
# Exemplo de cron: 0 8 * * * /path/to/daily-report.sh

# Configuracoes
PROJECT_ROOT="${PROJECT_ROOT:-$(dirname $(dirname $(dirname $0)))}"
source "${PROJECT_ROOT}/.env" 2>/dev/null || true

REPORT_TIME="${DAILY_REPORT_TIME:-08:00}"
TIMEZONE="${BUSINESS_HOURS_TIMEZONE:-America/Sao_Paulo}"
LOG_FILE="${PROJECT_ROOT}/logs/daily-report.log"

# Funcao para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Funcao para gerar metricas do dia anterior
generate_metrics() {
    log "Gerando metricas..."

    # Metricas basicas (seriam obtidas via MCP)
    local yesterday=$(date -d "yesterday" '+%Y-%m-%d')

    echo "📊 RELATORIO DIARIO - $yesterday"
    echo "════════════════════════════════════════"
    echo ""
    echo "📬 Mensagens"
    echo "   Recebidas: [DADOS_MCP]"
    echo "   Enviadas: [DADOS_MCP]"
    echo ""
    echo "🔥 Leads"
    echo "   Hot Leads: [DADOS_MCP]"
    echo "   Oportunidades: [DADOS_MCP]"
    echo ""
    echo "💰 Vendas"
    echo "   Fechadas: [DADOS_MCP]"
    echo "   Valor: [DADOS_MCP]"
    echo ""
    echo "⏱️ SLA"
    echo "   Taxa: [DADOS_MCP]%"
    echo "   Tempo medio: [DADOS_MCP] min"
}

# Funcao para enviar via WhatsApp
send_whatsapp_report() {
    local report="$1"

    if [ -n "$OWNER_WHATSAPP_NUMBER" ] && [ -n "$EVOLUTION_API_URL" ]; then
        log "Enviando relatorio via WhatsApp..."

        curl -s -X POST "${EVOLUTION_API_URL}/message/sendText/${EVOLUTION_INSTANCE}" \
            -H "Content-Type: application/json" \
            -H "apikey: ${EVOLUTION_API_KEY}" \
            -d "{
                \"number\": \"${OWNER_WHATSAPP_NUMBER}\",
                \"text\": \"${report}\"
            }"

        log "Relatorio enviado para ${OWNER_WHATSAPP_NUMBER}"
    else
        log "WhatsApp nao configurado, pulando envio"
    fi
}

# Funcao para enviar via Email
send_email_report() {
    local report="$1"
    local subject="Relatorio Diario - $(date '+%d/%m/%Y')"

    if [ -n "$NOTIFICATION_EMAIL" ]; then
        log "Enviando relatorio via Email..."

        # Usar mailx, sendmail, ou integrar com Gmail MCP
        if command -v mail &> /dev/null; then
            echo "$report" | mail -s "$subject" "$NOTIFICATION_EMAIL"
            log "Email enviado para ${NOTIFICATION_EMAIL}"
        else
            log "Comando mail nao disponivel"
        fi
    fi
}

# Funcao para salvar relatorio
save_report() {
    local report="$1"
    local date_str=$(date '+%Y-%m-%d')
    local report_dir="${PROJECT_ROOT}/reports"
    local report_file="${report_dir}/relatorio_${date_str}.txt"

    mkdir -p "$report_dir"
    echo "$report" > "$report_file"
    log "Relatorio salvo em $report_file"
}

# Funcao para verificar se e hora de executar
should_run() {
    local current_time=$(TZ="$TIMEZONE" date '+%H:%M')

    if [ "$current_time" = "$REPORT_TIME" ]; then
        return 0
    fi
    return 1
}

# Funcao principal
main() {
    log "=== Inicio do hook daily-report ==="

    # Verificar se deve executar (se chamado via cron com verificacao)
    if [ "$1" = "--check-time" ]; then
        if ! should_run; then
            log "Nao e hora de executar ($REPORT_TIME)"
            exit 0
        fi
    fi

    # Gerar relatorio
    local report=$(generate_metrics)

    # Salvar
    save_report "$report"

    # Enviar por canais configurados
    send_whatsapp_report "$report"
    send_email_report "$report"

    log "=== Fim do hook daily-report ==="

    # Output para Claude
    echo "$report"
}

# Executar
main "$@"
