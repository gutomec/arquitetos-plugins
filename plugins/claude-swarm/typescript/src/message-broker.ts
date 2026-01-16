/**
 * Claude Swarm - Message Broker
 * Sistema de mensageria baseado em Redis para comunicacao entre agentes.
 */

import Redis from 'ioredis';
import { v4 as uuidv4 } from 'uuid';
import { config } from './config';
import { Message, MessageType, Priority, HealthCheckResult } from './types';

export class MessageBroker {
  private client: Redis | null = null;
  private subscriber: Redis | null = null;
  private subscriptions: Map<string, (message: Message) => void> = new Map();
  private running = false;

  async connect(): Promise<void> {
    if (this.client) return;

    const redisConfig = {
      host: config.redisHost,
      port: config.redisPort,
      password: config.redisPassword,
      db: config.redisDb,
    };

    this.client = new Redis(redisConfig);
    this.subscriber = new Redis(redisConfig);

    await this.client.ping();
    console.log(`[BROKER] Conectado ao Redis em ${config.redisHost}:${config.redisPort}`);
  }

  async disconnect(): Promise<void> {
    this.running = false;
    if (this.subscriber) {
      await this.subscriber.quit();
      this.subscriber = null;
    }
    if (this.client) {
      await this.client.quit();
      this.client = null;
    }
    console.log('[BROKER] Desconectado do Redis');
  }

  createMessage(
    type: MessageType,
    to: string,
    payload: Record<string, unknown>,
    priority: Priority = Priority.MEDIUM
  ): Message {
    return {
      type,
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      from: config.agentId,
      to,
      payload,
      metadata: {
        priority,
        ttl: 300000, // 5 minutos
      },
    };
  }

  async publish(channel: string, message: Message): Promise<string> {
    await this.connect();

    // Determinar canal Redis
    let redisChannel: string;
    if (channel === 'broadcast' || channel === '*') {
      redisChannel = 'swarm:broadcast';
    } else if (channel === 'orchestrator') {
      redisChannel = 'swarm:results:orchestrator';
    } else {
      redisChannel = `swarm:tasks:${channel}`;
    }

    // Publicar
    await this.client!.publish(redisChannel, JSON.stringify(message));

    // Salvar referencia para coleta
    await this.client!.setex(
      `swarm:pending:${message.id}`,
      300,
      JSON.stringify({ channel, status: 'pending' })
    );

    return message.id;
  }

  async subscribe(
    channels: string[],
    callback: (message: Message) => void
  ): Promise<void> {
    await this.connect();

    // Mapear canais
    const redisChannels = channels.map((channel) => {
      if (channel === 'broadcast') return 'swarm:broadcast';
      if (channel === 'tasks') return `swarm:tasks:${config.agentId}`;
      if (channel === 'results') return `swarm:results:${config.agentId}`;
      return `swarm:${channel}`;
    });

    for (const ch of redisChannels) {
      this.subscriptions.set(ch, callback);
    }

    await this.subscriber!.subscribe(...redisChannels);
    console.log(`[BROKER] Inscrito em: ${redisChannels.join(', ')}`);
  }

  async listen(): Promise<void> {
    if (!this.subscriber) {
      throw new Error('Nao inscrito em nenhum canal');
    }

    this.running = true;
    console.log('[BROKER] Iniciando loop de escuta...');

    this.subscriber.on('message', (channel, data) => {
      if (!this.running) return;

      try {
        const message: Message = JSON.parse(data);
        const callback = this.subscriptions.get(channel);
        if (callback) {
          callback(message);
        }
      } catch (e) {
        console.error(`[BROKER] Erro processando mensagem: ${e}`);
      }
    });
  }

  async collect(taskId: string, timeoutSeconds: number = 30): Promise<Message | null> {
    await this.connect();

    const resultKey = `swarm:results:${taskId}`;
    const startTime = Date.now();

    while (true) {
      const result = await this.client!.get(resultKey);
      if (result) {
        await this.client!.del(resultKey);
        return JSON.parse(result);
      }

      const elapsed = (Date.now() - startTime) / 1000;
      if (elapsed >= timeoutSeconds) {
        return null;
      }

      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }

  async storeResult(
    taskId: string,
    result: Record<string, unknown>,
    status: string = 'success'
  ): Promise<void> {
    await this.connect();

    const message = this.createMessage(
      MessageType.RESULT,
      'orchestrator',
      { status, result }
    );
    message.id = taskId;

    const resultKey = `swarm:results:${taskId}`;
    await this.client!.setex(resultKey, 300, JSON.stringify(message));

    // Notificar orchestrator
    await this.client!.publish('swarm:results:orchestrator', JSON.stringify(message));

    // Remover de pendentes
    await this.client!.del(`swarm:pending:${taskId}`);
  }

  async broadcast(action: string, message: string = ''): Promise<string> {
    const msg = this.createMessage(
      MessageType.BROADCAST,
      '*',
      { action, message },
      Priority.HIGH
    );

    await this.publish('broadcast', msg);
    return msg.id;
  }

  async heartbeat(): Promise<void> {
    await this.connect();

    const key = `swarm:heartbeat:${config.agentId}`;
    const timestamp = Date.now() / 1000;
    await this.client!.setex(key, config.heartbeatTtl, timestamp.toString());
  }

  async healthCheck(): Promise<HealthCheckResult> {
    await this.connect();

    const workers: HealthCheckResult['workers'] = [];
    const keys = await this.client!.keys('swarm:heartbeat:*');
    const now = Date.now() / 1000;

    for (const key of keys) {
      const workerName = key.replace('swarm:heartbeat:', '');
      const lastSeen = await this.client!.get(key);

      let ageSeconds: number;
      let status: 'alive' | 'dead' | 'unknown';

      if (lastSeen) {
        ageSeconds = Math.floor(now - parseFloat(lastSeen));
        status = ageSeconds < 30 ? 'alive' : 'dead';
      } else {
        ageSeconds = -1;
        status = 'unknown';
      }

      workers.push({
        name: workerName,
        status,
        lastSeenSecondsAgo: ageSeconds,
      });
    }

    return {
      workers,
      total: workers.length,
      healthy: workers.filter((w) => w.status === 'alive').length,
      unhealthy: workers.filter((w) => w.status !== 'alive').length,
    };
  }

  async setState(
    key: string,
    value: unknown,
    ttlSeconds?: number
  ): Promise<void> {
    await this.connect();

    const fullKey = `swarm:state:${key}`;
    const valueStr = typeof value === 'string' ? value : JSON.stringify(value);

    if (ttlSeconds) {
      await this.client!.setex(fullKey, ttlSeconds, valueStr);
    } else {
      await this.client!.set(fullKey, valueStr);
    }
  }

  async getState(key: string): Promise<unknown | null> {
    await this.connect();

    const fullKey = `swarm:state:${key}`;
    const value = await this.client!.get(fullKey);

    if (value) {
      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    }
    return null;
  }
}

// Instancia global
export const broker = new MessageBroker();
