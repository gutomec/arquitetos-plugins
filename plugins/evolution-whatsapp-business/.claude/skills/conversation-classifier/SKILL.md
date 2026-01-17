---
name: conversation-classifier
description: Classifica conversas do WhatsApp em categorias de negocio
triggers:
  - webhook:messages.upsert
---

# Conversation Classifier

Classifica automaticamente cada conversa do WhatsApp em categorias de negocio para priorizacao.

## Uso

Esta skill e acionada automaticamente quando uma nova mensagem chega via webhook. Pode tambem ser chamada manualmente:

```
Classifique a conversa com 5511999999999
```

## Categorias

| Categoria | Score | Cor | Significado |
|-----------|-------|-----|-------------|
| HOT_LEAD | 80-100 | Vermelho | Oportunidade urgente de venda |
| OPPORTUNITY | 50-79 | Laranja | Potencial de negocio |
| FOLLOW_UP | 30-49 | Amarelo | Requer acompanhamento |
| INFORMATIVE | 10-29 | Verde | Conversa normal |
| SPAM | 0-9 | Preto | Irrelevante/spam |

## Algoritmo

### Fatores de Pontuacao

#### Keywords (max 30 pts)
- Hot keywords (+30): "quanto custa", "preco", "urgente", "comprar"
- Opportunity keywords (+20): "orcamento", "interessado", "gostaria"
- Follow-up keywords (+10): "vou pensar", "depois"
- Negative keywords (-20): "nao quero", "caro demais"

#### Comportamento (max 40 pts)
- Cliente iniciou conversa: +15
- 3+ mensagens seguidas: +10
- Resposta rapida (<1min): +10
- Enviou midia: +5

#### Temporal (max 10 pts)
- Horario comercial: +5
- Primeiro contato do dia: +5

#### Historico (max 20 pts)
- Cliente recorrente: +15
- 2+ conversas previas: +5

## Output

```json
{
  "classification": "HOT_LEAD",
  "score": 85,
  "confidence": 0.92,
  "factors": {
    "keywords": 30,
    "behavior": 25,
    "temporal": 10,
    "history": 20
  },
  "intent": "COMPRA",
  "recommended_action": "Responder imediatamente"
}
```

## Configuracao

Edite `config/scoring-weights.yaml` para ajustar pesos.

## Integracao

Esta skill alimenta:
- wa-lead-scorer
- wa-sdr-manager
- Dashboard de Hot Leads
