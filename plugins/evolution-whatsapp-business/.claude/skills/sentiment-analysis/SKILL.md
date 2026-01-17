---
name: sentiment-analysis
description: Analisa o tom emocional e intencao das mensagens
---

# Sentiment Analysis

Entende o estado emocional e a verdadeira intencao por tras de cada mensagem.

## Uso

```
Qual o sentimento da conversa com Maria?
Analise o tom das ultimas mensagens
Quais clientes estao frustrados?
```

## Dimensoes

### 1. Sentimento (Valence)

| Categoria | Score | Indicadores |
|-----------|-------|-------------|
| Muito Positivo | 0.8-1.0 | Elogios, entusiasmo |
| Positivo | 0.6-0.8 | Interesse, cordialidade |
| Neutro | 0.4-0.6 | Informativo |
| Negativo | 0.2-0.4 | Frustracao |
| Muito Negativo | 0.0-0.2 | Raiva, reclamacao |

### 2. Urgencia (Arousal)

| Nivel | Score | Indicadores |
|-------|-------|-------------|
| Critico | 0.8-1.0 | "URGENTE", "agora" |
| Alto | 0.6-0.8 | "preciso", "hoje" |
| Medio | 0.4-0.6 | "quando possivel" |
| Baixo | 0.0-0.4 | "sem pressa" |

### 3. Intencao (Intent)

| Intencao | Exemplo |
|----------|---------|
| COMPRA | "Quanto custa?" |
| INFORMACAO | "Como funciona?" |
| SUPORTE | "Nao funciona" |
| RECLAMACAO | "Pessimo!" |
| AGENDAMENTO | "Tem horario?" |
| NEGOCIACAO | "Faz desconto?" |
| CANCELAMENTO | "Quero cancelar" |

## Padroes

### Positivos

```yaml
muito_positivo:
  - "excelente", "perfeito", "maravilhoso"
  - "muito obrigado", "agradeco"
  - emojis: ["😊", "🙏", "❤️"]

positivo:
  - "obrigado", "legal", "bom"
  - "gostei", "interessante"
  - emojis: ["👍", "😀"]
```

### Negativos

```yaml
negativo:
  - "nao gostei", "ruim"
  - "demorado", "caro demais"
  - emojis: ["😕", "😔"]

muito_negativo:
  - "pessimo", "horrivel"
  - "nunca mais", "procon"
  - emojis: ["😡", "🤬"]
```

## Alertas de Churn

Detectar risco de perder cliente:

| Situacao | Acao |
|----------|------|
| Valence < 0.2 | Escalar para humano |
| Sentimento piorando | Aumentar prioridade |
| Pediu cancelamento | Retencao imediata |
| Reclamacao | Atendimento urgente |

## Output

```json
{
  "remote_jid": "5511999999999@s.whatsapp.net",
  "analysis": {
    "valence": 0.35,
    "valence_label": "NEGATIVO",
    "arousal": 0.75,
    "urgency_label": "ALTO",
    "intent": "RECLAMACAO",
    "intent_confidence": 0.89,
    "emotions": ["frustracao", "impaciencia"],
    "sentiment_shift": "DETERIORATING"
  },
  "flags": {
    "requires_human": true,
    "churn_risk": true
  },
  "recommendations": {
    "priority": "URGENT",
    "response_tone": "empatico_conciliador"
  }
}
```

## Metricas

```
💭 SENTIMENTO HOJE
════════════════════

📊 DISTRIBUICAO
   Muito Positivo: 15%
   Positivo: 46%
   Neutro: 24%
   Negativo: 12%
   Muito Negativo: 3%

⚠️ ALERTAS DE CHURN
   1. Maria - Reclamacao prazo
   2. Pedro - Cancelamento
   3. Ana - Piorando

🎯 INTENCOES
   Compra: 23%
   Informacao: 31%
   Suporte: 19%
```

## Calibracao

Ajustes automaticos:

- Cliente recorrente: +0.1
- Primeiro contato: -0.05
- Horario comercial: +0.05
- Fora do horario: -0.05
