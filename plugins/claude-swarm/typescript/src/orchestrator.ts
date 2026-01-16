/**
 * Claude Swarm - Orchestrator
 * Agente orquestrador que coordena todos os workers.
 */

import Anthropic from '@anthropic-ai/sdk';
import { config, getAgentConfig } from './config';
import { broker } from './message-broker';
import {
  Message,
  MessageType,
  Priority,
  ExecutionStrategy,
  ExecutionPlan,
  ExecutionResult,
  TaskResult,
  Subtask,
} from './types';

export class Orchestrator {
  private agentId = 'orchestrator';
  private config = getAgentConfig('orchestrator');
  private client: Anthropic;
  private pendingTasks: Map<string, { worker: string; status: string }> = new Map();

  constructor() {
    this.client = new Anthropic({ apiKey: config.anthropicApiKey });
  }

  get systemPrompt(): string {
    return `Voce e o Orchestrator do Claude Swarm - o lider que coordena uma equipe de agentes especializados.

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
- Identifique e resolva conflitos entre workers`;
  }

  private async analyzeTask(description: string): Promise<ExecutionPlan> {
    const response = await this.client.messages.create({
      model: this.config.model,
      max_tokens: 2048,
      system: `Voce e um planejador de tarefas. Analise a tarefa e retorne um JSON com:
{
    "strategy": "fan-out" | "pipeline" | "map-reduce",
    "workers": ["lista", "de", "workers", "necessarios"],
    "subtasks": [{"worker": "tipo", "instruction": "instrucao especifica"}],
    "rationale": "explicacao da escolha"
}

Workers disponiveis: analyst, coder, reviewer, tester, researcher

Retorne APENAS o JSON, sem markdown ou explicacoes adicionais.`,
      messages: [{ role: 'user', content: `Tarefa: ${description}` }],
    });

    const text = (response.content[0] as Anthropic.TextBlock).text;
    try {
      return JSON.parse(text);
    } catch {
      const match = text.match(/\{.*\}/s);
      if (match) {
        return JSON.parse(match[0]);
      }
      return {
        strategy: ExecutionStrategy.FAN_OUT,
        workers: ['analyst'],
        subtasks: [{ worker: 'analyst', instruction: description }],
        rationale: 'Fallback para analise simples',
      };
    }
  }

  async executeFanOut(
    description: string,
    workers: string[],
    subtasks: Subtask[]
  ): Promise<ExecutionResult> {
    const health = await broker.healthCheck();
    const aliveWorkers = health.workers
      .filter((w) => w.status === 'alive')
      .map((w) => w.name.replace('worker-', ''));

    const validSubtasks = subtasks.filter((st) => aliveWorkers.includes(st.worker));

    if (validSubtasks.length === 0) {
      return { success: false, strategy: 'fan-out', error: 'Nenhum worker disponivel' };
    }

    const taskIds: Array<{ id: string; worker: string }> = [];

    for (const subtask of validSubtasks) {
      const message = broker.createMessage(
        MessageType.TASK,
        `worker-${subtask.worker}`,
        {
          instruction: `[FAN-OUT] ${subtask.instruction}\n\nTarefa original: ${description}`,
          strategy: 'fan-out',
        },
        Priority.MEDIUM
      );

      await broker.publish(`worker-${subtask.worker}`, message);
      taskIds.push({ id: message.id, worker: subtask.worker });
      this.pendingTasks.set(message.id, { worker: subtask.worker, status: 'pending' });
    }

    const results: TaskResult[] = [];
    for (const task of taskIds) {
      const result = await broker.collect(task.id, config.collectTimeout);
      if (result) {
        results.push({
          taskId: task.id,
          worker: task.worker,
          success: true,
          result: (result.payload.result as Record<string, unknown>) || {},
          durationMs: 0,
        });
      } else {
        results.push({
          taskId: task.id,
          worker: task.worker,
          success: false,
          result: { error: 'timeout' },
          durationMs: 0,
        });
      }
    }

    return this.synthesizeResults(description, results, 'fan-out');
  }

  async executePipeline(
    description: string,
    workers: string[],
    subtasks: Subtask[]
  ): Promise<ExecutionResult> {
    let accumulatedContext = description;
    const results: TaskResult[] = [];

    for (let i = 0; i < subtasks.length; i++) {
      const subtask = subtasks[i];
      const instruction = `[PIPELINE STAGE ${i + 1}/${subtasks.length}]

${subtask.instruction}

Contexto acumulado dos estagios anteriores:
${accumulatedContext}

Execute sua parte e retorne o resultado para o proximo estagio.`;

      const message = broker.createMessage(
        MessageType.TASK,
        `worker-${subtask.worker}`,
        { instruction, strategy: 'pipeline', stage: i },
        Priority.HIGH
      );

      await broker.publish(`worker-${subtask.worker}`, message);

      const result = await broker.collect(message.id, config.collectTimeout * 2);

      if (result) {
        const resultData = (result.payload.result as Record<string, unknown>) || {};
        results.push({
          taskId: message.id,
          worker: subtask.worker,
          success: true,
          result: resultData,
          durationMs: 0,
        });
        accumulatedContext += `\n\n[OUTPUT ${subtask.worker.toUpperCase()}]:\n${JSON.stringify(resultData, null, 2)}`;
      } else {
        results.push({
          taskId: message.id,
          worker: subtask.worker,
          success: false,
          result: { error: 'timeout' },
          durationMs: 0,
        });
        break;
      }
    }

    return this.synthesizeResults(description, results, 'pipeline');
  }

  async executeMapReduce(
    description: string,
    data: unknown,
    workerType: string = 'analyst'
  ): Promise<ExecutionResult> {
    let chunks: unknown[];

    if (Array.isArray(data)) {
      const chunkSize = Math.max(1, Math.ceil(data.length / 5));
      chunks = [];
      for (let i = 0; i < data.length; i += chunkSize) {
        chunks.push(data.slice(i, i + chunkSize));
      }
    } else if (typeof data === 'string') {
      const lines = data.split('\n');
      const chunkSize = Math.max(1, Math.ceil(lines.length / 5));
      chunks = [];
      for (let i = 0; i < lines.length; i += chunkSize) {
        chunks.push(lines.slice(i, i + chunkSize).join('\n'));
      }
    } else {
      chunks = [data];
    }

    const taskIds: Array<{ id: string; chunk: number }> = [];

    for (let i = 0; i < chunks.length; i++) {
      const instruction = `[MAP-REDUCE CHUNK ${i + 1}/${chunks.length}]

Tarefa: ${description}

Processe este chunk de dados:
${typeof chunks[i] === 'string' ? chunks[i] : JSON.stringify(chunks[i])}

Retorne resultado estruturado em JSON.`;

      const message = broker.createMessage(
        MessageType.TASK,
        `worker-${workerType}`,
        { instruction, strategy: 'map-reduce', chunk: i },
        Priority.MEDIUM
      );

      await broker.publish(`worker-${workerType}`, message);
      taskIds.push({ id: message.id, chunk: i });
    }

    const chunkResults: Record<string, unknown>[] = [];
    for (const task of taskIds) {
      const result = await broker.collect(task.id, config.collectTimeout);
      if (result) {
        chunkResults.push((result.payload.result as Record<string, unknown>) || {});
      }
    }

    return this.reduceResults(description, chunkResults);
  }

  private async synthesizeResults(
    description: string,
    results: TaskResult[],
    strategy: string
  ): Promise<ExecutionResult> {
    const successful = results.filter((r) => r.success);
    const failed = results.filter((r) => !r.success);

    const resultsText = successful
      .map((r) => `[${r.worker.toUpperCase()}]:\n${JSON.stringify(r.result, null, 2)}`)
      .join('\n\n');

    const response = await this.client.messages.create({
      model: this.config.model,
      max_tokens: 4096,
      system: this.systemPrompt,
      messages: [
        {
          role: 'user',
          content: `Sintetize os resultados dos workers.

TAREFA ORIGINAL:
${description}

ESTRATEGIA: ${strategy}

RESULTADOS DOS WORKERS:
${resultsText}

WORKERS QUE FALHARAM: ${failed.length > 0 ? failed.map((r) => r.worker).join(', ') : 'Nenhum'}

Crie uma sintese consolidada com:
1. Resumo executivo
2. Principais descobertas/entregas
3. Conflitos ou inconsistencias (se houver)
4. Recomendacoes de proximos passos`,
        },
      ],
    });

    return {
      success: true,
      strategy,
      workersConsulted: results.length,
      workersSuccessful: successful.length,
      workersFailed: failed.length,
      synthesis: (response.content[0] as Anthropic.TextBlock).text,
      rawResults: successful.map((r) => ({ worker: r.worker, result: r.result })),
    };
  }

  private async reduceResults(
    description: string,
    chunkResults: Record<string, unknown>[]
  ): Promise<ExecutionResult> {
    const response = await this.client.messages.create({
      model: this.config.model,
      max_tokens: 4096,
      system: `Voce e o Reducer do map-reduce. Agregue resultados de multiplos chunks em uma resposta unificada.
Identifique padroes, agregue metricas, e sintetize insights.`,
      messages: [
        {
          role: 'user',
          content: `TAREFA: ${description}

RESULTADOS DOS CHUNKS (${chunkResults.length}):
${JSON.stringify(chunkResults, null, 2)}

Agregue todos os resultados em uma resposta unificada.`,
        },
      ],
    });

    return {
      success: true,
      strategy: 'map-reduce',
      synthesis: (response.content[0] as Anthropic.TextBlock).text,
    };
  }

  async execute(
    description: string,
    strategy: ExecutionStrategy = ExecutionStrategy.AUTO,
    data?: unknown
  ): Promise<ExecutionResult> {
    await broker.connect();

    let plan: ExecutionPlan;
    let effectiveStrategy = strategy;

    if (strategy === ExecutionStrategy.AUTO) {
      plan = await this.analyzeTask(description);
      effectiveStrategy = plan.strategy as ExecutionStrategy;
    } else {
      plan = await this.analyzeTask(description);
    }

    console.log(`[ORCHESTRATOR] Executando com estrategia: ${effectiveStrategy}`);
    console.log(`[ORCHESTRATOR] Workers: ${plan.workers.join(', ')}`);

    switch (effectiveStrategy) {
      case ExecutionStrategy.FAN_OUT:
        return this.executeFanOut(description, plan.workers, plan.subtasks);
      case ExecutionStrategy.PIPELINE:
        return this.executePipeline(description, plan.workers, plan.subtasks);
      case ExecutionStrategy.MAP_REDUCE:
        return this.executeMapReduce(description, data || description);
      default:
        return { success: false, strategy: String(effectiveStrategy), error: 'Estrategia desconhecida' };
    }
  }

  async broadcast(action: string, message: string = ''): Promise<string> {
    return broker.broadcast(action, message);
  }

  async healthCheck(): Promise<ReturnType<typeof broker.healthCheck>> {
    await broker.connect();
    return broker.healthCheck();
  }

  async shutdown(): Promise<void> {
    console.log('[ORCHESTRATOR] Iniciando shutdown do swarm...');
    await this.broadcast('shutdown', 'Swarm encerrando');
    await new Promise((resolve) => setTimeout(resolve, 2000));
    await broker.disconnect();
    console.log('[ORCHESTRATOR] Swarm encerrado');
  }
}
