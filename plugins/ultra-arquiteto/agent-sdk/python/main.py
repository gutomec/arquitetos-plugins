"""
Ultra Arquiteto - Claude Agent SDK Implementation.

Sistema especialista em criacao de plugins para Claude Code e Claude Agent SDK.
Gera sistemas completos de agentes, skills, workflows, tools e commands.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from claude_agent_sdk import create_sdk_mcp_server, tool

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_MODEL = "claude-sonnet-4-20250514"
OUTPUT_DIR = Path("./_output")


# =============================================================================
# TOOLS
# =============================================================================

@tool(
    "create_agent",
    """Cria um agente especializado com persona, principles e guardrails.
    Gera arquivo .md para Claude Code ou .py para Agent SDK.""",
    {
        "name": str,
        "description": str,
        "persona": str,
        "principles": list,
        "tools": list,
        "guardrails": list,
        "output_format": str,  # "claude_code" or "agent_sdk"
    }
)
async def create_agent(args: dict) -> dict:
    """Create a specialized agent."""
    name = args["name"]
    description = args["description"]
    persona = args["persona"]
    principles = args.get("principles", [])
    tools = args.get("tools", ["Read", "Write", "Edit"])
    guardrails = args.get("guardrails", [])
    output_format = args.get("output_format", "claude_code")

    if output_format == "claude_code":
        # Generate Claude Code agent (.md)
        content = f"""---
name: {name}
description: {description}
tools: {', '.join(tools)}
model: sonnet
---

<persona>
{persona}
</persona>

<principles>
{chr(10).join(f'{i+1}. {p}' for i, p in enumerate(principles))}
</principles>

<guardrails>
{chr(10).join(f'- {g}' for g in guardrails)}
</guardrails>
"""
        output_path = OUTPUT_DIR / "claude-code" / "agents" / f"{name}.md"
    else:
        # Generate Agent SDK agent (.py)
        content = f'''"""
Agent: {name}
{description}
"""

from dataclasses import dataclass
from typing import List

@dataclass
class {name.replace("-", "_").title().replace("_", "")}Agent:
    """
    {description}

    Persona: {persona}
    """

    name: str = "{name}"
    description: str = """{description}"""

    persona: str = """{persona}"""

    principles: List[str] = None
    guardrails: List[str] = None
    tools: List[str] = None

    def __post_init__(self):
        self.principles = {principles}
        self.guardrails = {guardrails}
        self.tools = {tools}

    async def execute(self, task: str) -> dict:
        """Execute agent task."""
        # Implementation here
        pass
'''
        output_path = OUTPUT_DIR / "agent-sdk" / "python" / "agents" / f"{name.replace('-', '_')}.py"

    # Save file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "status": "created",
                "agent": name,
                "format": output_format,
                "path": str(output_path),
            }, ensure_ascii=False, indent=2)
        }]
    }


@tool(
    "create_skill",
    """Cria uma skill com progressive disclosure.
    Gera diretorio com SKILL.md ou skills.py.""",
    {
        "name": str,
        "description": str,
        "triggers": list,
        "phases": list,
        "output_format": str,
    }
)
async def create_skill(args: dict) -> dict:
    """Create a skill with progressive disclosure."""
    name = args["name"]
    description = args["description"]
    triggers = args.get("triggers", [])
    phases = args.get("phases", [])
    output_format = args.get("output_format", "claude_code")

    if output_format == "claude_code":
        content = f"""# {name}

{description}

## Triggers

{chr(10).join(f'- {t}' for t in triggers)}

## Phases

{chr(10).join(f'### Phase {i+1}: {p.get("name", f"Phase {i+1}")}{chr(10)}{p.get("description", "")}' for i, p in enumerate(phases))}
"""
        output_path = OUTPUT_DIR / "claude-code" / "skills" / name / "SKILL.md"
    else:
        content = f'''"""
Skill: {name}
{description}
"""

from typing import List, Dict, Any

class {name.replace("-", "_").title().replace("_", "")}Skill:
    """
    {description}
    """

    name = "{name}"
    triggers = {triggers}
    phases = {[p.get("name", f"phase_{i}") for i, p in enumerate(phases)]}

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute skill phases."""
        results = {{}}
        for phase in self.phases:
            results[phase] = await self._execute_phase(phase, context)
        return results

    async def _execute_phase(self, phase: str, context: Dict[str, Any]) -> Any:
        """Execute single phase."""
        pass
'''
        output_path = OUTPUT_DIR / "agent-sdk" / "python" / "skills" / f"{name.replace('-', '_')}.py"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "status": "created",
                "skill": name,
                "format": output_format,
                "path": str(output_path),
            }, ensure_ascii=False, indent=2)
        }]
    }


@tool(
    "create_workflow",
    """Cria um workflow de orquestracao multi-agente.
    Define steps, dependencies e execution order.""",
    {
        "name": str,
        "description": str,
        "steps": list,
        "output_format": str,
    }
)
async def create_workflow(args: dict) -> dict:
    """Create an orchestration workflow."""
    name = args["name"]
    description = args["description"]
    steps = args.get("steps", [])
    output_format = args.get("output_format", "claude_code")

    if output_format == "claude_code":
        content = f"""# Workflow: {name}

{description}

## Steps

{chr(10).join(f'''### Step {i+1}: {s.get("name", f"Step {i+1}")}
- Agent: {s.get("agent", "N/A")}
- Action: {s.get("action", "N/A")}
- Depends on: {", ".join(s.get("depends_on", [])) or "None"}
''' for i, s in enumerate(steps))}
"""
        output_path = OUTPUT_DIR / "claude-code" / "workflows" / f"{name}.md"
    else:
        content = f'''"""
Workflow: {name}
{description}
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class WorkflowStep:
    name: str
    agent: str
    action: str
    depends_on: List[str] = None

class {name.replace("-", "_").title().replace("_", "")}Workflow:
    """
    {description}
    """

    name = "{name}"
    steps = {[{"name": s.get("name"), "agent": s.get("agent"), "action": s.get("action"), "depends_on": s.get("depends_on", [])} for s in steps]}

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps in dependency order."""
        results = {{}}
        for step in self.steps:
            # Check dependencies
            deps_met = all(d in results for d in step.get("depends_on", []))
            if deps_met:
                results[step["name"]] = await self._execute_step(step, context, results)
        return results

    async def _execute_step(self, step: dict, context: dict, prior_results: dict) -> Any:
        """Execute single workflow step."""
        pass
'''
        output_path = OUTPUT_DIR / "agent-sdk" / "python" / "workflows" / f"{name.replace('-', '_')}.py"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "status": "created",
                "workflow": name,
                "format": output_format,
                "path": str(output_path),
            }, ensure_ascii=False, indent=2)
        }]
    }


@tool(
    "create_tool",
    """Cria uma tool customizada ou MCP server.
    Gera funcao com @tool decorator.""",
    {
        "name": str,
        "description": str,
        "parameters": dict,
        "implementation": str,
        "output_format": str,
    }
)
async def create_tool(args: dict) -> dict:
    """Create a custom tool."""
    name = args["name"]
    description = args["description"]
    parameters = args.get("parameters", {})
    implementation = args.get("implementation", "pass")
    output_format = args.get("output_format", "agent_sdk")

    params_str = ", ".join(f'"{k}": {v}' for k, v in parameters.items())

    content = f'''"""
Tool: {name}
{description}
"""

import json
from claude_agent_sdk import tool

@tool(
    "{name}",
    """{description}""",
    {{{params_str}}}
)
async def {name.replace("-", "_")}(args: dict) -> dict:
    """
    {description}
    """
    {implementation}

    return {{
        "content": [{{"type": "text", "text": json.dumps({{"status": "ok"}})}}]
    }}
'''

    output_path = OUTPUT_DIR / "agent-sdk" / "python" / "tools" / f"{name.replace('-', '_')}.py"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "status": "created",
                "tool": name,
                "path": str(output_path),
            }, ensure_ascii=False, indent=2)
        }]
    }


@tool(
    "create_command",
    """Cria um slash command para Claude Code.
    Gera arquivo .md com trigger e instrucoes.""",
    {
        "name": str,
        "description": str,
        "trigger": str,
        "instructions": str,
    }
)
async def create_command(args: dict) -> dict:
    """Create a slash command."""
    name = args["name"]
    description = args["description"]
    trigger = args.get("trigger", f"/{name}")
    instructions = args.get("instructions", "")

    content = f"""---
name: {name}
description: {description}
trigger: {trigger}
---

# /{name}

{description}

## Instructions

{instructions}
"""

    output_path = OUTPUT_DIR / "claude-code" / "commands" / f"{name}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "status": "created",
                "command": name,
                "trigger": trigger,
                "path": str(output_path),
            }, ensure_ascii=False, indent=2)
        }]
    }


@tool(
    "generate_plugin",
    """Gera plugin completo com todos os componentes.
    Orquestra criacao de agents, skills, workflows, tools e commands.""",
    {
        "plugin_name": str,
        "description": str,
        "components": dict,
    }
)
async def generate_plugin(args: dict) -> dict:
    """Generate complete plugin with all components."""
    plugin_name = args["plugin_name"]
    description = args["description"]
    components = args.get("components", {})

    results = {
        "plugin": plugin_name,
        "description": description,
        "generated": {
            "agents": [],
            "skills": [],
            "workflows": [],
            "tools": [],
            "commands": [],
        }
    }

    # Generate agents
    for agent in components.get("agents", []):
        result = await create_agent({**agent, "output_format": "claude_code"})
        results["generated"]["agents"].append(agent.get("name"))
        # Also generate Agent SDK version
        await create_agent({**agent, "output_format": "agent_sdk"})

    # Generate skills
    for skill in components.get("skills", []):
        result = await create_skill({**skill, "output_format": "claude_code"})
        results["generated"]["skills"].append(skill.get("name"))
        await create_skill({**skill, "output_format": "agent_sdk"})

    # Generate workflows
    for workflow in components.get("workflows", []):
        result = await create_workflow({**workflow, "output_format": "claude_code"})
        results["generated"]["workflows"].append(workflow.get("name"))
        await create_workflow({**workflow, "output_format": "agent_sdk"})

    # Generate tools
    for tool_def in components.get("tools", []):
        result = await create_tool({**tool_def, "output_format": "agent_sdk"})
        results["generated"]["tools"].append(tool_def.get("name"))

    # Generate commands
    for command in components.get("commands", []):
        result = await create_command(command)
        results["generated"]["commands"].append(command.get("name"))

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(results, ensure_ascii=False, indent=2)
        }]
    }


# =============================================================================
# MCP SERVER
# =============================================================================

def create_mcp_server():
    """Create MCP server with all Ultra Arquiteto tools."""
    all_tools = [
        create_agent,
        create_skill,
        create_workflow,
        create_tool,
        create_command,
        generate_plugin,
    ]

    return create_sdk_mcp_server(
        name="ultra-arquiteto",
        version="1.0.0",
        description="Plugin especialista em criacao de plugins para Claude Code e Claude Agent SDK",
        tools=all_tools,
    )


# =============================================================================
# CLI
# =============================================================================

async def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        print("Starting Ultra Arquiteto MCP Server...")
        server = create_mcp_server()
        await server.run()
    else:
        print("Ultra Arquiteto - Plugin Generator")
        print("Usage: python main.py serve")


if __name__ == "__main__":
    asyncio.run(main())
