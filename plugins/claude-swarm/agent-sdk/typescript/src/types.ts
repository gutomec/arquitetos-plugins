/**
 * Claude Swarm - Type Definitions
 */

export enum MessageType {
  TASK = 'TASK',
  RESULT = 'RESULT',
  BROADCAST = 'BROADCAST',
  STATUS = 'STATUS',
  HEARTBEAT = 'HEARTBEAT',
  ERROR = 'ERROR',
}

export enum Priority {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum ExecutionStrategy {
  FAN_OUT = 'fan-out',
  PIPELINE = 'pipeline',
  MAP_REDUCE = 'map-reduce',
  AUTO = 'auto',
}

export interface MessageMetadata {
  priority: Priority;
  ttl: number;
}

export interface Message {
  type: MessageType;
  id: string;
  timestamp: string;
  from: string;
  to: string;
  payload: Record<string, unknown>;
  metadata: MessageMetadata;
}

export interface AgentContext {
  taskId: string;
  instruction: string;
  metadata: Record<string, unknown>;
  sharedState: Record<string, unknown>;
}

export interface TaskResult {
  taskId: string;
  worker: string;
  success: boolean;
  result: Record<string, unknown>;
  durationMs: number;
}

export interface HealthCheckResult {
  workers: WorkerHealth[];
  total: number;
  healthy: number;
  unhealthy: number;
}

export interface WorkerHealth {
  name: string;
  status: 'alive' | 'dead' | 'unknown';
  lastSeenSecondsAgo: number;
}

export interface ExecutionPlan {
  strategy: ExecutionStrategy;
  workers: string[];
  subtasks: Subtask[];
  rationale: string;
}

export interface Subtask {
  worker: string;
  instruction: string;
}

export interface ExecutionResult {
  success: boolean;
  strategy: string;
  workersConsulted?: number;
  workersSuccessful?: number;
  workersFailed?: number;
  synthesis?: string;
  rawResults?: Array<{ worker: string; result: Record<string, unknown> }>;
  error?: string;
}

export interface ToolDefinition {
  name: string;
  description: string;
  input_schema: {
    type: 'object';
    properties: Record<string, unknown>;
    required: string[];
  };
}
