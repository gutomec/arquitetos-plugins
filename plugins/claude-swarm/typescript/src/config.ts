/**
 * Claude Swarm - Configuration
 * Configuracoes centralizadas para o sistema de swarm.
 */

import 'dotenv/config';

export interface SwarmConfig {
  // Redis
  redisHost: string;
  redisPort: number;
  redisPassword?: string;
  redisDb: number;

  // Agent
  agentId: string;
  agentType: string;

  // Anthropic
  anthropicApiKey: string;
  claudeModel: string;
  orchestratorModel: string;

  // Timeouts
  taskTimeout: number;
  collectTimeout: number;
  heartbeatInterval: number;
  heartbeatTtl: number;

  // Swarm
  maxWorkers: number;
  checkpointInterval: number;

  // Logging
  logLevel: string;
}

export const config: SwarmConfig = {
  // Redis
  redisHost: process.env.SWARM_REDIS_HOST || 'localhost',
  redisPort: parseInt(process.env.SWARM_REDIS_PORT || '6379'),
  redisPassword: process.env.SWARM_REDIS_PASSWORD,
  redisDb: parseInt(process.env.SWARM_REDIS_DB || '0'),

  // Agent
  agentId: process.env.SWARM_AGENT_ID || 'unknown',
  agentType: process.env.SWARM_AGENT_TYPE || 'worker',

  // Anthropic
  anthropicApiKey: process.env.ANTHROPIC_API_KEY || '',
  claudeModel: process.env.CLAUDE_MODEL || 'claude-sonnet-4-20250514',
  orchestratorModel: process.env.ORCHESTRATOR_MODEL || 'claude-opus-4-5-20251101',

  // Timeouts
  taskTimeout: parseInt(process.env.SWARM_TASK_TIMEOUT || '300000'),
  collectTimeout: parseInt(process.env.SWARM_COLLECT_TIMEOUT || '30'),
  heartbeatInterval: parseInt(process.env.SWARM_HEARTBEAT_INTERVAL || '10'),
  heartbeatTtl: parseInt(process.env.SWARM_HEARTBEAT_TTL || '60'),

  // Swarm
  maxWorkers: parseInt(process.env.SWARM_MAX_WORKERS || '10'),
  checkpointInterval: parseInt(process.env.SWARM_CHECKPOINT_INTERVAL || '60000'),

  // Logging
  logLevel: process.env.SWARM_LOG_LEVEL || 'INFO',
};

export interface AgentTypeConfig {
  model: string;
  maxTokens: number;
  temperature: number;
  tools: string[];
}

export const agentConfigs: Record<string, AgentTypeConfig> = {
  orchestrator: {
    model: 'claude-opus-4-5-20251101',
    maxTokens: 8192,
    temperature: 0.7,
    tools: ['swarm_publish', 'swarm_collect', 'swarm_broadcast', 'swarm_health_check', 'swarm_state_set', 'swarm_state_get'],
  },
  analyst: {
    model: 'claude-sonnet-4-20250514',
    maxTokens: 4096,
    temperature: 0.5,
    tools: ['swarm_state_get', 'swarm_store_result', 'read_file', 'search_code'],
  },
  coder: {
    model: 'claude-sonnet-4-20250514',
    maxTokens: 8192,
    temperature: 0.3,
    tools: ['swarm_state_get', 'swarm_store_result', 'read_file', 'write_file', 'edit_file'],
  },
  reviewer: {
    model: 'claude-sonnet-4-20250514',
    maxTokens: 4096,
    temperature: 0.4,
    tools: ['swarm_state_get', 'swarm_store_result', 'read_file', 'search_code'],
  },
  tester: {
    model: 'claude-sonnet-4-20250514',
    maxTokens: 4096,
    temperature: 0.2,
    tools: ['swarm_state_get', 'swarm_store_result', 'read_file', 'write_file', 'run_command'],
  },
  researcher: {
    model: 'claude-sonnet-4-20250514',
    maxTokens: 4096,
    temperature: 0.6,
    tools: ['swarm_state_get', 'swarm_store_result', 'web_search', 'web_fetch'],
  },
};

export function getAgentConfig(agentType: string): AgentTypeConfig {
  return agentConfigs[agentType] || agentConfigs.analyst;
}
