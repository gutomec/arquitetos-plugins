---
name: wa-setup
description: Configuracao inicial do sistema SDR Virtual
---

# /wa-setup

Comando de configuracao inicial do sistema. Deve ser executado apos instalacao para configurar conexoes e preferencias.

## Uso

```
/wa-setup
```

## Fluxo de Configuracao

### 1. Verificar Conexoes

Teste automaticamente todas as conexoes:

```
🔌 VERIFICANDO CONEXOES
════════════════════════════════════════

1. Evolution API
   URL: $EVOLUTION_API_URL
   Status: ✅ Conectado
   Instancia: $EVOLUTION_INSTANCE

2. PostgreSQL
   Host: $POSTGRES_HOST
   Database: $POSTGRES_DB
   Status: ✅ Conectado
   Tabela Message: ✅ Existe (1.2M registros)

3. Redis
   Host: $REDIS_HOST
   Status: ✅ Conectado

4. MinIO
   Endpoint: $MINIO_ENDPOINT
   Bucket: $MINIO_BUCKET
   Status: ✅ Conectado

5. Google Calendar
   Status: ⚠️ Token expirado
   Acao: Execute /wa-setup google-auth

6. HubSpot
   Status: ✅ Conectado
   Contatos: 1,234

7. Stripe
   Status: ✅ Conectado
   Modo: Live
```

### 2. Configurar Modo de Operacao

```
⚙️ MODO DE OPERACAO
════════════════════════════════════════

Escolha o modo de operacao:

1. STEALTH (Recomendado para inicio)
   - Observa e classifica conversas
   - NAO responde automaticamente
   - Gera alertas e relatorios

2. ACTIVE
   - Observa, classifica E responde
   - Responde dentro do horario comercial
   - Limite de 3 respostas por conversa

3. HYBRID
   - Responde apenas Hot Leads (score >= 80)
   - Demais conversas em modo stealth

Modo atual: STEALTH
Alterar? [1/2/3/n]:
```

### 3. Configurar Thresholds

```
📊 THRESHOLDS
════════════════════════════════════════

Hot Lead (responder em 5 min):
  Score minimo: [80] _

SLA Timeout (alerta de esquecido):
  Minutos: [60] _

Horario Comercial:
  Inicio: [08:00] _
  Fim: [18:00] _
  Dias: [1,2,3,4,5] _ (1=seg, 7=dom)

Timezone: [America/Sao_Paulo] _
```

### 4. Configurar Notificacoes

```
🔔 NOTIFICACOES
════════════════════════════════════════

Canais disponiveis:

[x] Dashboard (sempre ativo)
[ ] WhatsApp do Dono
    Numero: _______________

[ ] Email
    Endereco: _______________

[ ] Webhook Externo
    URL: _______________

Tipos de alerta:
[x] Hot Lead detectado
[x] SLA violado
[x] Relatorio diario
[ ] Toda nova mensagem
```

### 5. Criar Tabelas Auxiliares

```sql
-- Executar migracao
CREATE TABLE IF NOT EXISTS wa_pipeline (...);
CREATE TABLE IF NOT EXISTS wa_score_history (...);
CREATE TABLE IF NOT EXISTS wa_sla_tracking (...);
CREATE TABLE IF NOT EXISTS wa_spam_log (...);
CREATE TABLE IF NOT EXISTS wa_sentiment_log (...);
CREATE TABLE IF NOT EXISTS wa_auto_responses (...);
```

### 6. Validacao Final

```
✅ CONFIGURACAO COMPLETA
════════════════════════════════════════

Sistema configurado com sucesso!

📌 Proximos passos:

1. Execute /wa-dashboard para ver o painel
2. Use /wa-leads para ver oportunidades
3. Use /wa-mode para alterar modo de operacao

💡 Dicas:
- Comece em modo STEALTH para conhecer seu fluxo
- Apos 1 semana, avalie mudar para HYBRID
- Ajuste thresholds conforme seu negocio

📖 Documentacao: CLAUDE.md
```

## Opcoes

```
/wa-setup                 # Setup completo
/wa-setup verify          # Apenas verificar conexoes
/wa-setup google-auth     # Reautenticar Google
/wa-setup hubspot-sync    # Sincronizar HubSpot
/wa-setup migrate         # Rodar migracoes de banco
/wa-setup reset           # Resetar configuracoes
```

## Variaveis de Ambiente

O setup verifica se todas as variaveis em `.env` estao configuradas:

```
EVOLUTION_API_URL ✅
EVOLUTION_API_KEY ✅
EVOLUTION_INSTANCE ✅
POSTGRES_HOST ✅
POSTGRES_PASSWORD ⚠️ Usando valor padrao
REDIS_HOST ✅
MINIO_ENDPOINT ✅
GOOGLE_CLIENT_ID ❌ Faltando
HUBSPOT_API_KEY ✅
STRIPE_SECRET_KEY ✅
```

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| Evolution nao conecta | Verifique URL e API_KEY |
| PostgreSQL nao conecta | Verifique credenciais e porta |
| Tabela Message vazia | Webhook pode nao estar configurado |
| Google Token expirado | Execute /wa-setup google-auth |
