#!/bin/bash
# Hook: sla-alert
# Trigger: PostToolUse
# Descricao: Alerta sobre violacoes de SLA apos cada uso de ferramenta

# Este hook e acionado apos cada uso de ferramenta
# Verifica se ha conversas violando SLA e alerta

# Configuracoes
SLA_TIMEOUT_MINUTES=${SLA_TIMEOUT_MINUTES:-60}
HOT_LEAD_MINUTES=${HOT_LEAD_MINUTES:-5}
PROJECT_ROOT="${PROJECT_ROOT:-.}"

# Cores para output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Funcao para verificar SLA via banco
check_sla_violations() {
    # Se PostgreSQL estiver configurado
    if [ -n "$EVOLUTION_DATABASE_URI" ]; then
        # Query para conversas esquecidas
        local query="
        SELECT COUNT(*)
        FROM (
            SELECT \"remoteJid\"
            FROM \"Message\"
            WHERE \"fromMe\" = false
              AND \"messageTimestamp\" > EXTRACT(EPOCH FROM NOW() - INTERVAL '24 hours')
            GROUP BY \"remoteJid\"
            HAVING (EXTRACT(EPOCH FROM NOW()) - MAX(\"messageTimestamp\")) > $((SLA_TIMEOUT_MINUTES * 60))
        ) esquecidos;
        "

        # Executar query (requer psql ou conexao MCP)
        # Aqui seria integrado com o MCP postgres
        echo "CHECK_SLA"
    fi
}

# Funcao para exibir alerta
show_alert() {
    local count="$1"
    local type="$2"

    case "$type" in
        "critical")
            echo -e "${RED}🔴 ALERTA CRITICO DE SLA${NC}"
            echo -e "${RED}$count conversas aguardando resposta!${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️ ALERTA DE SLA${NC}"
            echo -e "${YELLOW}$count conversas proximas do timeout${NC}"
            ;;
        "ok")
            echo -e "${GREEN}✅ SLA OK${NC}"
            ;;
    esac
}

# Funcao para notificar via WhatsApp (se configurado)
notify_owner() {
    local message="$1"

    if [ -n "$OWNER_WHATSAPP_NUMBER" ] && [ -n "$EVOLUTION_API_URL" ]; then
        # Enviar notificacao via Evolution API
        curl -s -X POST "${EVOLUTION_API_URL}/message/sendText/${EVOLUTION_INSTANCE}" \
            -H "Content-Type: application/json" \
            -H "apikey: ${EVOLUTION_API_KEY}" \
            -d "{
                \"number\": \"${OWNER_WHATSAPP_NUMBER}\",
                \"text\": \"${message}\"
            }" > /dev/null 2>&1
    fi
}

# Funcao principal
main() {
    local tool_name="$1"
    local tool_result="$2"

    # Verificar apenas apos certas ferramentas
    case "$tool_name" in
        "evolution-database"|"Read"|"Query")
            # Verificar SLA
            local violations=$(check_sla_violations)

            if [ "$violations" -gt 5 ]; then
                show_alert "$violations" "critical"
                notify_owner "⚠️ ALERTA: $violations conversas sem resposta ha mais de ${SLA_TIMEOUT_MINUTES} minutos!"
            elif [ "$violations" -gt 0 ]; then
                show_alert "$violations" "warning"
            fi
            ;;
    esac
}

# Executa se receber parametros de tool
if [ -n "$CLAUDE_TOOL_NAME" ]; then
    main "$CLAUDE_TOOL_NAME" "$CLAUDE_TOOL_RESULT"
fi

# Exibir status periodicamente (a cada 10 chamadas)
if [ -f "/tmp/sla_check_counter" ]; then
    counter=$(cat /tmp/sla_check_counter)
    counter=$((counter + 1))
else
    counter=1
fi
echo $counter > /tmp/sla_check_counter

if [ $((counter % 10)) -eq 0 ]; then
    echo ""
    echo "─────────────────────────────────────"
    echo "⏰ Verificacao periodica de SLA"
    check_sla_violations
    echo "─────────────────────────────────────"
fi
