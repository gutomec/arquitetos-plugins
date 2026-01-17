---
name: lead-scoring
description: Calcula score de oportunidade de 0 a 100 para cada lead
---

# Lead Scoring

Sistema de pontuacao que avalia o potencial comercial de cada conversa.

## Uso

```
Qual o score do lead 5511999999999?
Recalcule o score de todos os leads ativos
```

## Formula

```
Score Final = Keywords + Comportamento + Temporal + Historico
           = (0-30) + (0-40) + (0-10) + (0-20)
           = 0 a 100
```

## Componentes

### 1. Keywords (0-30)

Analise do texto das mensagens:

```yaml
hot_keywords: # +30 pontos
  - "quanto custa"
  - "qual o preco"
  - "preciso urgente"
  - "quero comprar"

opportunity_keywords: # +20 pontos
  - "me envia orcamento"
  - "estou interessado"
  - "gostaria de saber"

followup_keywords: # +10 pontos
  - "vou pensar"
  - "deixa eu ver"

negative_keywords: # -20 pontos
  - "nao tenho interesse"
  - "muito caro"
```

### 2. Comportamento (0-40)

Acoes do contato:

| Acao | Pontos |
|------|--------|
| Cliente iniciou conversa | +15 |
| 3+ mensagens seguidas | +10 |
| Respondeu em <1 min | +10 |
| Enviou audio/imagem | +5 |

### 3. Temporal (0-10)

Contexto de tempo:

| Fator | Pontos |
|-------|--------|
| Horario comercial | +5 |
| Primeiro contato do dia | +5 |

### 4. Historico (0-20)

Relacionamento anterior:

| Fator | Pontos |
|-------|--------|
| Ja comprou antes | +15 |
| 2+ conversas previas | +5 |

## Thresholds

| Score | Classificacao | SLA Resposta |
|-------|---------------|--------------|
| 80-100 | HOT_LEAD | 5 minutos |
| 50-79 | OPPORTUNITY | 30 minutos |
| 30-49 | FOLLOW_UP | 1 hora |
| 10-29 | INFORMATIVE | 4 horas |
| 0-9 | SPAM | Ignorar |

## Recalculo Automatico

O score e recalculado quando:

1. Nova mensagem do contato
2. Resposta enviada
3. Tempo passa sem resposta (+5/hora)
4. Dados do CRM atualizados

## Output

```json
{
  "remote_jid": "5511999999999@s.whatsapp.net",
  "score": 85,
  "previous_score": 65,
  "change": "+20",
  "classification": "HOT_LEAD",
  "breakdown": {
    "keywords": 30,
    "behavior": 25,
    "temporal": 10,
    "history": 20
  },
  "top_factors": [
    "Perguntou preco (+30)",
    "Cliente iniciou (+15)",
    "Cliente recorrente (+15)"
  ],
  "recommendation": "Priorizar resposta - hot lead detectado"
}
```

## Alertas

Score >= 80 gera alerta automatico:

```
🔴 HOT LEAD DETECTADO

Contato: Maria Santos
Score: 85 (+20 desde ultima msg)
Motivo: Perguntou preco, cliente recorrente

Ultima mensagem:
"Quanto custa o servico de consultoria?"

⏱️ SLA: Responder em 5 minutos
```

## Historico de Score

```sql
SELECT
  score,
  classification,
  recorded_at
FROM wa_score_history
WHERE remote_jid = $1
ORDER BY recorded_at DESC
LIMIT 10;
```

## Configuracao

Ajuste pesos em `config/scoring-weights.yaml`
