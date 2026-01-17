# Evolution WhatsApp Business

**SDR Virtual Inteligente para WhatsApp com Evolution API**

Sistema completo de gestao de leads, classificacao de conversas, monitoramento de SLA e automacao de vendas para WhatsApp Business.

## Visao Geral

Este projeto implementa um **SDR (Sales Development Representative) Virtual** que:

- Analisa conversas do WhatsApp em tempo real
- Identifica oportunidades de negocio e hot leads
- Detecta conversas esquecidas (sem resposta > 1h)
- Classifica mensagens (importante vs spam)
- Gerencia pipeline de vendas
- Opera em 3 modos: STEALTH, ACTIVE ou HYBRID

## Instalacao

### Via Claude Code Plugin Marketplace

```bash
# Adicionar marketplace
/plugin marketplace add gutomec/arquitetos-plugins

# Instalar plugin
/plugin install evolution-whatsapp-business@arquitetos-plugins
```

### Manual

```bash
# Clonar repositorio
git clone https://github.com/gutomec/arquitetos-plugins.git

# Copiar para seu projeto Claude Code
cp -r plugins/evolution-whatsapp-business/.claude .claude
cp plugins/evolution-whatsapp-business/.mcp.json .mcp.json

# Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

## Configuracao

### Variaveis de Ambiente

```bash
# Evolution API (obrigatorio)
EVOLUTION_API_URL=https://evolution.seudominio.com
EVOLUTION_API_KEY=sua-chave-api
EVOLUTION_INSTANCE=principal

# PostgreSQL (acesso ao banco da Evolution)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua-senha
POSTGRES_DB=evolution

# Integracoes (opcional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
HUBSPOT_API_KEY=...
STRIPE_SECRET_KEY=...
```

### Primeiro Setup

```bash
/wa-setup
```

## Modos de Operacao

| Modo | Descricao | Comportamento |
|------|-----------|---------------|
| **STEALTH** | Observador silencioso | Analisa, classifica, alerta - NAO responde |
| **ACTIVE** | Assistente ativo | Analisa, classifica, alerta E responde |
| **HYBRID** | Inteligente | Responde apenas hot leads (score >= 80) |

```bash
# Alternar modo
/wa-mode stealth
/wa-mode active
/wa-mode hybrid
```

## Comandos Disponiveis

| Comando | Descricao |
|---------|-----------|
| `/wa-setup` | Configuracao inicial |
| `/wa-mode` | Alternar modos |
| `/wa-dashboard` | Dashboard interativo |
| `/wa-leads` | Listar hot leads |
| `/wa-esquecidos` | Conversas sem resposta |
| `/wa-spam` | Gerenciar spam |
| `/wa-relatorio` | Gerar relatorios |

## Sistema de Classificacao

| Tag | Score | Cor | SLA |
|-----|-------|-----|-----|
| HOT_LEAD | 80-100 | Vermelho | 5 min |
| OPPORTUNITY | 50-79 | Laranja | 30 min |
| FOLLOW_UP | 30-49 | Amarelo | 1 hora |
| INFORMATIVE | 10-29 | Verde | 4 horas |
| SPAM | 0-9 | Preto | Ignorar |

## Arquitetura

```
wa-business-brain (orchestrator)
       |
       +-- wa-inbox-monitor (captura mensagens)
       +-- wa-lead-scorer (pontua leads)
       +-- wa-sla-tracker (monitora tempos)
       +-- wa-spam-detector (filtra spam)
       +-- wa-sentiment-analyzer (analisa sentimento)
       +-- wa-sdr-manager (gerencia pipeline)
       +-- wa-auto-responder (responde - modo active)
```

## Dashboard

O dashboard interativo mostra:

- Metricas principais (mensagens, hot leads, tempo medio, vendas)
- Lista de hot leads para acao imediata
- Conversas esquecidas
- Pipeline de vendas
- Graficos de performance
- Centro de acoes rapidas

Acesse via:

```bash
/wa-dashboard
```

Ou abra `dashboard/index.html` diretamente.

## Integracoes

### Evolution API

- Captura de mensagens via webhook
- Envio de respostas automaticas
- Acesso ao historico de conversas

### HubSpot CRM

- Sincronizacao de contatos
- Criacao automatica de deals
- Atualizacao de estagios

### Google Calendar

- Agendamento de reunioes
- Verificacao de disponibilidade
- Lembretes automaticos

### Stripe

- Cobranca de clientes
- Links de pagamento
- Acompanhamento de transacoes

## Estrutura de Arquivos

```
evolution-whatsapp-business/
├── .claude/
│   ├── agents/           # 8 agentes especializados
│   ├── commands/         # 7 comandos
│   ├── skills/           # 6 skills
│   └── hooks/            # 3 hooks
├── config/
│   ├── operation-mode.yaml
│   ├── sla-thresholds.yaml
│   ├── scoring-weights.yaml
│   └── notification-channels.yaml
├── dashboard/
│   ├── index.html        # Dashboard standalone
│   └── SDRDashboard.tsx  # Componente React
├── .mcp.json             # Configuracao MCPs
├── .env.example          # Template de variaveis
└── CLAUDE.md             # Memoria do projeto
```

## Metricas Monitoradas

- Tempo medio de resposta
- Taxa de resposta em SLA
- Taxa de conversao de leads
- Score medio de leads
- Quantidade de hot leads por dia
- Conversas esquecidas
- Distribuicao de sentimento
- Pipeline de vendas

## Seguranca

- Credenciais via variaveis de ambiente
- Validacao de webhooks
- Modo restricted para queries SQL
- Whitelist/blacklist de contatos
- Deteccao automatica de phishing

## Suporte

- Issues: https://github.com/gutomec/arquitetos-plugins/issues
- Documentacao: CLAUDE.md

## Licenca

MIT License

---

*Desenvolvido por Arquitetos de Prompt*
*Versao 1.0.0 | Janeiro 2026*
