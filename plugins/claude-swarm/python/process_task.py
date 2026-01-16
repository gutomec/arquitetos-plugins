#!/usr/bin/env python3
"""
Claude Swarm - Task Processor
Script chamado pelo entrypoint para processar tarefas individuais.
"""

import sys
import json
import asyncio
from typing import Dict, Any

from agents import create_agent, AgentContext


async def process_task(agent_type: str, instruction: str) -> Dict[str, Any]:
    """
    Processa uma tarefa com o agente especificado.

    Args:
        agent_type: Tipo do agente
        instruction: Instrucao da tarefa

    Returns:
        Resultado do processamento
    """
    try:
        agent = create_agent(agent_type)

        context = AgentContext(
            task_id="direct-" + str(hash(instruction))[:8],
            instruction=instruction,
            metadata={},
            shared_state={}
        )

        result = await agent.process_task(context)
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent_type": agent_type
        }


def main():
    """Ponto de entrada principal."""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Uso: process_task.py <agent_type> <instruction>"}))
        sys.exit(1)

    agent_type = sys.argv[1]
    instruction = sys.argv[2]

    result = asyncio.run(process_task(agent_type, instruction))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
