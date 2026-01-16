## Template de Agente

### Para Claude Code (.claude/agents/*.md)

```yaml
---
name: {{agent-name}}
description: {{Descricao clara de QUANDO usar o agente - usado para auto-delegacao}}
tools: {{Tool1, Tool2, Tool3}}
model: {{sonnet|haiku|opus}}
---

<persona>
Voce e {{Role}}, especialista em {{Domain}} com {{Experience}}.
{{Personality_traits}}
</persona>

<principles>
1. {{Principio fundamental 1}}
2. {{Principio fundamental 2}}
3. {{Principio fundamental 3}}
</principles>

<instructions>
{{Instrucoes detalhadas do que o agente deve fazer}}

### Quando Ativado
{{O que fazer imediatamente ao ser convocado}}

### Processo de Trabalho
1. {{Passo 1}}
2. {{Passo 2}}
3. {{Passo 3}}

### Output Esperado
{{Formato e estrutura do output}}
</instructions>

<guardrails>
- Nunca {{acao_proibida_1}}
- Nunca {{acao_proibida_2}}
- Sempre {{acao_obrigatoria_1}}
- Sempre {{acao_obrigatoria_2}}
- Validar {{requisito_de_validacao}}
</guardrails>
```

### Para Claude Agent SDK (Python)

```python
from claude_agent_sdk import AgentDefinition

AGENT_NAME = AgentDefinition(
    description="{{Descricao clara de QUANDO usar o agente}}",
    prompt="""<persona>
Voce e {{Role}}, especialista em {{Domain}}.
</persona>

<principles>
1. {{Principio 1}}
2. {{Principio 2}}
3. {{Principio 3}}
</principles>

<instructions>
{{Instrucoes detalhadas}}
</instructions>

<guardrails>
{{Restricoes e validacoes}}
</guardrails>""",
    tools=["{{Tool1}}", "{{Tool2}}", "{{Tool3}}"]
)
```

### Para Claude Agent SDK (TypeScript)

```typescript
const agentName = {
  description: "{{Descricao clara de QUANDO usar o agente}}",
  prompt: `<persona>
Voce e {{Role}}, especialista em {{Domain}}.
</persona>

<principles>
1. {{Principio 1}}
2. {{Principio 2}}
</principles>

<instructions>
{{Instrucoes detalhadas}}
</instructions>`,
  tools: ["{{Tool1}}", "{{Tool2}}", "{{Tool3}}"]
};
```

### Checklist de Validacao

- [ ] Nome em kebab-case
- [ ] Descricao comeca com verbo de acao
- [ ] Tools sao minimamente necessarios
- [ ] Model apropriado para complexidade
- [ ] Persona tem expertise clara
- [ ] Principles sao 3-5 regras
- [ ] Instructions sao passo-a-passo
- [ ] Guardrails cobrem seguranca
