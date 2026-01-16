#!/usr/bin/env python3
"""
Claude Swarm MCP Server
Servidor MCP para comunicacao entre agentes Claude em containers.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Any, Optional

import redis.asyncio as redis
from mcp import Server
from mcp.types import Tool, TextContent

# Configuracao
REDIS_HOST = os.getenv("SWARM_REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("SWARM_REDIS_PORT", "6379"))
AGENT_ID = os.getenv("SWARM_AGENT_ID", "unknown")

# Servidor MCP
server = Server("swarm-communication")

# Cliente Redis (inicializado lazy)
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Obtem cliente Redis, criando se necessario."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
    return _redis_client


def generate_message_id() -> str:
    """Gera ID unico para mensagem."""
    return str(uuid.uuid4())


def create_message(
    msg_type: str,
    to: str,
    payload: dict,
    priority: str = "medium"
) -> dict:
    """Cria mensagem no formato padrao do Swarm."""
    return {
        "type": msg_type,
        "id": generate_message_id(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "from": AGENT_ID,
        "to": to,
        "payload": payload,
        "metadata": {
            "priority": priority,
            "ttl": 300000  # 5 minutos
        }
    }


# =============================================================================
# TOOLS
# =============================================================================

@server.tool()
async def swarm_publish(
    channel: str,
    message_type: str,
    payload: str,
    priority: str = "medium"
) -> str:
    """
    Publica mensagem para um worker ou canal do Swarm.

    Args:
        channel: Nome do canal ou worker (ex: "analyst", "broadcast")
        message_type: Tipo da mensagem (TASK, RESULT, BROADCAST, STATUS)
        payload: Payload JSON da mensagem
        priority: Prioridade (high, medium, low)

    Returns:
        ID da mensagem publicada
    """
    try:
        payload_dict = json.loads(payload)
    except json.JSONDecodeError:
        return json.dumps({"error": "Payload deve ser JSON valido"})

    message = create_message(message_type, channel, payload_dict, priority)

    r = await get_redis()

    if channel == "broadcast" or channel == "*":
        redis_channel = "swarm:broadcast"
    else:
        redis_channel = f"swarm:tasks:{channel}"

    await r.publish(redis_channel, json.dumps(message))

    # Salvar referencia para coleta posterior
    await r.setex(
        f"swarm:pending:{message['id']}",
        300,  # 5 minutos TTL
        json.dumps({"channel": channel, "status": "pending"})
    )

    return json.dumps({
        "success": True,
        "message_id": message["id"],
        "channel": redis_channel
    })


@server.tool()
async def swarm_collect(
    task_id: str,
    timeout_seconds: int = 30
) -> str:
    """
    Coleta resultado de uma tarefa enviada anteriormente.

    Args:
        task_id: ID da tarefa/mensagem
        timeout_seconds: Timeout em segundos (default: 30)

    Returns:
        Resultado da tarefa ou erro de timeout
    """
    r = await get_redis()
    result_key = f"swarm:results:{task_id}"

    # Polling com timeout
    start_time = asyncio.get_event_loop().time()
    while True:
        result = await r.get(result_key)
        if result:
            # Limpar resultado apos coleta
            await r.delete(result_key)
            return result

        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout_seconds:
            return json.dumps({
                "error": "timeout",
                "message": f"Timeout aguardando resultado de {task_id}",
                "elapsed_seconds": elapsed
            })

        await asyncio.sleep(0.5)


@server.tool()
async def swarm_state_set(
    key: str,
    value: str,
    ttl_seconds: Optional[int] = None
) -> str:
    """
    Salva estado compartilhado no Swarm.

    Args:
        key: Chave do estado
        value: Valor (string ou JSON)
        ttl_seconds: Tempo de vida em segundos (opcional)

    Returns:
        Confirmacao de sucesso
    """
    r = await get_redis()
    full_key = f"swarm:state:{key}"

    if ttl_seconds:
        await r.setex(full_key, ttl_seconds, value)
    else:
        await r.set(full_key, value)

    return json.dumps({"success": True, "key": key})


@server.tool()
async def swarm_state_get(key: str) -> str:
    """
    Recupera estado compartilhado do Swarm.

    Args:
        key: Chave do estado

    Returns:
        Valor armazenado ou null se nao existir
    """
    r = await get_redis()
    full_key = f"swarm:state:{key}"
    value = await r.get(full_key)

    return json.dumps({
        "key": key,
        "value": value,
        "exists": value is not None
    })


@server.tool()
async def swarm_health_check() -> str:
    """
    Verifica saude de todos os workers do Swarm.

    Returns:
        Status de cada worker registrado
    """
    r = await get_redis()
    workers = []

    # Buscar todos os heartbeats
    keys = await r.keys("swarm:heartbeat:*")
    now = datetime.utcnow().timestamp()

    for key in keys:
        worker_name = key.replace("swarm:heartbeat:", "")
        last_seen = await r.get(key)

        if last_seen:
            age_seconds = int(now - float(last_seen))
            status = "alive" if age_seconds < 30 else "dead"
        else:
            age_seconds = -1
            status = "unknown"

        workers.append({
            "name": worker_name,
            "status": status,
            "last_seen_seconds_ago": age_seconds
        })

    return json.dumps({
        "workers": workers,
        "total": len(workers),
        "healthy": sum(1 for w in workers if w["status"] == "alive"),
        "unhealthy": sum(1 for w in workers if w["status"] != "alive")
    })


@server.tool()
async def swarm_heartbeat() -> str:
    """
    Envia heartbeat para registrar que este agente esta ativo.

    Returns:
        Confirmacao de heartbeat
    """
    r = await get_redis()
    key = f"swarm:heartbeat:{AGENT_ID}"
    timestamp = datetime.utcnow().timestamp()

    await r.setex(key, 60, str(timestamp))  # TTL de 60 segundos

    return json.dumps({
        "success": True,
        "agent": AGENT_ID,
        "timestamp": timestamp
    })


@server.tool()
async def swarm_broadcast(
    action: str,
    message: str = ""
) -> str:
    """
    Envia broadcast para todos os workers do Swarm.

    Args:
        action: Acao (pause, resume, status, shutdown, context)
        message: Mensagem adicional opcional

    Returns:
        Confirmacao de broadcast
    """
    payload = {
        "action": action,
        "message": message
    }

    msg = create_message("BROADCAST", "*", payload, "high")

    r = await get_redis()
    await r.publish("swarm:broadcast", json.dumps(msg))

    return json.dumps({
        "success": True,
        "message_id": msg["id"],
        "action": action,
        "recipients": "all"
    })


@server.tool()
async def swarm_subscribe_once(
    channel: str,
    timeout_seconds: int = 30
) -> str:
    """
    Aguarda uma mensagem em um canal (blocking).

    Args:
        channel: Canal para escutar (ex: "results", "broadcast")
        timeout_seconds: Timeout em segundos

    Returns:
        Primeira mensagem recebida ou timeout
    """
    r = await get_redis()
    pubsub = r.pubsub()

    if channel == "results":
        redis_channel = f"swarm:results:{AGENT_ID}"
    elif channel == "tasks":
        redis_channel = f"swarm:tasks:{AGENT_ID}"
    else:
        redis_channel = f"swarm:{channel}"

    await pubsub.subscribe(redis_channel)

    try:
        start_time = asyncio.get_event_loop().time()
        async for message in pubsub.listen():
            if message["type"] == "message":
                await pubsub.unsubscribe(redis_channel)
                return message["data"]

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout_seconds:
                await pubsub.unsubscribe(redis_channel)
                return json.dumps({
                    "error": "timeout",
                    "channel": redis_channel
                })
    finally:
        await pubsub.close()


@server.tool()
async def swarm_list_pending_tasks() -> str:
    """
    Lista todas as tarefas pendentes no Swarm.

    Returns:
        Lista de tarefas pendentes
    """
    r = await get_redis()
    keys = await r.keys("swarm:pending:*")

    tasks = []
    for key in keys:
        task_id = key.replace("swarm:pending:", "")
        data = await r.get(key)
        if data:
            task_data = json.loads(data)
            tasks.append({
                "id": task_id,
                **task_data
            })

    return json.dumps({
        "pending_tasks": tasks,
        "count": len(tasks)
    })


@server.tool()
async def swarm_store_result(
    task_id: str,
    result: str,
    status: str = "success"
) -> str:
    """
    Armazena resultado de uma tarefa para coleta pelo orchestrator.

    Args:
        task_id: ID da tarefa original
        result: Resultado (JSON string)
        status: Status (success, partial, failed)

    Returns:
        Confirmacao de armazenamento
    """
    try:
        result_dict = json.loads(result)
    except json.JSONDecodeError:
        result_dict = {"raw": result}

    message = create_message("RESULT", "orchestrator", {
        "status": status,
        "result": result_dict
    })
    message["id"] = task_id  # Usar mesmo ID da tarefa

    r = await get_redis()
    result_key = f"swarm:results:{task_id}"

    await r.setex(result_key, 300, json.dumps(message))

    # Publicar notificacao
    await r.publish("swarm:results:orchestrator", json.dumps(message))

    # Remover de pendentes
    await r.delete(f"swarm:pending:{task_id}")

    return json.dumps({
        "success": True,
        "task_id": task_id,
        "stored_at": result_key
    })


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Inicia o servidor MCP."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
