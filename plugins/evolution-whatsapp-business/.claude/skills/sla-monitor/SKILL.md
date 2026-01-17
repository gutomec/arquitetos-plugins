---
name: sla-monitor
description: Monitora tempos de resposta e alerta sobre violacoes de SLA
---

# SLA Monitor

Monitora continuamente os tempos de resposta e gera alertas quando SLAs estao prestes a ser violados.

## Uso

```
Verifique o status de SLA
Quais conversas estao atrasadas?
Gere relatorio de SLA do dia
```

## SLAs por Classificacao

| Classificacao | Tempo Maximo | Alerta Em | Critico Em |
|---------------|--------------|-----------|------------|
| HOT_LEAD | 5 min | 3 min | 5 min |
| OPPORTUNITY | 30 min | 20 min | 30 min |
| FOLLOW_UP | 60 min | 45 min | 60 min |
| INFORMATIVE | 120 min | 90 min | 120 min |

## Niveis de Alerta

| Nivel | Cor | Condicao | Acao |
|-------|-----|----------|------|
| INFO | Verde | 50% do SLA | Log apenas |
| WARNING | Amarelo | 75% do SLA | Dashboard |
| CRITICAL | Laranja | 100% do SLA | Notificacao push |
| URGENT | Vermelho | 150% do SLA | Alerta sonoro |

## Monitoramento

### Query de Conversas Aguardando

```sql
WITH conversas AS (
  SELECT
    "remoteJid",
    MAX("messageTimestamp") as ultima_msg_cliente,
    MAX(CASE WHEN "fromMe" THEN "messageTimestamp" ELSE 0 END) as ultima_resposta
  FROM "Message"
  WHERE "messageTimestamp" > EXTRACT(EPOCH FROM NOW() - INTERVAL '24 hours')
  GROUP BY "remoteJid"
)
SELECT
  "remoteJid",
  ROUND((EXTRACT(EPOCH FROM NOW()) - ultima_msg_cliente) / 60) as minutos_esperando
FROM conversas
WHERE ultima_msg_cliente > ultima_resposta
ORDER BY minutos_esperando DESC;
```

### Conversas Esquecidas (>1h)

```sql
SELECT
  "remoteJid",
  "pushName",
  MAX("messageTimestamp") as ultima_msg,
  ROUND((EXTRACT(EPOCH FROM NOW()) - MAX("messageTimestamp")) / 60) as minutos
FROM "Message"
WHERE "fromMe" = false
  AND "messageTimestamp" > EXTRACT(EPOCH FROM NOW() - INTERVAL '24 hours')
GROUP BY "remoteJid", "pushName"
HAVING (EXTRACT(EPOCH FROM NOW()) - MAX("messageTimestamp")) > 3600
ORDER BY minutos DESC;
```

## Metricas

### Tempo Medio de Resposta

```sql
SELECT
  AVG(response_time) / 60 as avg_minutes,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time) / 60 as median_minutes,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) / 60 as p95_minutes
FROM wa_response_times
WHERE created_at > NOW() - INTERVAL '24 hours';
```

### Taxa de Resposta em SLA

```sql
SELECT
  COUNT(*) FILTER (WHERE within_sla) as dentro,
  COUNT(*) as total,
  ROUND(100.0 * COUNT(*) FILTER (WHERE within_sla) / COUNT(*), 1) as taxa
FROM wa_sla_tracking
WHERE created_at > NOW() - INTERVAL '24 hours';
```

## Escalonamento

### Niveis

| Multiplicador | Acao |
|---------------|------|
| 1.0x SLA | Alerta no dashboard |
| 1.5x SLA | Notificacao push |
| 2.0x SLA | Email para dono |
| 3.0x SLA | Marcar como perdido |

### Configuracao

```yaml
# config/sla-thresholds.yaml
escalation:
  level_1:
    multiplier: 1.0
    action: dashboard_alert
  level_2:
    multiplier: 1.5
    action: push_notification
  level_3:
    multiplier: 2.0
    action: email_owner
  level_4:
    multiplier: 3.0
    action: mark_as_lost
```

## Output

```json
{
  "timestamp": "2026-01-17T14:40:00Z",
  "summary": {
    "within_sla": 142,
    "warning": 3,
    "critical": 2,
    "urgent": 0
  },
  "forgotten_conversations": [
    {
      "remote_jid": "5511999999999@s.whatsapp.net",
      "contact_name": "Maria Santos",
      "wait_time_minutes": 154,
      "classification": "OPPORTUNITY",
      "sla_minutes": 30,
      "exceeded_by": 124,
      "urgency": "CRITICAL"
    }
  ],
  "avg_response_time": 23,
  "sla_rate": 87.5
}
```

## Relatorio

```
📊 RELATORIO DE SLA - 17/01/2026
════════════════════════════════════════

⏱️ TEMPO MEDIO DE RESPOSTA
   Hoje: 23 min (Alvo: 15 min) ⚠️
   Ontem: 18 min
   Semana: 21 min

✅ TAXA DE RESPOSTA EM SLA
   Hoje: 87% (Alvo: 95%) ⚠️
   Ontem: 92%
   Semana: 89%

🔴 VIOLACOES DE SLA HOJE
   Hot Leads: 2 (de 8)
   Oportunidades: 5 (de 23)
   Follow-ups: 3 (de 15)

⏰ ESQUECIDOS AGORA: 5
   1. Maria Santos - 2h34min
   2. Pedro Costa - 1h58min
   3. Ana Oliveira - 1h23min
```

## Configuracao

Edite `config/sla-thresholds.yaml` para ajustar tempos.
