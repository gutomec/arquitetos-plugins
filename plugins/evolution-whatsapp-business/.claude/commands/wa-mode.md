---
name: wa-mode
description: Alternar entre modos de operacao (stealth/active/hybrid)
---

# /wa-mode

Alterna o modo de operacao do sistema entre STEALTH, ACTIVE e HYBRID.

## Uso

```
/wa-mode              # Mostra modo atual
/wa-mode stealth      # Ativa modo stealth
/wa-mode active       # Ativa modo active
/wa-mode hybrid       # Ativa modo hybrid
```

## Modos

### STEALTH (Observador Silencioso)

```
🔇 MODO STEALTH
════════════════════════════════════════

O sistema APENAS observa. NUNCA responde.

✅ Ativo:
   • Captura todas as mensagens
   • Classifica conversas
   • Pontua leads (0-100)
   • Monitora SLAs
   • Detecta spam
   • Gera alertas no dashboard
   • Envia relatorios diarios

❌ Desativado:
   • Respostas automaticas
   • Follow-ups automaticos
   • Mensagens de ausencia

💡 Ideal para:
   • Conhecer seu fluxo de mensagens
   • Validar classificacoes
   • Fase inicial do sistema
```

### ACTIVE (Assistente Ativo)

```
📢 MODO ACTIVE
════════════════════════════════════════

O sistema observa E responde automaticamente.

✅ Ativo:
   • Tudo do modo STEALTH
   • Respostas automaticas personalizadas
   • Mensagens de ausencia fora do horario
   • Follow-ups programados
   • Agendamento via Google Calendar

⚠️ Limites:
   • Max 3 respostas por conversa
   • Apenas em horario comercial
   • Delay humanizado (5-30s)
   • Nunca responde em grupos

💡 Ideal para:
   • Alto volume de mensagens
   • Respostas padronizadas
   • Disponibilidade 24/7 aparente
```

### HYBRID (Inteligente)

```
🎯 MODO HYBRID
════════════════════════════════════════

O sistema responde APENAS Hot Leads (score >= 80).

✅ Ativo:
   • Tudo do modo STEALTH para todos
   • Respostas automaticas SO para hot leads
   • Priorizacao inteligente

⚙️ Configuravel:
   • Threshold de score (padrao: 80)
   • Tipos de intencao respondidos
   • Horarios de resposta

💡 Ideal para:
   • Equilibrio entre automacao e controle
   • Foco em oportunidades reais
   • Transicao de stealth para active
```

## Mudanca de Modo

```
/wa-mode active

🔄 ALTERANDO MODO
════════════════════════════════════════

Modo anterior: STEALTH
Modo novo: ACTIVE

⚠️ ATENCAO: Em modo ACTIVE o sistema
   ira responder mensagens automaticamente.

Confirma a mudanca? [s/n]: s

✅ Modo alterado para ACTIVE

📋 Configuracoes aplicadas:
   • Horario: 08:00 - 18:00
   • Dias: Seg a Sex
   • Max respostas: 3 por conversa
   • Delay: 5-30 segundos

💡 Use /wa-mode stealth para desativar
```

## Status Detalhado

```
/wa-mode

📊 STATUS DO MODO
════════════════════════════════════════

Modo atual: HYBRID

⏰ Horario comercial: 08:00 - 18:00
   Status agora: ✅ DENTRO DO HORARIO

📈 Threshold hot lead: 80
   Hot leads ativos: 5

📊 Estatisticas (ultimas 24h):
   • Respostas automaticas: 23
   • Escaladas para humano: 8
   • Taxa de resposta: 74%

🔧 Configuracoes:
   • Delay min: 5s
   • Delay max: 30s
   • Max por conversa: 3
   • Grupos: DESATIVADO
```

## Modo Temporario

```
/wa-mode stealth --temp 2h

⏰ MODO TEMPORARIO
════════════════════════════════════════

Modo: STEALTH
Duracao: 2 horas
Retorna para: ACTIVE as 16:30

Motivo sugerido:
• Reuniao importante
• Manutencao do sistema
• Periodo de observacao

✅ Modo temporario ativado
```

## Configuracao do Modo

```
/wa-mode hybrid --config

⚙️ CONFIGURAR MODO HYBRID
════════════════════════════════════════

Threshold de score: [80] _
Responder intencoes:
  [x] COMPRA
  [x] AGENDAMENTO
  [ ] INFORMACAO
  [ ] SUPORTE

Horario de resposta:
  Inicio: [08:00] _
  Fim: [18:00] _

Dias ativos:
  [x] Segunda
  [x] Terca
  [x] Quarta
  [x] Quinta
  [x] Sexta
  [ ] Sabado
  [ ] Domingo

✅ Configuracao salva
```

## Arquivo de Configuracao

O modo e salvo em `config/operation-mode.yaml`:

```yaml
mode: hybrid

stealth:
  analyze: true
  classify: true
  alert: true
  respond: false

active:
  respond: true
  auto_followup: true
  response_delay_seconds: 5
  max_auto_responses: 3

hybrid:
  respond_hot_leads_only: true
  hot_lead_threshold: 80
  intents:
    - COMPRA
    - AGENDAMENTO
```
