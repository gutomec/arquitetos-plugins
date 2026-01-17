---
name: wa-esquecidos
description: Lista conversas sem resposta por mais de 1 hora
---

# /wa-esquecidos

Lista todas as conversas que estao aguardando resposta por mais de 1 hora (timeout configuravel).

## Uso

```
/wa-esquecidos              # Lista todos os esquecidos
/wa-esquecidos --urgent     # Apenas criticos (> 2h)
/wa-esquecidos --all        # Incluir todos os tempos
/wa-esquecidos [numero]     # Ver detalhes e responder
```

## Lista de Esquecidos

```
/wa-esquecidos

⏰ CONVERSAS ESQUECIDAS
════════════════════════════════════════

⚠️ 7 conversas aguardando resposta > 1 hora

Por prioridade:

🔴 CRITICO (> 2 horas)
────────────────────────────────────────
1. Ana Oliveira                    2h 34min
   Score: 45 | FOLLOW_UP
   "Pode me ligar quando puder?"
   [📞 Ligar] [💬 Responder] [✓ Marcar respondido]

2. Carlos Dias                     1h 58min
   Score: 52 | OPPORTUNITY
   "Vou pensar no orcamento que mandou"
   [💬 Follow-up] [📋 Ver proposta] [✓ Marcar]


🟠 ALERTA (1-2 horas)
────────────────────────────────────────
3. Julia Lima                      1h 23min
   Score: 38 | FOLLOW_UP
   "Quando fica pronto o servico?"
   [💬 Responder] [✓ Marcar respondido]

4. Roberto Silva                   1h 15min
   Score: 29 | INFORMATIVE
   "Ok, obrigado pela informacao"
   [✓ Encerrar] [💬 Responder]

5. Fernanda Costa                  1h 02min
   Score: 61 | OPPORTUNITY
   "Me manda fotos do produto?"
   [📷 Enviar fotos] [💬 Responder]


📊 RESUMO
   Criticos (>2h): 2
   Alerta (1-2h): 5
   SLA violado: 5 (de 7)
   Valor em risco: R$ 28.500
```

## Detalhes do Esquecido

```
/wa-esquecidos 5511999999999

⏰ CONVERSA ESQUECIDA
════════════════════════════════════════

👤 CONTATO
   Nome: Ana Oliveira
   Telefone: +55 11 99999-9999
   Esperando: 2h 34min

📊 CLASSIFICACAO
   Score: 45 (FOLLOW_UP)
   Intencao: SUPORTE
   SLA: ⚠️ VIOLADO (max 60min)

💬 ULTIMA MENSAGEM
   "Pode me ligar quando puder? Preciso tirar
   uma duvida sobre o pedido que fiz semana
   passada. Obrigada!"

   Enviada: 17/01/2026 11:58

📜 CONTEXTO (ultimas 5 msgs)
   [11:58] Ana: Pode me ligar quando puder?
   [11:45] Ana: Oi, tudo bem?
   [10:30] Voce: Bom dia Ana! Tudo sim, e voce?
   [10:28] Ana: Oi, bom dia!
   [15/01] Voce: Pedido enviado, codigo XYZ123

💡 SUGESTAO DE RESPOSTA
   "Oi Ana! Desculpa a demora. Posso te ligar
   agora ou prefere que eu responda por aqui
   mesmo? Sobre qual pedido e a duvida?"

🎯 ACOES
   [📞 Ligar agora]
   [💬 Usar sugestao]
   [✏️ Escrever resposta]
   [✓ Marcar como respondido]
   [🔕 Ignorar (nao relevante)]
```

## Resposta Rapida

```
/wa-esquecidos 5511999999999 --respond

💬 RESPONDER
════════════════════════════════════════

Para: Ana Oliveira (+55 11 99999-9999)
Esperando: 2h 34min

Sugestoes de resposta:

[1] "Oi Ana! Desculpa a demora. Posso te ligar
    agora ou prefere que eu responda por aqui?"

[2] "Ola Ana! Vi sua mensagem agora. Como
    posso ajudar?"

[3] [Escrever resposta personalizada]

Escolha [1/2/3]: _

────────────────────────────────────────

Resposta escolhida: 1

✅ Mensagem enviada!
   Para: Ana Oliveira
   Horario: 14:32
   Status: Entregue ✓✓
```

## Marcar como Respondido

```
/wa-esquecidos 5511999999999 --done

✅ MARCADO COMO RESPONDIDO
════════════════════════════════════════

Contato: Ana Oliveira
Tempo de espera: 2h 34min
Status: Respondido externamente

📊 Metricas atualizadas:
   - Removido da lista de esquecidos
   - SLA registrado como violado
   - Historico atualizado
```

## Bulk Actions

```
/wa-esquecidos --mark-all-non-urgent

🔄 ACAO EM MASSA
════════════════════════════════════════

Marcar como "nao urgente":
   - Roberto Silva (1h 15min) - "Ok, obrigado"
   - Marcos Lima (1h 05min) - "Valeu!"

Confirmar? [s/n]: s

✅ 2 conversas marcadas como encerradas
   (Mensagens de cortesia, sem acao necessaria)
```

## Filtros

```
/wa-esquecidos --filter score>=50

⏰ ESQUECIDOS COM SCORE >= 50
════════════════════════════════════════

Total: 3 conversas (de 7)
Valor em risco: R$ 22.700

1. Carlos Dias (52 pts) - 1h 58min
2. Fernanda Costa (61 pts) - 1h 02min
3. Amanda Santos (55 pts) - 1h 01min

💡 Estas sao oportunidades reais!
   Responda prioritariamente.
```

## Configuracao

O timeout e configuravel em `config/sla-thresholds.yaml`:

```yaml
conversation_timeout_minutes: 60  # Padrao
critical_threshold_minutes: 120   # Critico
```

## Alertas

O sistema gera alertas quando:

- Nova conversa atinge 50% do SLA
- Conversa atinge 100% do SLA (violacao)
- Conversa atinge 150% do SLA (critico)

```
⚠️ ALERTA DE SLA
────────────────────────────────────────
Ana Oliveira esta esperando ha 2h34min
SLA maximo: 60min
Acao: Responder imediatamente
```
