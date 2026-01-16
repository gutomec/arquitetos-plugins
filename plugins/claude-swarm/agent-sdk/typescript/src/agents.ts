/**
 * Claude Swarm - Agent Implementations
 * Implementacoes dos agentes usando Claude Agent SDK.
 */

import Anthropic from '@anthropic-ai/sdk';
import { config, getAgentConfig, AgentTypeConfig } from './config';
import { broker } from './message-broker';
import { Message, MessageType, AgentContext, ToolDefinition } from './types';
import { execSync } from 'child_process';
import * as fs from 'fs';

export abstract class BaseAgent {
  protected agentType: string;
  protected agentId: string;
  protected config: AgentTypeConfig;
  protected client: Anthropic;
  protected running = false;
  protected currentTask: string | null = null;

  constructor(agentType: string) {
    this.agentType = agentType;
    this.agentId = `worker-${agentType}`;
    this.config = getAgentConfig(agentType);
    this.client = new Anthropic({ apiKey: config.anthropicApiKey });
  }

  abstract get systemPrompt(): string;

  get tools(): ToolDefinition[] {
    return this.getToolDefinitions();
  }

  private getToolDefinitions(): ToolDefinition[] {
    const allTools: Record<string, ToolDefinition> = {
      swarm_state_get: {
        name: 'swarm_state_get',
        description: 'Recupera estado compartilhado do Swarm',
        input_schema: {
          type: 'object',
          properties: {
            key: { type: 'string', description: 'Chave do estado' },
          },
          required: ['key'],
        },
      },
      swarm_store_result: {
        name: 'swarm_store_result',
        description: 'Armazena resultado da tarefa para o orchestrator',
        input_schema: {
          type: 'object',
          properties: {
            result: { type: 'string', description: 'Resultado em JSON' },
            status: { type: 'string', enum: ['success', 'partial', 'failed'] },
          },
          required: ['result'],
        },
      },
      read_file: {
        name: 'read_file',
        description: 'Le conteudo de um arquivo',
        input_schema: {
          type: 'object',
          properties: {
            path: { type: 'string', description: 'Caminho do arquivo' },
          },
          required: ['path'],
        },
      },
      write_file: {
        name: 'write_file',
        description: 'Escreve conteudo em um arquivo',
        input_schema: {
          type: 'object',
          properties: {
            path: { type: 'string', description: 'Caminho do arquivo' },
            content: { type: 'string', description: 'Conteudo' },
          },
          required: ['path', 'content'],
        },
      },
      search_code: {
        name: 'search_code',
        description: 'Busca padrao em arquivos de codigo',
        input_schema: {
          type: 'object',
          properties: {
            pattern: { type: 'string', description: 'Padrao regex' },
            path: { type: 'string', description: 'Diretorio base' },
          },
          required: ['pattern'],
        },
      },
      run_command: {
        name: 'run_command',
        description: 'Executa comando shell',
        input_schema: {
          type: 'object',
          properties: {
            command: { type: 'string', description: 'Comando a executar' },
          },
          required: ['command'],
        },
      },
    };

    const allowedTools = this.config.tools;
    return allowedTools
      .filter((t) => t in allTools)
      .map((t) => allTools[t]);
  }

  protected async handleToolCall(
    toolName: string,
    toolInput: Record<string, unknown>,
    context: AgentContext
  ): Promise<string> {
    switch (toolName) {
      case 'swarm_state_get': {
        const result = await broker.getState(toolInput.key as string);
        return result ? JSON.stringify(result) : 'null';
      }

      case 'swarm_store_result': {
        const result = JSON.parse(toolInput.result as string);
        const status = (toolInput.status as string) || 'success';
        await broker.storeResult(context.taskId, result, status);
        return `Resultado armazenado com status: ${status}`;
      }

      case 'read_file': {
        try {
          return fs.readFileSync(toolInput.path as string, 'utf-8');
        } catch (e) {
          return `Erro: ${e}`;
        }
      }

      case 'write_file': {
        try {
          fs.writeFileSync(toolInput.path as string, toolInput.content as string);
          return `Arquivo salvo: ${toolInput.path}`;
        } catch (e) {
          return `Erro: ${e}`;
        }
      }

      case 'search_code': {
        try {
          const result = execSync(
            `grep -r "${toolInput.pattern}" ${toolInput.path || '.'}`,
            { timeout: 30000, encoding: 'utf-8' }
          );
          return result || 'Nenhum resultado';
        } catch (e) {
          return `Erro: ${e}`;
        }
      }

      case 'run_command': {
        try {
          const result = execSync(toolInput.command as string, {
            timeout: 60000,
            encoding: 'utf-8',
          });
          return result;
        } catch (e) {
          return `Erro: ${e}`;
        }
      }

      default:
        return `Ferramenta desconhecida: ${toolName}`;
    }
  }

  async processTask(context: AgentContext): Promise<Record<string, unknown>> {
    this.currentTask = context.taskId;
    const messages: Anthropic.MessageParam[] = [
      { role: 'user', content: context.instruction },
    ];

    try {
      while (true) {
        const response = await this.client.messages.create({
          model: this.config.model,
          max_tokens: this.config.maxTokens,
          system: this.systemPrompt,
          tools: this.tools.length > 0 ? this.tools as Anthropic.Tool[] : undefined,
          messages,
        });

        if (response.stop_reason === 'end_turn') {
          const textBlocks = response.content
            .filter((b): b is Anthropic.TextBlock => b.type === 'text')
            .map((b) => b.text);
          return {
            success: true,
            output: textBlocks.join('\n'),
            model: this.config.model,
          };
        }

        if (response.stop_reason === 'tool_use') {
          messages.push({ role: 'assistant', content: response.content });

          const toolResults: Anthropic.ToolResultBlockParam[] = [];
          for (const block of response.content) {
            if (block.type === 'tool_use') {
              const result = await this.handleToolCall(
                block.name,
                block.input as Record<string, unknown>,
                context
              );
              toolResults.push({
                type: 'tool_result',
                tool_use_id: block.id,
                content: result,
              });
            }
          }

          messages.push({ role: 'user', content: toolResults });
        } else {
          break;
        }
      }

      return {
        success: false,
        error: 'Execucao interrompida inesperadamente',
        model: this.config.model,
      };
    } catch (e) {
      return {
        success: false,
        error: String(e),
        model: this.config.model,
      };
    } finally {
      this.currentTask = null;
    }
  }

  async handleMessage(message: Message): Promise<void> {
    if (message.type === MessageType.TASK) {
      console.log(`[${this.agentId}] Recebida tarefa: ${message.id}`);

      const context: AgentContext = {
        taskId: message.id,
        instruction: (message.payload.instruction as string) || '',
        metadata: message.metadata,
        sharedState: {},
      };

      const result = await this.processTask(context);
      await broker.storeResult(message.id, result);

      console.log(`[${this.agentId}] Tarefa ${message.id} completada`);
    } else if (message.type === MessageType.BROADCAST) {
      const action = message.payload.action as string;
      console.log(`[${this.agentId}] Broadcast recebido: ${action}`);

      if (action === 'shutdown') {
        this.running = false;
      } else if (action === 'status') {
        const status = {
          agentId: this.agentId,
          type: this.agentType,
          running: this.running,
          currentTask: this.currentTask,
        };
        await broker.setState(`status:${this.agentId}`, status, 60);
      }
    }
  }

  async start(): Promise<void> {
    this.running = true;
    await broker.connect();

    await broker.setState(`agents:${this.agentId}`, {
      type: this.agentType,
      status: 'running',
      startedAt: Date.now(),
    });

    await broker.subscribe(['tasks', 'broadcast'], (msg) => this.handleMessage(msg));

    this.heartbeatLoop();

    console.log(`[${this.agentId}] Agente iniciado`);

    await broker.listen();
  }

  private heartbeatLoop(): void {
    const interval = setInterval(async () => {
      if (!this.running) {
        clearInterval(interval);
        return;
      }
      await broker.heartbeat();
    }, config.heartbeatInterval * 1000);
  }

  async stop(): Promise<void> {
    this.running = false;
    await broker.setState(`agents:${this.agentId}`, {
      type: this.agentType,
      status: 'stopped',
    });
    await broker.disconnect();
    console.log(`[${this.agentId}] Agente parado`);
  }
}

// =============================================================================
// IMPLEMENTACOES ESPECIFICAS
// =============================================================================

export class AnalystAgent extends BaseAgent {
  constructor() {
    super('analyst');
  }

  get systemPrompt(): string {
    return `Voce e um Analista especializado no Claude Swarm.

Sua especialidade:
- Analisar codigo, arquitetura e requisitos
- Identificar padroes, problemas e oportunidades
- Documentar descobertas de forma clara

Diretrizes:
- Seja objetivo e baseado em evidencias
- Forneca analises estruturadas
- Destaque riscos e recomendacoes

Voce trabalha como parte de um swarm de agentes. Foque na sua especialidade
e contribua com insights de analise para a tarefa coletiva.`;
  }
}

export class CoderAgent extends BaseAgent {
  constructor() {
    super('coder');
  }

  get systemPrompt(): string {
    return `Voce e um Desenvolvedor especializado no Claude Swarm.

Sua especialidade:
- Escrever codigo limpo e eficiente
- Implementar features e corrigir bugs
- Seguir padroes e boas praticas

Diretrizes:
- Codigo deve ser legivel e bem documentado
- Siga os padroes do projeto existente
- Considere performance e seguranca

Voce trabalha como parte de um swarm de agentes. Foque na implementacao
e contribua com codigo de qualidade para a tarefa coletiva.`;
  }
}

export class ReviewerAgent extends BaseAgent {
  constructor() {
    super('reviewer');
  }

  get systemPrompt(): string {
    return `Voce e um Revisor especializado no Claude Swarm.

Sua especialidade:
- Revisar codigo para qualidade e seguranca
- Identificar bugs, vulnerabilidades e melhorias
- Sugerir refatoracoes e otimizacoes

Diretrizes:
- Seja construtivo e especifico
- Priorize issues por severidade
- Forneca sugestoes concretas de melhoria

Voce trabalha como parte de um swarm de agentes. Foque na revisao
e contribua com feedback de qualidade para a tarefa coletiva.`;
  }
}

export class TesterAgent extends BaseAgent {
  constructor() {
    super('tester');
  }

  get systemPrompt(): string {
    return `Voce e um Engenheiro de Testes especializado no Claude Swarm.

Sua especialidade:
- Criar e executar testes automatizados
- Validar requisitos e comportamentos
- Identificar casos de borda e falhas

Diretrizes:
- Cobertura completa de casos de uso
- Testes devem ser reproduziveis
- Documente cenarios e resultados

Voce trabalha como parte de um swarm de agentes. Foque em testes
e contribua com validacao de qualidade para a tarefa coletiva.`;
  }
}

export class ResearcherAgent extends BaseAgent {
  constructor() {
    super('researcher');
  }

  get systemPrompt(): string {
    return `Voce e um Pesquisador especializado no Claude Swarm.

Sua especialidade:
- Pesquisar informacoes e documentacao
- Coletar dados e referencias
- Sintetizar conhecimento relevante

Diretrizes:
- Busque fontes confiaveis
- Valide informacoes encontradas
- Apresente descobertas de forma estruturada

Voce trabalha como parte de um swarm de agentes. Foque na pesquisa
e contribua com conhecimento relevante para a tarefa coletiva.`;
  }
}

// Factory
const AGENT_CLASSES: Record<string, new () => BaseAgent> = {
  analyst: AnalystAgent,
  coder: CoderAgent,
  reviewer: ReviewerAgent,
  tester: TesterAgent,
  researcher: ResearcherAgent,
};

export function createAgent(agentType: string): BaseAgent {
  const AgentClass = AGENT_CLASSES[agentType];
  if (!AgentClass) {
    throw new Error(`Tipo de agente desconhecido: ${agentType}`);
  }
  return new AgentClass();
}
