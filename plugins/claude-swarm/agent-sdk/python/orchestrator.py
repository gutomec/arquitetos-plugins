"""
Claude Swarm - Orchestrator
Agente orquestrador que coordena todos os workers.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from anthropic import Anthropic

from config import config, agent_config
from message_broker import broker, Message, MessageType, Priority


class ExecutionStrategy(str, Enum):
    """Estrategias de execucao."""
    FAN_OUT = "fan-out"
    PIPELINE = "pipeline"
    MAP_REDUCE = "map-reduce"
    AUTO = "auto"


@dataclass
class TaskResult:
    """Resultado de uma tarefa."""
    task_id: str
    worker: str
    success: bool
    result: Dict[str, Any]
    duration_ms: int


class Orchestrator:
    """
    Agente Orchestrator do Swarm.
    Coordena workers e executa estrategias de orquestracao.
    """

    def __init__(self):
        self.agent_id = "orchestrator"
        self.config = agent_config.get_config("orchestrator")
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self._running = False
        self._pending_tasks: Dict[str, dict] = {}

    @property
    def system_prompt(self) -> str:
        return """Voce e o Orchestrator do Claude Swarm - o lider que coordena uma equipe de agentes especializados.

Sua responsabilidade:
1. Analisar tarefas complexas e decompor em subtarefas
2. Delegar trabalho para workers apropriados
3. Coordenar execucao paralela ou sequencial
4. Sintetizar resultados de multiplos workers
5. Garantir qualidade e completude das entregas

Workers disponiveis:
- analyst: Analise de codigo, arquitetura e requisitos
- coder: Implementacao e codificacao
- reviewer: Revisao de codigo e qualidade
- tester: Criacao e execucao de testes
- researcher: Pesquisa e coleta de informacoes

Estrategias de execucao:
- fan-out: Todos workers em paralelo (para tarefas independentes)
- pipeline: Workers em sequencia (cada um recebe output do anterior)
- map-reduce: Dividir dados, processar paralelo, agregar

Diretrizes:
- Escolha a estrategia mais eficiente para cada tarefa
- Distribua trabalho de forma balanceada
- Sintetize resultados de forma clara e acionavel
- Identifique e resolva conflitos entre workers"""

    async def _analyze_task(self, description: str) -> Dict[str, Any]:
        """
        Analisa tarefa e determina estrategia e workers.

        Args:
            description: Descricao da tarefa

        Returns:
            Plano de execucao
        """
        response = self.client.messages.create(
            model=self.config["model"],
            max_tokens=2048,
            system="""Voce e um planejador de tarefas. Analise a tarefa e retorne um JSON com:
{
    "strategy": "fan-out" | "pipeline" | "map-reduce",
    "workers": ["lista", "de", "workers", "necessarios"],
    "subtasks": [{"worker": "tipo", "instruction": "instrucao especifica"}],
    "rationale": "explicacao da escolha"
}

Workers disponiveis: analyst, coder, reviewer, tester, researcher

Retorne APENAS o JSON, sem markdown ou explicacoes adicionais.""",
            messages=[{"role": "user", "content": f"Tarefa: {description}"}]
        )

        # Extrair JSON da resposta
        text = response.content[0].text
        try:
            # Tentar parse direto
            return json.loads(text)
        except json.JSONDecodeError:
            # Tentar extrair JSON do texto
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            # Fallback
            return {
                "strategy": "fan-out",
                "workers": ["analyst"],
                "subtasks": [{"worker": "analyst", "instruction": description}],
                "rationale": "Fallback para analise simples"
            }

    async def execute_fan_out(
        self,
        description: str,
        workers: List[str],
        subtasks: List[dict]
    ) -> Dict[str, Any]:
        """
        Executa estrategia fan-out (paralelo).

        Args:
            description: Descricao original
            workers: Lista de workers
            subtasks: Subtarefas

        Returns:
            Resultado agregado
        """
        # Verificar workers disponiveis
        health = await broker.health_check()
        alive_workers = [w["name"].replace("worker-", "") for w in health["workers"] if w["status"] == "alive"]

        # Filtrar subtasks para workers disponiveis
        valid_subtasks = [st for st in subtasks if st["worker"] in alive_workers]

        if not valid_subtasks:
            return {"error": "Nenhum worker disponivel", "available": alive_workers}

        # Enviar todas as tarefas em paralelo
        task_ids = []
        for subtask in valid_subtasks:
            message = Message(
                type=MessageType.TASK,
                to_agent=f"worker-{subtask['worker']}",
                payload={
                    "instruction": f"[FAN-OUT] {subtask['instruction']}\n\nTarefa original: {description}",
                    "strategy": "fan-out"
                },
                metadata={"priority": Priority.MEDIUM.value, "ttl": 300000}
            )

            await broker.publish(f"worker-{subtask['worker']}", message)
            task_ids.append({"id": message.id, "worker": subtask["worker"]})
            self._pending_tasks[message.id] = {"worker": subtask["worker"], "status": "pending"}

        # Coletar resultados
        results = []
        for task in task_ids:
            result = await broker.collect(task["id"], timeout_seconds=config.collect_timeout)
            if result:
                results.append(TaskResult(
                    task_id=task["id"],
                    worker=task["worker"],
                    success=True,
                    result=result.payload.get("result", {}),
                    duration_ms=0
                ))
            else:
                results.append(TaskResult(
                    task_id=task["id"],
                    worker=task["worker"],
                    success=False,
                    result={"error": "timeout"},
                    duration_ms=0
                ))

        # Sintetizar
        return await self._synthesize_results(description, results, "fan-out")

    async def execute_pipeline(
        self,
        description: str,
        workers: List[str],
        subtasks: List[dict]
    ) -> Dict[str, Any]:
        """
        Executa estrategia pipeline (sequencial).

        Args:
            description: Descricao original
            workers: Lista de workers em ordem
            subtasks: Subtarefas

        Returns:
            Resultado final
        """
        accumulated_context = description
        results = []

        for i, subtask in enumerate(subtasks):
            instruction = f"""[PIPELINE STAGE {i + 1}/{len(subtasks)}]

{subtask['instruction']}

Contexto acumulado dos estagios anteriores:
{accumulated_context}

Execute sua parte e retorne o resultado para o proximo estagio."""

            message = Message(
                type=MessageType.TASK,
                to_agent=f"worker-{subtask['worker']}",
                payload={"instruction": instruction, "strategy": "pipeline", "stage": i},
                metadata={"priority": Priority.HIGH.value, "ttl": 300000}
            )

            await broker.publish(f"worker-{subtask['worker']}", message)

            result = await broker.collect(message.id, timeout_seconds=config.collect_timeout * 2)

            if result:
                result_data = result.payload.get("result", {})
                results.append(TaskResult(
                    task_id=message.id,
                    worker=subtask["worker"],
                    success=True,
                    result=result_data,
                    duration_ms=0
                ))
                # Acumular contexto
                accumulated_context += f"\n\n[OUTPUT {subtask['worker'].upper()}]:\n{json.dumps(result_data, indent=2)}"
            else:
                results.append(TaskResult(
                    task_id=message.id,
                    worker=subtask["worker"],
                    success=False,
                    result={"error": "timeout"},
                    duration_ms=0
                ))
                break  # Pipeline para no primeiro erro

        return await self._synthesize_results(description, results, "pipeline")

    async def execute_map_reduce(
        self,
        description: str,
        data: Any,
        worker_type: str = "analyst"
    ) -> Dict[str, Any]:
        """
        Executa estrategia map-reduce.

        Args:
            description: Descricao da tarefa
            data: Dados a processar
            worker_type: Tipo de worker para processamento

        Returns:
            Resultado agregado
        """
        # Dividir dados em chunks
        if isinstance(data, list):
            chunk_size = max(1, len(data) // 5)  # 5 chunks
            chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        elif isinstance(data, str):
            lines = data.split('\n')
            chunk_size = max(1, len(lines) // 5)
            chunks = ['\n'.join(lines[i:i+chunk_size]) for i in range(0, len(lines), chunk_size)]
        else:
            chunks = [data]

        # Map: processar chunks em paralelo
        task_ids = []
        for i, chunk in enumerate(chunks):
            instruction = f"""[MAP-REDUCE CHUNK {i + 1}/{len(chunks)}]

Tarefa: {description}

Processe este chunk de dados:
{json.dumps(chunk) if not isinstance(chunk, str) else chunk}

Retorne resultado estruturado em JSON."""

            message = Message(
                type=MessageType.TASK,
                to_agent=f"worker-{worker_type}",
                payload={"instruction": instruction, "strategy": "map-reduce", "chunk": i},
                metadata={"priority": Priority.MEDIUM.value, "ttl": 300000}
            )

            await broker.publish(f"worker-{worker_type}", message)
            task_ids.append({"id": message.id, "chunk": i})

        # Coletar resultados
        chunk_results = []
        for task in task_ids:
            result = await broker.collect(task["id"], timeout_seconds=config.collect_timeout)
            if result:
                chunk_results.append(result.payload.get("result", {}))

        # Reduce: agregar resultados
        return await self._reduce_results(description, chunk_results)

    async def _synthesize_results(
        self,
        description: str,
        results: List[TaskResult],
        strategy: str
    ) -> Dict[str, Any]:
        """
        Sintetiza resultados de multiplos workers.

        Args:
            description: Tarefa original
            results: Resultados dos workers
            strategy: Estrategia usada

        Returns:
            Sintese final
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        results_text = "\n\n".join([
            f"[{r.worker.upper()}]:\n{json.dumps(r.result, indent=2)}"
            for r in successful
        ])

        response = self.client.messages.create(
            model=self.config["model"],
            max_tokens=4096,
            system=self.system_prompt,
            messages=[{
                "role": "user",
                "content": f"""Sintetize os resultados dos workers.

TAREFA ORIGINAL:
{description}

ESTRATEGIA: {strategy}

RESULTADOS DOS WORKERS:
{results_text}

WORKERS QUE FALHARAM: {[r.worker for r in failed] if failed else 'Nenhum'}

Crie uma sintese consolidada com:
1. Resumo executivo
2. Principais descobertas/entregas
3. Conflitos ou inconsistencias (se houver)
4. Recomendacoes de proximos passos"""
            }]
        )

        return {
            "success": True,
            "strategy": strategy,
            "workers_consulted": len(results),
            "workers_successful": len(successful),
            "workers_failed": len(failed),
            "synthesis": response.content[0].text,
            "raw_results": [{"worker": r.worker, "result": r.result} for r in successful]
        }

    async def _reduce_results(
        self,
        description: str,
        chunk_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        Reduz/agrega resultados de map-reduce.

        Args:
            description: Tarefa original
            chunk_results: Resultados dos chunks

        Returns:
            Resultado agregado
        """
        response = self.client.messages.create(
            model=self.config["model"],
            max_tokens=4096,
            system="""Voce e o Reducer do map-reduce. Agregue resultados de multiplos chunks em uma resposta unificada.
Identifique padroes, agregue metricas, e sintetize insights.""",
            messages=[{
                "role": "user",
                "content": f"""TAREFA: {description}

RESULTADOS DOS CHUNKS ({len(chunk_results)}):
{json.dumps(chunk_results, indent=2)}

Agregue todos os resultados em uma resposta unificada."""
            }]
        )

        return {
            "success": True,
            "strategy": "map-reduce",
            "chunks_processed": len(chunk_results),
            "aggregated_result": response.content[0].text
        }

    async def execute(
        self,
        description: str,
        strategy: ExecutionStrategy = ExecutionStrategy.AUTO,
        data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Executa uma tarefa com a estrategia especificada.

        Args:
            description: Descricao da tarefa
            strategy: Estrategia de execucao
            data: Dados opcionais para map-reduce

        Returns:
            Resultado da execucao
        """
        await broker.connect()

        # Analisar tarefa se estrategia for AUTO
        if strategy == ExecutionStrategy.AUTO:
            plan = await self._analyze_task(description)
            strategy = ExecutionStrategy(plan.get("strategy", "fan-out"))
            workers = plan.get("workers", ["analyst"])
            subtasks = plan.get("subtasks", [{"worker": "analyst", "instruction": description}])
        else:
            # Usar analise simples
            plan = await self._analyze_task(description)
            workers = plan.get("workers", ["analyst"])
            subtasks = plan.get("subtasks", [{"worker": "analyst", "instruction": description}])

        print(f"[ORCHESTRATOR] Executando com estrategia: {strategy.value}")
        print(f"[ORCHESTRATOR] Workers: {workers}")

        # Executar estrategia
        if strategy == ExecutionStrategy.FAN_OUT:
            return await self.execute_fan_out(description, workers, subtasks)
        elif strategy == ExecutionStrategy.PIPELINE:
            return await self.execute_pipeline(description, workers, subtasks)
        elif strategy == ExecutionStrategy.MAP_REDUCE:
            return await self.execute_map_reduce(description, data or description)
        else:
            return {"error": f"Estrategia desconhecida: {strategy}"}

    async def broadcast(self, action: str, message: str = "") -> str:
        """
        Envia broadcast para todos workers.

        Args:
            action: Acao
            message: Mensagem

        Returns:
            ID do broadcast
        """
        return await broker.broadcast(action, message)

    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica saude do swarm.

        Returns:
            Status dos workers
        """
        await broker.connect()
        return await broker.health_check()

    async def shutdown(self) -> None:
        """Encerra o swarm graciosamente."""
        print("[ORCHESTRATOR] Iniciando shutdown do swarm...")
        await self.broadcast("shutdown", "Swarm encerrando")
        await asyncio.sleep(2)  # Dar tempo para workers processarem
        await broker.disconnect()
        print("[ORCHESTRATOR] Swarm encerrado")
