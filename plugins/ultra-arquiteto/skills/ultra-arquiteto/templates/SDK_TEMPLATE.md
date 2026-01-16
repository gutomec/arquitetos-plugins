## Template de Plugin para Claude Agent SDK

### Estrutura Python

```
plugin-name-sdk/
├── python/
│   ├── __init__.py
│   ├── agents.py
│   ├── tools.py
│   ├── hooks.py
│   ├── config.py
│   └── main.py
├── requirements.txt
└── README.md
```

### __init__.py

```python
"""{{Plugin Name}} - {{Brief Description}}"""

from .agents import AGENTS
from .tools import TOOLS
from .hooks import HOOKS
from .main import run_plugin

__version__ = "1.0.0"
__all__ = ["AGENTS", "TOOLS", "HOOKS", "run_plugin"]
```

### agents.py

```python
"""Agent definitions for {{Plugin Name}}"""

from claude_agent_sdk import AgentDefinition

AGENTS = {
    "{{agent-1-name}}": AgentDefinition(
        description="{{When to use agent 1}}",
        prompt="""{{System prompt for agent 1}}""",
        tools=["Read", "Glob", "Grep"]
    ),

    "{{agent-2-name}}": AgentDefinition(
        description="{{When to use agent 2}}",
        prompt="""{{System prompt for agent 2}}""",
        tools=["Read", "Write", "Edit"]
    )
}
```

### tools.py

```python
"""Custom tools for {{Plugin Name}}"""

from typing import Any, Dict

async def {{tool_name}}({{parameters}}) -> Dict[str, Any]:
    """{{Tool description}}

    Args:
        {{param}}: {{param description}}

    Returns:
        Dict with result
    """
    # Validate inputs
    if not {{validation}}:
        raise ValueError("{{error_message}}")

    # Execute logic
    result = {{implementation}}

    return {"result": result}


TOOLS = {
    "{{tool_name}}": {{tool_name}}
}
```

### hooks.py

```python
"""Hook definitions for {{Plugin Name}}"""

from claude_agent_sdk import HookMatcher
from typing import Any, Dict

async def pre_tool_validator(input_data: Dict, tool_use_id: str, context: Any) -> Dict:
    """Validate tool usage before execution"""
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Security validations
    if tool_name == "Bash":
        command = tool_input.get('command', '')
        blocked = ["rm -rf", "sudo", "chmod 777"]
        for pattern in blocked:
            if pattern in command:
                return {"block": True, "message": f"Comando bloqueado: {pattern}"}

    return {}


async def post_tool_logger(input_data: Dict, tool_use_id: str, context: Any) -> Dict:
    """Log tool usage after execution"""
    tool_name = input_data.get('tool_name', '')
    # Add logging logic here
    return {}


HOOKS = {
    "PreToolUse": [
        HookMatcher(matcher="Bash|Write|Edit", hooks=[pre_tool_validator])
    ],
    "PostToolUse": [
        HookMatcher(matcher=".*", hooks=[post_tool_logger])
    ]
}
```

### config.py

```python
"""Configuration for {{Plugin Name}}"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PluginConfig:
    """Plugin configuration"""
    name: str = "{{plugin-name}}"
    version: str = "1.0.0"
    allowed_tools: List[str] = None
    permission_mode: str = "acceptEdits"
    sandbox_enabled: bool = True

    def __post_init__(self):
        if self.allowed_tools is None:
            self.allowed_tools = [
                "Read", "Write", "Edit", "Bash",
                "Glob", "Grep", "Task"
            ]


DEFAULT_CONFIG = PluginConfig()
```

### main.py

```python
"""Main entry point for {{Plugin Name}}"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

from .agents import AGENTS
from .tools import TOOLS
from .hooks import HOOKS
from .config import DEFAULT_CONFIG


async def run_plugin(prompt: str, config: PluginConfig = None):
    """Execute the plugin with given prompt

    Args:
        prompt: User's task description
        config: Optional configuration override
    """
    if config is None:
        config = DEFAULT_CONFIG

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=config.allowed_tools,
            agents=AGENTS,
            hooks=HOOKS,
            permission_mode=config.permission_mode
        )
    ):
        if hasattr(message, "result"):
            print(message.result)
        yield message


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m {{plugin_name}} 'your prompt here'")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    asyncio.run(run_plugin(prompt))
```

### requirements.txt

```
claude-agent-sdk>=1.0.0
```

---

### Estrutura TypeScript

```
plugin-name-sdk/
├── typescript/
│   ├── src/
│   │   ├── agents.ts
│   │   ├── tools.ts
│   │   ├── hooks.ts
│   │   ├── config.ts
│   │   └── index.ts
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

### agents.ts

```typescript
import { AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

export const agents: Record<string, AgentDefinition> = {
  "{{agent-1-name}}": {
    description: "{{When to use agent 1}}",
    prompt: `{{System prompt for agent 1}}`,
    tools: ["Read", "Glob", "Grep"]
  },

  "{{agent-2-name}}": {
    description: "{{When to use agent 2}}",
    prompt: `{{System prompt for agent 2}}`,
    tools: ["Read", "Write", "Edit"]
  }
};
```

### hooks.ts

```typescript
import { HookCallback } from "@anthropic-ai/claude-agent-sdk";

export const preToolValidator: HookCallback = async (input) => {
  const toolName = (input as any).tool_name ?? "";
  const toolInput = (input as any).tool_input ?? {};

  if (toolName === "Bash") {
    const command = toolInput.command ?? "";
    const blocked = ["rm -rf", "sudo", "chmod 777"];

    for (const pattern of blocked) {
      if (command.includes(pattern)) {
        return { block: true, message: `Comando bloqueado: ${pattern}` };
      }
    }
  }

  return {};
};

export const hooks = {
  PreToolUse: [
    { matcher: "Bash|Write|Edit", hooks: [preToolValidator] }
  ]
};
```

### index.ts

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { agents } from "./agents";
import { hooks } from "./hooks";

export async function* runPlugin(prompt: string) {
  for await (const message of query({
    prompt,
    options: {
      allowedTools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task"],
      agents,
      hooks,
      permissionMode: "acceptEdits"
    }
  })) {
    if ("result" in message) {
      console.log(message.result);
    }
    yield message;
  }
}

// CLI entry point
if (require.main === module) {
  const prompt = process.argv.slice(2).join(" ");

  if (!prompt) {
    console.log("Usage: npx {{plugin-name}} 'your prompt here'");
    process.exit(1);
  }

  (async () => {
    for await (const _ of runPlugin(prompt)) {
      // Process messages
    }
  })();
}
```

### package.json

```json
{
  "name": "{{plugin-name}}",
  "version": "1.0.0",
  "description": "{{Plugin description}}",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

### Checklist de Validacao

- [ ] Estrutura de diretorios correta
- [ ] agents.py/ts com AgentDefinition validos
- [ ] hooks.py/ts com validacoes de seguranca
- [ ] main.py/index.ts com entry point funcional
- [ ] requirements.txt/package.json com dependencias
- [ ] README.md com instrucoes de uso
- [ ] Testes basicos implementados
