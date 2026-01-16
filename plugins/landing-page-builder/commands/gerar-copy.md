---
description: Gera apenas o copywriting de uma landing page sem criar o projeto completo
---

# /gerar-copy

## Objetivo

Gera textos de alta conversao para uma landing page usando os frameworks dos maiores copywriters.

## Uso

```
/gerar-copy $ARGUMENTS
```

## Exemplos

```
/gerar-copy produto: app de meditacao, publico: profissionais estressados
/gerar-copy servico de consultoria financeira para autonomos
```

## Instrucoes

1. Analise o `$ARGUMENTS` para extrair:
   - Produto/servico
   - Publico-alvo (se informado)
   - Tom de voz (se informado)

2. Se faltarem informacoes, pergunte:
   - Qual o principal problema que resolve?
   - Quem e o publico ideal?
   - Que tom usar (formal/casual/tecnico)?

3. Convoque o agente `copywriter-supreme`

4. Gere copy para todas as secoes:
   - Hero (headline, subheadline, CTA)
   - Problema (usando PAS)
   - Solucao
   - Beneficios (3-5 itens)
   - Depoimentos (templates)
   - FAQ (5 perguntas)
   - CTA Final

5. Entregue em formato Markdown estruturado

## Output Esperado

```markdown
## COPY - [Nome do Produto]

### Hero Section
**Headline:** [headline poderosa]
**Subheadline:** [expansao da promessa]
**CTA:** [texto do botao]

### Problema
[Copy usando framework PAS]

### Solucao
[Apresentacao da solucao]

### Beneficios
- [Beneficio 1]
- [Beneficio 2]
- [Beneficio 3]

### Depoimentos
[Templates para 3 depoimentos]

### FAQ
1. [Pergunta]
   [Resposta]
...

### CTA Final
[Fechamento urgente]
```
