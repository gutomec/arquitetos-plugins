---
name: daily-digest
description: Gera relatorios consolidados diarios e semanais
---

# Daily Digest

Gera relatorios consolidados com todas as metricas e insights do dia/semana.

## Uso

```
Gere o relatorio do dia
Relatorio semanal de vendas
Resumo de performance da semana
```

## Horario Automatico

O relatorio diario e gerado automaticamente as 08:00 (configurable).

```yaml
# config/sla-thresholds.yaml
daily_report_time: "08:00"
weekly_report_day: "monday"
timezone: "America/Sao_Paulo"
```

## Secoes do Relatorio

### 1. Resumo Executivo

```
📊 RESUMO EXECUTIVO - 17/01/2026
════════════════════════════════════════

✅ DESTAQUES DO DIA
   • 7 vendas fechadas (R$ 52.300)
   • Taxa de conversao: 31.8% (+5.2%)
   • Tempo medio resposta: 18 min

⚠️ PONTOS DE ATENCAO
   • 5 conversas esquecidas
   • SLA abaixo da meta (87%)
   • 2 hot leads nao respondidos
```

### 2. Metricas de Volume

```
📈 VOLUME DE MENSAGENS
════════════════════════════════════════

   Recebidas: 147
   Enviadas: 89
   Ratio: 1.65

   Por Tipo:
   └── Texto: 112 (76%)
   └── Audio: 23 (16%)
   └── Imagem: 8 (5%)
   └── Outros: 4 (3%)
```

### 3. Pipeline de Vendas

```
🎯 PIPELINE
════════════════════════════════════════

   LEAD          │ 23 │ ████████████
   MQL           │ 12 │ ██████
   SQL           │  8 │ ████
   OPPORTUNITY   │  5 │ ██
   PROPOSAL      │  3 │ █
   ────────────────────────────────────
   WON (mes)     │  7 │ R$ 52.300
   LOST (mes)    │ 15 │ (31.8% taxa)

   💰 Valor em Pipeline: R$ 125.000
```

### 4. Leads e Oportunidades

```
🔥 HOT LEADS DO DIA
════════════════════════════════════════

1. Maria Santos (92 pts)
   "Quanto custa consultoria?"
   ⏱️ Respondido em 3 min ✅

2. Joao Silva (87 pts)
   "Preciso urgente para hoje"
   ⏱️ Respondido em 8 min ✅

3. Pedro Costa (85 pts)
   "Aceita pix?"
   ⏱️ NAO RESPONDIDO ⚠️
```

### 5. SLA e Tempos

```
⏱️ PERFORMANCE DE SLA
════════════════════════════════════════

   Tempo Medio Resposta: 18 min
   Alvo: 15 min
   Status: ⚠️ ACIMA DO ALVO

   Taxa em SLA:
   └── Hot Leads: 85% (alvo: 95%)
   └── Oportunidades: 78% (alvo: 90%)
   └── Follow-ups: 92% (alvo: 85%)

   Conversas Esquecidas: 5
   └── Maria Santos - 2h34min
   └── Pedro Costa - 1h58min
```

### 6. Sentimento

```
💭 ANALISE DE SENTIMENTO
════════════════════════════════════════

   😊 Positivo: 61%
   😐 Neutro: 27%
   😕 Negativo: 12%

   Tendencia: ESTAVEL

   ⚠️ Clientes em Risco:
   └── Ana Lima - sentiment deteriorating
   └── Carlos Dias - pediu cancelamento
```

### 7. Spam e Filtros

```
🛡️ PROTECAO ANTI-SPAM
════════════════════════════════════════

   Analisadas: 147
   Spam Detectado: 23 (15.6%)
   Phishing Bloqueado: 5

   Por Categoria:
   └── Comercial: 12
   └── Phishing: 5
   └── Correntes: 4
   └── Bots: 2
```

### 8. Top Acoes

```
🎯 ACOES RECOMENDADAS
════════════════════════════════════════

1. URGENTE: Responder Pedro Costa (hot lead)
2. Follow-up: 3 propostas pendentes
3. Recuperar: 5 conversas esquecidas
4. Celebrar: 7 vendas fechadas! 🎉
```

## Queries SQL

### Metricas do Dia

```sql
SELECT
  COUNT(*) as total_messages,
  COUNT(*) FILTER (WHERE "fromMe" = false) as received,
  COUNT(*) FILTER (WHERE "fromMe" = true) as sent
FROM "Message"
WHERE "messageTimestamp" > EXTRACT(EPOCH FROM NOW() - INTERVAL '24 hours');
```

### Conversoes

```sql
SELECT
  COUNT(*) FILTER (WHERE stage = 'WON') as won,
  SUM(actual_value) FILTER (WHERE stage = 'WON') as revenue
FROM wa_pipeline
WHERE won_at > NOW() - INTERVAL '24 hours';
```

## Output

```json
{
  "report_date": "2026-01-17",
  "period": "daily",
  "summary": {
    "messages_received": 147,
    "messages_sent": 89,
    "hot_leads": 8,
    "opportunities": 23,
    "conversions": 7,
    "revenue": 52300.00,
    "avg_response_time_minutes": 18,
    "sla_rate": 87.5
  },
  "alerts": [
    "5 conversas esquecidas",
    "SLA abaixo da meta",
    "2 hot leads nao respondidos"
  ],
  "recommendations": [
    "Responder Pedro Costa imediatamente",
    "Follow-up em 3 propostas pendentes"
  ]
}
```

## Canais de Entrega

O relatorio pode ser enviado via:

1. **Dashboard**: Exibido na tela inicial
2. **WhatsApp**: Enviado para o dono
3. **Email**: Via Gmail integration
4. **Webhook**: Para sistemas externos

## Configuracao

```yaml
# config/notification-channels.yaml
daily_digest:
  enabled: true
  time: "08:00"
  channels:
    - dashboard
    - owner_whatsapp
  include:
    - summary
    - pipeline
    - hot_leads
    - sla
    - actions
```
