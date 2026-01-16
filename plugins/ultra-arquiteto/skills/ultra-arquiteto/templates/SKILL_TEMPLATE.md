## Template de Skill

### Estrutura de Diretorio

```
skill-name/
├── SKILL.md           # Obrigatorio - instrucoes principais
├── ADVANCED.md        # Opcional - funcionalidades avancadas
├── REFERENCE.md       # Opcional - documentacao de referencia
├── scripts/
│   └── helper.py      # Opcional - scripts auxiliares
└── templates/
    └── output.md      # Opcional - templates de saida
```

### SKILL.md Template

```yaml
---
name: {{skill-name}}
description: {{Descricao do skill e QUANDO usar (max 1024 chars). Deve explicar O QUE faz e em quais situacoes deve ser ativado.}}
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# {{Skill Title}}

## Quick Start

{{Instrucoes minimas para comecar a usar o skill em 3-5 passos}}

### Passo 1
{{Instrucao}}

### Passo 2
{{Instrucao}}

## Detailed Usage

### {{Funcionalidade 1}}

{{Descricao detalhada}}

```{{language}}
{{exemplo_de_codigo}}
```

### {{Funcionalidade 2}}

{{Descricao detalhada}}

## Advanced Features

Para funcionalidades avancadas, consulte [ADVANCED.md](ADVANCED.md).

## Security Considerations

### Permissoes Necessarias
{{Lista de permissoes que o skill precisa}}

### Dados Sensiveis
{{Como o skill trata dados sensiveis}}

### Restricoes
{{O que o skill NAO deve fazer}}

## Examples

### Example 1: {{Caso de Uso Simples}}

```
{{Input do usuario}}
```

Resultado:
```
{{Output esperado}}
```

### Example 2: {{Caso de Uso Avancado}}

```
{{Input do usuario}}
```

Resultado:
```
{{Output esperado}}
```

## Troubleshooting

### Problema: {{Erro Comum 1}}
Solucao: {{Como resolver}}

### Problema: {{Erro Comum 2}}
Solucao: {{Como resolver}}
```

### ADVANCED.md Template

```markdown
# {{Skill Name}} - Advanced Features

## {{Feature Avancada 1}}

{{Descricao detalhada com exemplos}}

## {{Feature Avancada 2}}

{{Descricao detalhada com exemplos}}

## Integration

### Com Outros Skills
{{Como integrar com outros skills}}

### Com Agentes
{{Como usar com agentes especificos}}

## Configuration

### Opcoes Avancadas
{{Configuracoes adicionais}}
```

### Checklist de Validacao

- [ ] Nome em kebab-case
- [ ] Descricao < 1024 caracteres
- [ ] Descricao explica QUANDO usar
- [ ] allowed-tools sao minimamente necessarios
- [ ] Quick Start permite uso imediato
- [ ] Detailed Usage e passo-a-passo
- [ ] Security Considerations presente
- [ ] Examples sao praticos e testados
- [ ] Progressive disclosure aplicado
