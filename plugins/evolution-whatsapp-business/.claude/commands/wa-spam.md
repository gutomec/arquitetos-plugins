---
name: wa-spam
description: Gerencia lista de spam e mensagens filtradas
---

# /wa-spam

Gerencia a deteccao de spam, visualiza mensagens filtradas e configura whitelist/blacklist.

## Uso

```
/wa-spam                    # Resumo de spam do dia
/wa-spam list               # Lista spam detectado
/wa-spam whitelist          # Ver/gerenciar whitelist
/wa-spam blacklist          # Ver/gerenciar blacklist
/wa-spam [numero]           # Analisar numero especifico
/wa-spam report             # Relatorio completo
```

## Resumo de Spam

```
/wa-spam

🛡️ PROTECAO ANTI-SPAM
════════════════════════════════════════

📊 HOJE (17/01/2026)
   Mensagens analisadas: 147
   Spam detectado: 23 (15.6%)
   Phishing bloqueado: 5 ⚠️
   Falsos positivos: 2

🚫 POR CATEGORIA
   ┌────────────────────────────────────┐
   │ Phishing       │ 5  │ ██████████  │ BLOQUEADO
   │ Comercial      │ 12 │ ████████████│
   │ Correntes      │ 4  │ ████        │
   │ Bots           │ 2  │ ██          │
   └────────────────────────────────────┘

⚠️ ALERTAS
   3 tentativas de phishing do mesmo numero
   Numero: 5511666666666
   Acao: Bloqueio automatico aplicado

✅ WHITELIST
   5 contatos adicionados automaticamente
   (Clientes que responderam)

🎯 ACOES
   [Ver detalhes] [Configurar filtros] [Exportar log]
```

## Lista de Spam

```
/wa-spam list

🚫 SPAM DETECTADO HOJE
════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│ #  │ Numero         │ Categoria  │ Score │ Preview               │ Acao│
├─────────────────────────────────────────────────────────────────────────┤
│ 1  │ 5511666666666  │ PHISHING   │  95   │ "Atualize seus dad... │ 🔒  │
│ 2  │ 5511555555555  │ PHISHING   │  92   │ "Sua conta sera bl... │ 🔒  │
│ 3  │ 5511444444444  │ COMERCIAL  │  75   │ "Ganhe R$5000 trab... │ ⛔  │
│ 4  │ 5511333333333  │ COMERCIAL  │  70   │ "Promocao imperdiv... │ ⛔  │
│ 5  │ 5511222222222  │ CORRENTE   │  65   │ "Repasse para 10 a... │ ⛔  │
│ 6  │ 5511111111111  │ BOT        │  60   │ "Link do grupo: ht... │ ⛔  │
└─────────────────────────────────────────────────────────────────────────┘

Legenda: 🔒 Bloqueado | ⛔ Ignorado | ⚠️ Suspeito

[1-6] Ver detalhes | [w] Adicionar whitelist | [b] Bloquear
```

## Detalhes do Spam

```
/wa-spam 5511666666666

🔍 ANALISE DE SPAM
════════════════════════════════════════

📱 NUMERO: 5511666666666
   Status: 🔒 BLOQUEADO
   Categoria: PHISHING
   Score: 95/100

💬 MENSAGEM ORIGINAL
   "URGENTE! Sua conta sera bloqueada em 24h.
   Atualize seus dados agora: bit.ly/xyz123
   Evite perder acesso ao seu WhatsApp!"

🚨 INDICADORES DETECTADOS
   ✗ Palavra-chave phishing: "conta bloqueada" (+50)
   ✗ Link encurtado suspeito: bit.ly (+40)
   ✗ Urgencia artificial: "URGENTE" (+15)
   ✗ Primeiro contato com link (+20)
   ─────────────────────────────────────
   Total: 125 (cap 100)

📊 HISTORICO DO NUMERO
   Primeira vez: 15/01/2026
   Total de tentativas: 3
   Todas bloqueadas: Sim

🎯 ACOES
   [🔓 Desbloquear] [✅ Marcar como falso positivo]
   [📋 Ver todas mensagens] [🚫 Reportar para blacklist global]
```

## Whitelist

```
/wa-spam whitelist

✅ WHITELIST
════════════════════════════════════════

Contatos que NUNCA sao marcados como spam:

┌─────────────────────────────────────────────────────────────────────────┐
│ #  │ Numero         │ Nome           │ Motivo              │ Desde    │
├─────────────────────────────────────────────────────────────────────────┤
│ 1  │ 5511999999999  │ Maria Santos   │ Cliente recorrente  │ 10/01/26 │
│ 2  │ 5511888888888  │ Joao Silva     │ Resposta enviada    │ 12/01/26 │
│ 3  │ 5511777777777  │ Pedro Costa    │ 5+ conversas        │ 08/01/26 │
│ 4  │ 5511666666666  │ Ana Oliveira   │ Manual              │ 15/01/26 │
│ 5  │ 5511555555555  │ Carlos Dias    │ Contato salvo       │ 05/01/26 │
└─────────────────────────────────────────────────────────────────────────┘

Total: 234 contatos na whitelist

🎯 ACOES
   [+ Adicionar] [- Remover] [🔄 Sincronizar com contatos]
```

## Blacklist

```
/wa-spam blacklist

🚫 BLACKLIST
════════════════════════════════════════

Contatos PERMANENTEMENTE bloqueados:

┌─────────────────────────────────────────────────────────────────────────┐
│ #  │ Numero         │ Motivo                    │ Tentativas │ Desde   │
├─────────────────────────────────────────────────────────────────────────┤
│ 1  │ 5511666666666  │ Phishing (3x)             │ 3          │ 15/01/26│
│ 2  │ 5511555555555  │ Phishing (2x)             │ 2          │ 14/01/26│
│ 3  │ 5511444444444  │ Spam comercial persistente│ 8          │ 10/01/26│
│ 4  │ 5511333333333  │ Bot automatizado          │ 15         │ 05/01/26│
└─────────────────────────────────────────────────────────────────────────┘

Total: 47 numeros bloqueados

⚠️ BLOQUEIO AUTOMATICO
   Ativado apos: 3 tentativas de phishing
   Ou: 5 mensagens de spam comercial

🎯 ACOES
   [- Remover da blacklist] [📋 Exportar lista]
```

## Adicionar a Whitelist

```
/wa-spam whitelist add 5511999999999

✅ ADICIONADO A WHITELIST
════════════════════════════════════════

Numero: 5511999999999
Nome: Maria Santos (se disponivel)
Motivo: Adicionado manualmente

A partir de agora, mensagens deste numero
NAO serao filtradas como spam.
```

## Bloquear Numero

```
/wa-spam block 5511666666666

🚫 NUMERO BLOQUEADO
════════════════════════════════════════

Numero: 5511666666666
Motivo: Bloqueio manual

Acoes aplicadas:
   ✅ Adicionado a blacklist
   ✅ Mensagens futuras ignoradas
   ✅ Historico mantido para analise
```

## Falso Positivo

```
/wa-spam 5511999999999 --false-positive

🔄 MARCADO COMO FALSO POSITIVO
════════════════════════════════════════

Numero: 5511999999999
Mensagem original restaurada

Acoes aplicadas:
   ✅ Removido da lista de spam
   ✅ Adicionado a whitelist
   ✅ Modelo de deteccao atualizado

💡 Obrigado pelo feedback!
   Isso ajuda a melhorar a deteccao.
```

## Configuracao

```
/wa-spam config

⚙️ CONFIGURACAO DE SPAM
════════════════════════════════════════

Sensibilidade: [MEDIA] _
   Alta: Mais falsos positivos, menos spam passa
   Media: Equilibrado
   Baixa: Menos falsos positivos, mais spam passa

Auto-bloqueio phishing: [✓] _
   Bloquear automaticamente apos 3 tentativas

Auto-whitelist clientes: [✓] _
   Adicionar automaticamente quem ja comprou

Notificar phishing: [✓] _
   Alertar imediatamente sobre tentativas

[Salvar configuracoes]
```
