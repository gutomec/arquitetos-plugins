"""
Claude Swarm - Agent Implementations
Implementacoes dos agentes usando Claude Agent SDK.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from anthropic import Anthropic

from config import config, agent_config
from message_broker import broker, Message, MessageType


@dataclass
class AgentContext:
    """Contexto de execucao do agente."""
    task_id: str
    instruction: str
    metadata: Dict[str, Any]
    shared_state: Dict[str, Any]


class BaseAgent(ABC):
    """
    Classe base para todos os agentes do Swarm.
    """

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.agent_id = f"worker-{agent_type}"
        self.config = agent_config.get_config(agent_type)
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self._running = False
        self._current_task: Optional[str] = None

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt especifico do agente."""
        pass

    @property
    def tools(self) -> List[Dict[str, Any]]:
        """Ferramentas disponiveis para o agente."""
        return self._get_tool_definitions()

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Retorna definicoes de ferramentas baseado no tipo de agente."""
        all_tools = {
            "swarm_state_get": {
                "name": "swarm_state_get",
                "description": "Recupera estado compartilhado do Swarm",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Chave do estado"}
                    },
                    "required": ["key"]
                }
            },
            "swarm_store_result": {
                "name": "swarm_store_result",
                "description": "Armazena resultado da tarefa para o orchestrator",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "string", "description": "Resultado em JSON"},
                        "status": {"type": "string", "enum": ["success", "partial", "failed"]}
                    },
                    "required": ["result"]
                }
            },
            "read_file": {
                "name": "read_file",
                "description": "Le conteudo de um arquivo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Caminho do arquivo"}
                    },
                    "required": ["path"]
                }
            },
            "write_file": {
                "name": "write_file",
                "description": "Escreve conteudo em um arquivo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Caminho do arquivo"},
                        "content": {"type": "string", "description": "Conteudo"}
                    },
                    "required": ["path", "content"]
                }
            },
            "search_code": {
                "name": "search_code",
                "description": "Busca padrao em arquivos de codigo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Padrao regex"},
                        "path": {"type": "string", "description": "Diretorio base"}
                    },
                    "required": ["pattern"]
                }
            },
            "run_command": {
                "name": "run_command",
                "description": "Executa comando shell",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Comando a executar"}
                    },
                    "required": ["command"]
                }
            }
        }

        allowed_tools = self.config.get("tools", [])
        return [all_tools[t] for t in allowed_tools if t in all_tools]

    async def _handle_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        context: AgentContext
    ) -> str:
        """Processa chamada de ferramenta."""

        if tool_name == "swarm_state_get":
            result = await broker.get_state(tool_input["key"])
            return str(result) if result else "null"

        elif tool_name == "swarm_store_result":
            import json
            result = json.loads(tool_input["result"])
            status = tool_input.get("status", "success")
            await broker.store_result(context.task_id, result, status)
            return f"Resultado armazenado com status: {status}"

        elif tool_name == "read_file":
            try:
                with open(tool_input["path"], "r") as f:
                    return f.read()
            except Exception as e:
                return f"Erro: {e}"

        elif tool_name == "write_file":
            try:
                with open(tool_input["path"], "w") as f:
                    f.write(tool_input["content"])
                return f"Arquivo salvo: {tool_input['path']}"
            except Exception as e:
                return f"Erro: {e}"

        elif tool_name == "search_code":
            import subprocess
            try:
                result = subprocess.run(
                    ["grep", "-r", tool_input["pattern"], tool_input.get("path", ".")],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.stdout or "Nenhum resultado"
            except Exception as e:
                return f"Erro: {e}"

        elif tool_name == "run_command":
            import subprocess
            try:
                result = subprocess.run(
                    tool_input["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return f"stdout: {result.stdout}\nstderr: {result.stderr}"
            except Exception as e:
                return f"Erro: {e}"

        return f"Ferramenta desconhecida: {tool_name}"

    async def process_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Processa uma tarefa usando o Claude.

        Args:
            context: Contexto da tarefa

        Returns:
            Resultado do processamento
        """
        self._current_task = context.task_id
        messages = [{"role": "user", "content": context.instruction}]

        try:
            # Loop de conversacao com ferramentas
            while True:
                response = self.client.messages.create(
                    model=self.config["model"],
                    max_tokens=self.config["max_tokens"],
                    system=self.system_prompt,
                    tools=self.tools if self.tools else None,
                    messages=messages
                )

                # Verificar se terminou
                if response.stop_reason == "end_turn":
                    # Extrair texto final
                    text_blocks = [b.text for b in response.content if hasattr(b, 'text')]
                    return {
                        "success": True,
                        "output": "\n".join(text_blocks),
                        "model": self.config["model"]
                    }

                # Processar tool calls
                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            result = await self._handle_tool_call(
                                block.name,
                                block.input,
                                context
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            })

                    messages.append({"role": "user", "content": tool_results})
                else:
                    # Outros stop reasons
                    break

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.config["model"]
            }
        finally:
            self._current_task = None

    async def handle_message(self, message: Message) -> None:
        """
        Handler para mensagens recebidas.

        Args:
            message: Mensagem recebida
        """
        if message.type == MessageType.TASK:
            print(f"[{self.agent_id}] Recebida tarefa: {message.id}")

            context = AgentContext(
                task_id=message.id,
                instruction=message.payload.get("instruction", ""),
                metadata=message.metadata,
                shared_state={}
            )

            result = await self.process_task(context)
            await broker.store_result(message.id, result)

            print(f"[{self.agent_id}] Tarefa {message.id} completada")

        elif message.type == MessageType.BROADCAST:
            action = message.payload.get("action", "")
            print(f"[{self.agent_id}] Broadcast recebido: {action}")

            if action == "shutdown":
                self._running = False
            elif action == "status":
                status = {
                    "agent_id": self.agent_id,
                    "type": self.agent_type,
                    "running": self._running,
                    "current_task": self._current_task
                }
                await broker.set_state(f"status:{self.agent_id}", status, ttl_seconds=60)

    async def start(self) -> None:
        """Inicia o agente."""
        self._running = True
        await broker.connect()

        # Registrar
        await broker.set_state(f"agents:{self.agent_id}", {
            "type": self.agent_type,
            "status": "running",
            "started_at": asyncio.get_event_loop().time()
        })

        # Inscrever em canais
        await broker.subscribe(
            ["tasks", "broadcast"],
            self.handle_message
        )

        # Iniciar heartbeat
        asyncio.create_task(self._heartbeat_loop())

        print(f"[{self.agent_id}] Agente iniciado")

        # Loop principal
        await broker.listen()

    async def _heartbeat_loop(self) -> None:
        """Loop de heartbeat."""
        while self._running:
            await broker.heartbeat()
            await asyncio.sleep(config.heartbeat_interval)

    async def stop(self) -> None:
        """Para o agente."""
        self._running = False
        await broker.set_state(f"agents:{self.agent_id}", {
            "type": self.agent_type,
            "status": "stopped"
        })
        await broker.disconnect()
        print(f"[{self.agent_id}] Agente parado")


# =============================================================================
# IMPLEMENTACOES ESPECIFICAS
# =============================================================================

class AnalystAgent(BaseAgent):
    """Agente especializado em analise."""

    def __init__(self):
        super().__init__("analyst")

    @property
    def system_prompt(self) -> str:
        return """Voce e um Analista especializado no Claude Swarm.

Sua especialidade:
- Analisar codigo, arquitetura e requisitos
- Identificar padroes, problemas e oportunidades
- Documentar descobertas de forma clara

Diretrizes:
- Seja objetivo e baseado em evidencias
- Forneca analises estruturadas
- Destaque riscos e recomendacoes

Voce trabalha como parte de um swarm de agentes. Foque na sua especialidade
e contribua com insights de analise para a tarefa coletiva."""


class CoderAgent(BaseAgent):
    """Agente especializado em codificacao."""

    def __init__(self):
        super().__init__("coder")

    @property
    def system_prompt(self) -> str:
        return """Voce e um Desenvolvedor especializado no Claude Swarm.

Sua especialidade:
- Escrever codigo limpo e eficiente
- Implementar features e corrigir bugs
- Seguir padroes e boas praticas

Diretrizes:
- Codigo deve ser legivel e bem documentado
- Siga os padroes do projeto existente
- Considere performance e seguranca

Voce trabalha como parte de um swarm de agentes. Foque na implementacao
e contribua com codigo de qualidade para a tarefa coletiva."""


class ReviewerAgent(BaseAgent):
    """Agente especializado em revisao."""

    def __init__(self):
        super().__init__("reviewer")

    @property
    def system_prompt(self) -> str:
        return """Voce e um Revisor especializado no Claude Swarm.

Sua especialidade:
- Revisar codigo para qualidade e seguranca
- Identificar bugs, vulnerabilidades e melhorias
- Sugerir refatoracoes e otimizacoes

Diretrizes:
- Seja construtivo e especifico
- Priorize issues por severidade
- Forneca sugestoes concretas de melhoria

Voce trabalha como parte de um swarm de agentes. Foque na revisao
e contribua com feedback de qualidade para a tarefa coletiva."""


class TesterAgent(BaseAgent):
    """Agente especializado em testes."""

    def __init__(self):
        super().__init__("tester")

    @property
    def system_prompt(self) -> str:
        return """Voce e um Engenheiro de Testes especializado no Claude Swarm.

Sua especialidade:
- Criar e executar testes automatizados
- Validar requisitos e comportamentos
- Identificar casos de borda e falhas

Diretrizes:
- Cobertura completa de casos de uso
- Testes devem ser reproduziveis
- Documente cenarios e resultados

Voce trabalha como parte de um swarm de agentes. Foque em testes
e contribua com validacao de qualidade para a tarefa coletiva."""


class ResearcherAgent(BaseAgent):
    """Agente especializado em pesquisa."""

    def __init__(self):
        super().__init__("researcher")

    @property
    def system_prompt(self) -> str:
        return """Voce e um Pesquisador especializado no Claude Swarm.

Sua especialidade:
- Pesquisar informacoes e documentacao
- Coletar dados e referencias
- Sintetizar conhecimento relevante

Diretrizes:
- Busque fontes confiaveis
- Valide informacoes encontradas
- Apresente descobertas de forma estruturada

Voce trabalha como parte de um swarm de agentes. Foque na pesquisa
e contribua com conhecimento relevante para a tarefa coletiva."""


# Factory
AGENT_CLASSES = {
    "analyst": AnalystAgent,
    "coder": CoderAgent,
    "reviewer": ReviewerAgent,
    "tester": TesterAgent,
    "researcher": ResearcherAgent
}


def create_agent(agent_type: str) -> BaseAgent:
    """
    Cria instancia de agente pelo tipo.

    Args:
        agent_type: Tipo do agente

    Returns:
        Instancia do agente
    """
    if agent_type not in AGENT_CLASSES:
        raise ValueError(f"Tipo de agente desconhecido: {agent_type}")
    return AGENT_CLASSES[agent_type]()
