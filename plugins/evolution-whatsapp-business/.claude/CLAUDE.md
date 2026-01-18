# Evolution WhatsApp Business

Sistema SDR Virtual Inteligente para gestao de negocios via WhatsApp com Evolution API.

## Visao Geral

Este projeto implementa um **SDR (Sales Development Representative) Virtual** que analisa conversas do WhatsApp em tempo real, identifica oportunidades de negocio, detecta leads quentes, alerta sobre conversas esquecidas e gerencia o pipeline de vendas.

### Modos de Operacao

| Modo | Descricao | Comportamento |
|------|-----------|---------------|
| **STEALTH** | Observador silencioso | Analisa, classifica, alerta - NAO responde |
| **ACTIVE** | Assistente ativo | Analisa, classifica, alerta E responde automaticamente |
| **HYBRID** | Inteligente | Responde apenas hot leads (score > 80) |

### Arquitetura

```
wa-business-brain (orchestrator)
       |
       +-- wa-inbox-monitor (captura mensagens)
       +-- wa-lead-scorer (pontua oportunidades)
       +-- wa-sla-tracker (monitora tempos)
       +-- wa-spam-detector (filtra ruido)
       +-- wa-sentiment-analyzer (entende contexto)
       +-- wa-sdr-manager (gerencia pipeline)
       +-- wa-auto-responder (responde - modo active)
```

## Comandos Disponiveis

| Comando | Descricao |
|---------|-----------|
| `/wa-setup` | Configuracao inicial do sistema |
| `/wa-mode` | Alternar entre stealth/active/hybrid |
| `/wa-dashboard` | Abrir dashboard interativo |
| `/wa-leads` | Listar hot leads ativos |
| `/wa-esquecidos` | Conversas sem resposta >1h |
| `/wa-spam` | Gerenciar lista de spam |
| `/wa-relatorio` | Gerar relatorio diario/semanal |

## Classificacao de Mensagens

O sistema classifica automaticamente cada conversa:

| Tag | Cor | Score | Descricao |
|-----|-----|-------|-----------|
| HOT_LEAD | Vermelho | 80-100 | Oportunidade urgente de venda |
| OPPORTUNITY | Laranja | 50-79 | Potencial de negocio |
| FOLLOW_UP | Amarelo | 30-49 | Requer acompanhamento |
| INFORMATIVE | Verde | 10-29 | Conversa normal |
| SPAM | Preto | 0-9 | Irrelevante/spam |

### Padroes de Deteccao

**HOT_LEAD (responder em <5min):**
- "quanto custa", "qual o preco", "valor"
- "preciso urgente", "para hoje", "agora"
- "como compro", "como faco para adquirir"
- "tem disponivel", "aceita cartao"

**OPPORTUNITY:**
- "me envia orcamento", "pode me passar"
- "estou interessado", "gostaria de saber"
- "voces fazem", "voces tem"

**SPAM:**
- Correntes, memes, figurinhas excessivas
- Links suspeitos, promocoes genericas
- Mensagens de grupos nao-comerciais

## Arquitetura de Bancos de Dados

O sistema utiliza **dois bancos de dados PostgreSQL separados** para melhor organizacao e seguranca:

### evolution-database (READ-ONLY)

Banco de dados gerenciado pela Evolution API. O sistema apenas **consulta** dados aqui.

```
Tabelas consultadas:
├── Message          # Mensagens do WhatsApp
├── Contact          # Contatos
├── Chat             # Conversas
├── MessageUpdate    # Atualizacoes de status
└── ...              # Outras tabelas da Evolution
```

**Uso**: Queries de leitura para historico de mensagens, contatos, timestamps.
**Acesso**: `--access-mode restricted` (somente SELECT)

### system-database (READ-WRITE)

Banco de dados gerenciado pelo sistema SDR Virtual. Aqui ficam todas as tabelas customizadas.

```
Tabelas do sistema:
├── wa_pipeline          # Pipeline de vendas (LEAD -> WON/LOST)
├── wa_score_history     # Historico de scores de leads
├── wa_sla_tracking      # Monitoramento de SLA
├── wa_spam_log          # Log de spam detectado
├── wa_blacklist         # Contatos bloqueados
├── wa_sentiment_log     # Historico de analise de sentimento
├── wa_auto_responses    # Log de respostas automaticas
└── wa_message_tracking  # Tracking de mensagens processadas
```

**Uso**: Leitura e escrita para toda logica de negocio do SDR.
**Acesso**: `--access-mode unrestricted` (SELECT, INSERT, UPDATE, DELETE)

### Mapeamento Agente -> Banco

| Agente | evolution-database | system-database |
|--------|-------------------|-----------------|
| wa-business-brain | READ | READ/WRITE |
| wa-inbox-monitor | READ | WRITE |
| wa-lead-scorer | READ | WRITE |
| wa-sla-tracker | READ | WRITE |
| wa-spam-detector | READ | WRITE |
| wa-sentiment-analyzer | READ | WRITE |
| wa-sdr-manager | READ | WRITE |
| wa-auto-responder | READ | WRITE |

## MCPs Configurados

### Evolution API (Principal)
- `evolution-whatsapp`: Gestao de instancias e mensagens
- `evolution-extended`: Resources read-only (contatos, grupos)
- `evolution-database`: PostgreSQL Evolution (READ-ONLY)
- `system-database`: PostgreSQL Sistema SDR (READ-WRITE)

### Integracao Business (Opcional)
- `google-calendar`: Agendamentos e reunioes
- `gmail`: Envio de emails de follow-up
- `hubspot-crm`: Sincronizacao de leads (opcional)
- `stripe`: Cobrancas e pagamentos (opcional)

### Processamento
- `whisper-transcription`: Transcricao de audios
- `minio-storage`: Armazenamento de arquivos

## Variaveis de Ambiente

```bash
# Evolution API
EVOLUTION_API_URL=https://evolution.seudominio.com
EVOLUTION_API_KEY=sua-chave-api
EVOLUTION_INSTANCE=principal

# PostgreSQL - Evolution API (READ-ONLY)
EVOLUTION_POSTGRES_HOST=localhost
EVOLUTION_POSTGRES_PORT=5432
EVOLUTION_POSTGRES_USER=postgres
EVOLUTION_POSTGRES_PASSWORD=sua-senha
EVOLUTION_POSTGRES_DB=evolution
EVOLUTION_DATABASE_URI=postgresql://user:pass@host:5432/evolution

# PostgreSQL - Sistema SDR (READ-WRITE)
SYSTEM_POSTGRES_HOST=localhost
SYSTEM_POSTGRES_PORT=5432
SYSTEM_POSTGRES_USER=postgres
SYSTEM_POSTGRES_PASSWORD=sua-senha
SYSTEM_POSTGRES_DB=sdr_virtual
SYSTEM_DATABASE_URI=postgresql://user:pass@host:5432/sdr_virtual

# Storage
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Google (opcional)
GOOGLE_CLIENT_ID=seu-client-id
GOOGLE_CLIENT_SECRET=seu-client-secret

# CRM (opcional)
HUBSPOT_API_KEY=seu-hubspot-key

# Payments (opcional)
STRIPE_SECRET_KEY=sk_live_xxx
```

## Thresholds Configuraveis

```yaml
# config/sla-thresholds.yaml
conversation_timeout_minutes: 60  # Alerta apos 1h sem resposta
hot_lead_response_minutes: 5      # Hot leads devem ser respondidos em 5min
follow_up_delay_hours: 24         # Follow-up automatico apos 24h
daily_report_time: "08:00"        # Horario do relatorio diario
```

## Skills Disponiveis

| Skill | Funcao |
|-------|--------|
| conversation-classifier | Classifica mensagens automaticamente |
| lead-scoring | Pontua oportunidades de 0-100 |
| sla-monitor | Monitora tempos de resposta |
| spam-detection | Detecta e filtra spam |
| sentiment-analysis | Analisa tom e intencao |
| daily-digest | Gera relatorios consolidados |

## Hooks Ativos

| Hook | Trigger | Funcao |
|------|---------|--------|
| webhook-processor | UserPromptSubmit | Processa webhooks da Evolution API |
| sla-alert | PostToolUse | Alerta sobre SLA violado |
| daily-report | Scheduled (08:00) | Envia relatorio diario |

## Convencoes de Codigo

- **Linguagem**: Portugues para UI, Ingles para codigo
- **Formato de data**: DD/MM/YYYY HH:mm
- **Moeda**: BRL (R$)
- **Timezone**: America/Sao_Paulo

## Fluxo de Trabalho

1. **Webhook recebido** -> wa-inbox-monitor captura
2. **Mensagem classificada** -> conversation-classifier processa
3. **Score calculado** -> wa-lead-scorer pontua
4. **SLA verificado** -> wa-sla-tracker monitora
5. **Alerta gerado** -> Se necessario, notifica usuario
6. **Resposta enviada** -> Apenas em modo ACTIVE/HYBRID

## Dashboard

O dashboard interativo esta em `dashboard/` e pode ser acessado via `/wa-dashboard`.

### Secoes do Dashboard

1. **Header + Metricas**: KPIs principais do dia
2. **Hot Leads**: Lista de leads quentes para acao imediata
3. **Esquecidos**: Conversas aguardando resposta >1h
4. **Analytics**: Graficos de performance
5. **Action Center**: Acoes rapidas e configuracoes

## Seguranca

- Nunca exponha API keys no codigo
- Use variaveis de ambiente para credenciais
- Valide webhooks com assinatura
- Modo restricted para queries de banco em producao
- Sanitize todos os inputs de usuario

## Performance

- Cache Redis para queries frequentes
- Paginacao em todas as listagens
- Processamento assincrono de midia
- Indices otimizados no PostgreSQL

---

*Projeto criado com Ultra Arquiteto de Plugins*
*Versao: 1.0.0 | Janeiro 2026*
