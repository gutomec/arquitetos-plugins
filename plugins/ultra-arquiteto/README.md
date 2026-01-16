# Ultra Arquiteto

Plugin especialista em criacao de plugins para Claude Code e Claude Agent SDK.

## Descricao

O Ultra Arquiteto e um sistema multi-agente que gera plugins completos para:
- **Claude Code**: Agents, Skills, Commands, Hooks
- **Claude Agent SDK**: Python e TypeScript implementations

## Arquitetura

```
Ultra Arquiteto (Orquestrador)
    ├── Arquiteto de Agentes
    ├── Arquiteto de Skills
    ├── Arquiteto de Workflows
    ├── Arquiteto de Tools
    └── Arquiteto de Commands
```

## Agentes

| Agente | Descricao |
|--------|-----------|
| `ultra-arquiteto` | Orquestrador principal |
| `arquiteto-agentes` | Cria subagents com personas e guardrails |
| `arquiteto-skills` | Cria skills com progressive disclosure |
| `arquiteto-workflows` | Cria workflows de orquestracao |
| `arquiteto-tools` | Cria custom tools e MCP servers |
| `arquiteto-commands` | Cria slash commands |

## Instalacao

### Claude Code

```bash
# Copiar para .claude/
cp -r agents/* ~/.claude/agents/
cp -r skills/* ~/.claude/skills/
cp -r commands/* ~/.claude/commands/
```

### Agent SDK (Python)

```bash
cd agent-sdk/python
pip install -r requirements.txt
python main.py serve
```

### Agent SDK (TypeScript)

```bash
cd agent-sdk/typescript
npm install
npm run build
npm start
```

## Uso

### Slash Command

```
/criar-plugin sistema de automacao de testes com Jest e Playwright
```

### Agent SDK

```python
from main import generate_plugin

result = await generate_plugin({
    "plugin_name": "test-automation",
    "description": "Sistema de automacao de testes",
    "components": {
        "agents": [
            {
                "name": "test-runner",
                "description": "Executa testes automatizados",
                "persona": "Especialista em QA e testing",
                "tools": ["Bash", "Read", "Write"],
            }
        ],
        "skills": [
            {
                "name": "test-automation",
                "triggers": ["run tests", "execute test suite"],
                "phases": [
                    {"name": "setup", "description": "Configurar ambiente"},
                    {"name": "execute", "description": "Executar testes"},
                    {"name": "report", "description": "Gerar relatorio"},
                ]
            }
        ],
    }
})
```

## Output

O plugin gera dois outputs simultaneos:

### Claude Code
```
.claude/
├── agents/*.md
├── skills/*/SKILL.md
├── commands/*.md
└── hooks/*.sh
```

### Agent SDK
```
agent-sdk/
├── python/
│   ├── agents/*.py
│   ├── skills/*.py
│   ├── workflows/*.py
│   ├── tools/*.py
│   └── main.py
└── typescript/
    ├── agents/*.ts
    ├── skills/*.ts
    ├── workflows/*.ts
    ├── tools/*.ts
    └── index.ts
```

## Metodologia BMAD

O Ultra Arquiteto segue a metodologia BMAD para criacao de plugins:

1. **Analise**: Compreender requisitos do usuario
2. **Pesquisa**: Investigar dominio e best practices
3. **Discussao**: Debate entre agentes BMAD
4. **Geracao**: Criacao paralela por 5 arquitetos
5. **Output**: Plugins Claude Code + Agent SDK

## Licenca

MIT
