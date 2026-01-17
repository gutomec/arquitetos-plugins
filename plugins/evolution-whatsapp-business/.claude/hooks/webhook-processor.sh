#!/bin/bash
# Hook: webhook-processor
# Trigger: UserPromptSubmit
# Descricao: Processa webhooks da Evolution API recebidos

# Este hook e acionado quando o usuario submete um prompt
# Verifica se o prompt contem dados de webhook e os processa

# Configuracoes do ambiente
source "${PROJECT_ROOT}/.env" 2>/dev/null || true

# Funcao para verificar se e um webhook da Evolution
is_evolution_webhook() {
    local input="$1"
    # Verifica se contem estrutura de webhook da Evolution API
    if echo "$input" | grep -q '"event".*"messages.upsert"'; then
        return 0
    fi
    return 1
}

# Funcao para extrair dados do webhook
extract_webhook_data() {
    local webhook_json="$1"

    # Extrai campos principais usando jq (se disponivel)
    if command -v jq &> /dev/null; then
        remote_jid=$(echo "$webhook_json" | jq -r '.data.key.remoteJid // empty')
        push_name=$(echo "$webhook_json" | jq -r '.data.pushName // empty')
        from_me=$(echo "$webhook_json" | jq -r '.data.key.fromMe // false')
        timestamp=$(echo "$webhook_json" | jq -r '.data.messageTimestamp // empty')
        instance=$(echo "$webhook_json" | jq -r '.instance // empty')

        echo "WEBHOOK_DATA:"
        echo "  remote_jid: $remote_jid"
        echo "  push_name: $push_name"
        echo "  from_me: $from_me"
        echo "  timestamp: $timestamp"
        echo "  instance: $instance"
    else
        echo "WARN: jq nao instalado, processamento limitado"
        echo "$webhook_json"
    fi
}

# Funcao para notificar sobre nova mensagem
notify_new_message() {
    local remote_jid="$1"
    local push_name="$2"

    # Log para debug
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Nova mensagem de $push_name ($remote_jid)" >> "${PROJECT_ROOT}/logs/webhook.log"
}

# Funcao principal
main() {
    local input="$1"

    # Verifica se e um webhook
    if is_evolution_webhook "$input"; then
        echo "📩 Webhook da Evolution API detectado"
        extract_webhook_data "$input"

        # Aciona processamento pelo agente
        echo ""
        echo "Processando com wa-inbox-monitor..."
    fi
}

# Executa se receber input
if [ -n "$CLAUDE_USER_PROMPT" ]; then
    main "$CLAUDE_USER_PROMPT"
fi
