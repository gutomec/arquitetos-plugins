---
description: Cria um plugin completo para Claude Code e Claude Agent SDK usando o Ultra Arquiteto
---

# /criar-plugin

## Objetivo

Este comando invoca o Ultra Arquiteto de Plugins para criar um plugin completo baseado na solicitacao do usuario. O sistema executa:

1. Pesquisa web sobre o dominio
2. Discussao BMAD multi-agente
3. Geracao paralela por 5 arquitetos
4. Output dual (Claude Code + Agent SDK)

## Uso

```
/criar-plugin $ARGUMENTS
```

Onde `$ARGUMENTS` e a descricao do plugin desejado.

## Exemplos

```
/criar-plugin sistema de automacao de testes com Jest e Playwright
/criar-plugin gerenciamento de projetos agile com sprints e retrospectivas
/criar-plugin integracao com APIs de pagamento Stripe e PayPal
```

## Instrucoes de Execucao

Ao receber este comando:

### Fase 1: Analise

1. Parse a solicitacao em `$ARGUMENTS`
2. Identifique a intencao principal
3. Extraia requisitos explicitos e implicitos
4. Determine o dominio de conhecimento
5. Gere palavras-chave para pesquisa

### Fase 2: Pesquisa

1. Execute pesquisas web:
   - "{dominio} best practices 2025"
   - "{dominio} experts methodology"
   - "Claude Code {dominio} integration"
   - "Claude Agent SDK {dominio} tools"

2. Compile conhecimento sobre:
   - Especialistas do setor
   - Metodologias reconhecidas
   - Best practices atuais
   - Integracoes existentes com Claude

### Fase 3: Discussao BMAD

1. Convoque os agentes BMAD para Party Mode:
   - Architect (Winston): Arquitetura tecnica
   - Analyst (Mary): Requisitos e gaps
   - Developer (Amelia): Viabilidade tecnica
   - Agent Builder (Bond): Estrutura de agentes

2. Conduza discussao sobre:
   - Arquitetura ideal
   - Componentes necessarios
   - Abordagens alternativas
   - Riscos e mitigacoes

3. Documente o consenso

### Fase 4: Geracao Paralela

Execute os 5 arquitetos especializados:

1. **arquiteto-agentes**: Criar subagents com personas
2. **arquiteto-skills**: Criar skills com progressive disclosure
3. **arquiteto-workflows**: Criar fluxos de orquestracao
4. **arquiteto-tools**: Criar MCP servers e hooks
5. **arquiteto-commands**: Criar slash commands

### Fase 5: Output

1. Gere estrutura completa para Claude Code:
   ```
   .claude/
   ├── agents/*.md
   ├── skills/*/SKILL.md
   ├── commands/*.md
   └── hooks/*.sh
   ```

2. Gere estrutura completa para Claude Agent SDK:
   ```
   python/
   ├── agents.py
   ├── tools.py
   ├── hooks.py
   └── main.py

   typescript/
   ├── agents.ts
   ├── tools.ts
   └── index.ts
   ```

3. Crie README.md com documentacao completa

4. Aplique validacoes de seguranca

## Output Esperado

Ao final, o usuario deve receber:

1. Todos os arquivos do plugin Claude Code criados
2. Todos os arquivos do plugin Agent SDK criados
3. Documentacao de uso
4. Instrucoes de instalacao
5. Exemplos de uso

## Validacoes

Antes de entregar:

1. Verificar formato de todos os arquivos
2. Validar YAML frontmatter
3. Confirmar tools sao validos
4. Verificar guardrails de seguranca
5. Testar sintaxe de codigo Python/TypeScript
