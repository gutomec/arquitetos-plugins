---
name: wa-leads
description: Lista e gerencia leads ativos no pipeline
---

# /wa-leads

Lista e gerencia todos os leads ativos no pipeline de vendas.

## Uso

```
/wa-leads                  # Lista todos os leads
/wa-leads hot              # Apenas hot leads (score >= 80)
/wa-leads opportunity      # Oportunidades (score 50-79)
/wa-leads pipeline         # Visao do funil completo
/wa-leads [numero]         # Detalhes de um lead especifico
```

## Lista de Leads

```
/wa-leads

🎯 LEADS ATIVOS
════════════════════════════════════════

Encontrados: 45 leads | Pipeline: R$ 125.000

┌─────────────────────────────────────────────────────────────────────────┐
│ #  │ Nome           │ Score │ Estagio     │ Valor Est. │ Esperando    │
├─────────────────────────────────────────────────────────────────────────┤
│ 1  │ Maria Santos   │  92🔴 │ OPPORTUNITY │ R$ 15.000  │ 3 min        │
│ 2  │ Joao Silva     │  87🔴 │ PROPOSAL    │ R$ 8.500   │ 8 min        │
│ 3  │ Pedro Costa    │  85🔴 │ OPPORTUNITY │ R$ 12.000  │ 15 min       │
│ 4  │ Ana Oliveira   │  72🟠 │ SQL         │ R$ 5.000   │ 45 min       │
│ 5  │ Carlos Dias    │  68🟠 │ SQL         │ R$ 7.200   │ 1h 23min     │
│ 6  │ Julia Lima     │  65🟠 │ MQL         │ R$ 3.500   │ 2h 15min     │
│ 7  │ Roberto Silva  │  52🟠 │ PROPOSAL    │ R$ 22.000  │ 3 dias       │
│ 8  │ Fernanda Costa │  48🟡 │ MQL         │ R$ 4.800   │ 1h 02min     │
└─────────────────────────────────────────────────────────────────────────┘

Legenda: 🔴 Hot Lead | 🟠 Opportunity | 🟡 Follow-up

[1-8] Ver detalhes | [f] Filtrar | [s] Ordenar | [r] Refresh
```

## Hot Leads

```
/wa-leads hot

🔥 HOT LEADS (Score >= 80)
════════════════════════════════════════

Total: 8 leads prontos para fechar!

1. Maria Santos (92 pts) ⏱️ 3min
   📱 5511999999999
   💬 "Quanto custa o servico de consultoria?"
   🎯 Intencao: COMPRA
   💰 Valor estimado: R$ 15.000
   [Responder] [Ver historico] [Marcar como respondido]

2. Joao Silva (87 pts) ⏱️ 8min
   📱 5511888888888
   💬 "Preciso urgente para hoje"
   🎯 Intencao: COMPRA
   💰 Valor estimado: R$ 8.500
   [Responder] [Ver historico] [Marcar como respondido]

3. Pedro Costa (85 pts) ⏱️ 15min ⚠️
   📱 5511777777777
   💬 "Aceita pix? Quero fechar agora"
   🎯 Intencao: COMPRA
   💰 Valor estimado: R$ 12.000
   [Responder] [Ver historico] [Marcar como respondido]

⚠️ 1 hot lead esperando > SLA (5min)
```

## Detalhes do Lead

```
/wa-leads 5511999999999

📋 DETALHES DO LEAD
════════════════════════════════════════

👤 CONTATO
   Nome: Maria Santos
   Telefone: +55 11 99999-9999
   WhatsApp: 5511999999999@s.whatsapp.net

📊 CLASSIFICACAO
   Score: 92 (HOT_LEAD)
   Estagio: OPPORTUNITY
   Intencao: COMPRA
   Confianca: 94%

💰 VALOR
   Estimado: R$ 15.000,00
   Produto: Consultoria Premium

📅 TIMELINE
   Primeiro contato: 15/01/2026 10:23
   Ultima mensagem: 17/01/2026 14:32 (3min atras)
   Tempo no estagio: 2 dias

💬 HISTORICO RECENTE
   [14:32] Maria: Quanto custa o servico de consultoria?
   [14:28] Maria: Vi no Instagram que voces fazem consultoria
   [14:25] Voce: Ola Maria! Bem-vinda!
   [14:23] Maria: Oi, boa tarde!

🔗 INTEGRACOES
   HubSpot: Contato #12345
   Deal: #6789 (R$ 15.000)
   Ultima sync: 5min atras

🎯 ACOES
   [💬 Responder] [📋 Enviar proposta] [📅 Agendar reuniao]
   [✅ Marcar como WON] [❌ Marcar como LOST] [📝 Adicionar nota]
```

## Gestao do Lead

```
/wa-leads 5511999999999 --update-stage proposal

✅ LEAD ATUALIZADO
════════════════════════════════════════

Lead: Maria Santos
Estagio anterior: OPPORTUNITY
Estagio novo: PROPOSAL

📋 Proximos passos:
   - Enviar proposta formal
   - Agendar follow-up em 48h
   - Sincronizar com HubSpot

✅ Deal atualizado no HubSpot
```

## Marcar como Ganho

```
/wa-leads 5511999999999 --won 15000

🎉 VENDA FECHADA!
════════════════════════════════════════

Lead: Maria Santos
Valor: R$ 15.000,00

📊 Metricas da venda:
   Tempo para fechar: 2 dias
   Mensagens trocadas: 23
   Score inicial: 45
   Score final: 92

🔗 Acoes executadas:
   ✅ Estagio atualizado para WON
   ✅ HubSpot deal fechado
   ✅ Cliente criado no sistema
   ✅ Notificacao enviada

💡 Proximos passos sugeridos:
   - Enviar email de boas-vindas
   - Agendar onboarding
   - Solicitar avaliacao
```

## Marcar como Perdido

```
/wa-leads 5511999999999 --lost "preco alto"

❌ OPORTUNIDADE PERDIDA
════════════════════════════════════════

Lead: Pedro Costa
Motivo: Preco alto

📊 Analise:
   Tempo no funil: 5 dias
   Estagio alcancado: PROPOSAL
   Valor perdido: R$ 12.000,00

📋 Aprendizado:
   - Cliente sensivel a preco
   - Considerar oferta mais agressiva

🔄 Reativacao agendada para: 17/02/2026
```

## Filtros e Ordenacao

```
/wa-leads --filter score>=50 --sort waiting desc

📋 LEADS FILTRADOS
════════════════════════════════════════

Filtro: score >= 50
Ordenacao: tempo de espera (desc)

Total: 12 leads

[Lista de leads ordenada por tempo de espera]
```

## Opcoes

```
/wa-leads                          # Lista todos
/wa-leads hot                      # Score >= 80
/wa-leads opportunity              # Score 50-79
/wa-leads pipeline                 # Visao do funil
/wa-leads [numero]                 # Detalhes
/wa-leads [numero] --respond       # Abrir para responder
/wa-leads [numero] --won [valor]   # Marcar como ganho
/wa-leads [numero] --lost [motivo] # Marcar como perdido
/wa-leads --filter [criterio]      # Filtrar
/wa-leads --sort [campo] [asc|desc]# Ordenar
/wa-leads --export                 # Exportar CSV
```
