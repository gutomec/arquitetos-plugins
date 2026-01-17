---
name: spam-detection
description: Detecta e filtra mensagens de spam e ruido
---

# Spam Detection

Filtra automaticamente mensagens indesejadas para manter o foco em conversas comerciais relevantes.

## Uso

```
Esta mensagem e spam?
Analise o contato 5511999999999 para spam
Liste os spams detectados hoje
```

## Categorias de Spam

### 1. Spam Comercial

```yaml
patterns:
  - "renda extra"
  - "ganhe dinheiro"
  - "trabalhe de casa"
  - "marketing multinivel"
  - "bitcoin", "cripto"
score: +30
```

### 2. Phishing

```yaml
patterns:
  - "atualize seus dados"
  - "conta bloqueada"
  - "clique aqui para verificar"
  - "comprovante pix"
score: +50
action: BLOCK
```

### 3. Correntes

```yaml
patterns:
  - "repasse para 10 amigos"
  - "se nao repassar"
  - "urgente!!!"
  - "video vazado"
score: +25
```

### 4. Bots

```yaml
indicators:
  - mensagens identicas repetidas
  - horarios regulares
  - convites de grupo
score: +35
```

### 5. Ruido

```yaml
indicators:
  - apenas emojis
  - "ok", "sim" isolados
  - stickers sem contexto
  - reacoes
score: +10
```

## Algoritmo

```python
def detect_spam(message):
    spam_score = 0

    # Verificar padroes
    for pattern in SPAM_PATTERNS:
        if pattern in message.lower():
            spam_score += pattern.weight

    # Verificar links suspeitos
    if has_suspicious_links(message):
        spam_score += 40

    # Verificar repeticao
    if is_repeated(message):
        spam_score += 35

    # Ajustar por contexto
    if has_previous_conversation:
        spam_score -= 20

    return {
        "is_spam": spam_score >= 50,
        "score": spam_score
    }
```

## Links Suspeitos

Detectar automaticamente:

- URLs encurtadas (bit.ly, short.link)
- Dominios estranhos
- Muitos numeros na URL
- Palavras suspeitas (login, verify)

## Whitelist

Nunca marcar como spam:

- Clientes anteriores
- Contatos com 5+ conversas
- Contatos que receberam resposta
- Contatos salvos

## Blacklist

Bloquear automaticamente:

- Numeros com 3+ tentativas de phishing
- Numeros na lista de spam global
- Numeros reportados pelo usuario

## Acoes

| Categoria | Acao | Notificar |
|-----------|------|-----------|
| Phishing | Bloquear | Sim, urgente |
| Spam Comercial | Ignorar | Nao |
| Corrente | Ignorar | Nao |
| Bot | Monitorar | Log |

## Output

```json
{
  "remote_jid": "5511999999999@s.whatsapp.net",
  "is_spam": true,
  "spam_score": 75,
  "category": "PHISHING",
  "reasons": [
    "phishing: atualize seus dados",
    "link_suspeito: bit.ly/xyz",
    "primeiro_contato_com_link"
  ],
  "action": "BLOCK",
  "confidence": 0.95
}
```

## Relatorio

```
🛡️ SPAM DETECTADO - Hoje
════════════════════════

📊 RESUMO
   Mensagens analisadas: 147
   Spam detectado: 23 (15.6%)

🚫 POR CATEGORIA
   Phishing: 5 (BLOQUEADOS)
   Comercial: 12
   Correntes: 4
   Bots: 2

⚠️ ALERTAS
   3 tentativas de phishing do mesmo numero
```

## Configuracao

Adicione padroes customizados em `config/spam-patterns.yaml`
