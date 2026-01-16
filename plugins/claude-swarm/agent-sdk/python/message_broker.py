"""
Claude Swarm - Message Broker
Sistema de mensageria baseado em Redis para comunicacao entre agentes.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional, Callable, Any, Dict, List
from dataclasses import dataclass, field, asdict
from enum import Enum

import redis.asyncio as redis

from config import config


class MessageType(str, Enum):
    """Tipos de mensagem do Swarm."""
    TASK = "TASK"
    RESULT = "RESULT"
    BROADCAST = "BROADCAST"
    STATUS = "STATUS"
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"


class Priority(str, Enum):
    """Prioridades de mensagem."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Message:
    """Estrutura de mensagem do Swarm."""
    type: MessageType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    from_agent: str = field(default_factory=lambda: config.agent_id)
    to_agent: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.metadata:
            self.metadata = {
                "priority": Priority.MEDIUM.value,
                "ttl": 300000  # 5 minutos
            }

    def to_json(self) -> str:
        """Serializa mensagem para JSON."""
        data = {
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "id": self.id,
            "timestamp": self.timestamp,
            "from": self.from_agent,
            "to": self.to_agent,
            "payload": self.payload,
            "metadata": self.metadata
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, data: str) -> "Message":
        """Deserializa mensagem de JSON."""
        parsed = json.loads(data)
        return cls(
            type=MessageType(parsed.get("type", "TASK")),
            id=parsed.get("id", str(uuid.uuid4())),
            timestamp=parsed.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            from_agent=parsed.get("from", "unknown"),
            to_agent=parsed.get("to", ""),
            payload=parsed.get("payload", {}),
            metadata=parsed.get("metadata", {})
        )


class MessageBroker:
    """
    Message Broker para comunicacao entre agentes.
    Usa Redis Pub/Sub para comunicacao em tempo real.
    """

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._subscriptions: Dict[str, Callable] = {}
        self._running = False

    async def connect(self) -> None:
        """Conecta ao Redis."""
        if self._client is None:
            self._client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                db=config.redis_db,
                decode_responses=True
            )
            # Testar conexao
            await self._client.ping()
            print(f"[BROKER] Conectado ao Redis em {config.redis_host}:{config.redis_port}")

    async def disconnect(self) -> None:
        """Desconecta do Redis."""
        self._running = False
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        if self._client:
            await self._client.close()
            self._client = None
        print("[BROKER] Desconectado do Redis")

    async def publish(
        self,
        channel: str,
        message: Message,
    ) -> str:
        """
        Publica mensagem em um canal.

        Args:
            channel: Nome do canal ou worker
            message: Mensagem a publicar

        Returns:
            ID da mensagem publicada
        """
        await self.connect()

        # Determinar canal Redis
        if channel == "broadcast" or channel == "*":
            redis_channel = "swarm:broadcast"
        elif channel == "orchestrator":
            redis_channel = "swarm:results:orchestrator"
        else:
            redis_channel = f"swarm:tasks:{channel}"

        # Publicar
        await self._client.publish(redis_channel, message.to_json())

        # Salvar referencia para coleta
        await self._client.setex(
            f"swarm:pending:{message.id}",
            300,
            json.dumps({"channel": channel, "status": "pending"})
        )

        return message.id

    async def subscribe(
        self,
        channels: List[str],
        callback: Callable[[Message], Any]
    ) -> None:
        """
        Inscreve-se em canais para receber mensagens.

        Args:
            channels: Lista de canais
            callback: Funcao chamada para cada mensagem
        """
        await self.connect()

        if self._pubsub is None:
            self._pubsub = self._client.pubsub()

        # Mapear canais
        redis_channels = []
        for channel in channels:
            if channel == "broadcast":
                redis_channels.append("swarm:broadcast")
            elif channel == "tasks":
                redis_channels.append(f"swarm:tasks:{config.agent_id}")
            elif channel == "results":
                redis_channels.append(f"swarm:results:{config.agent_id}")
            else:
                redis_channels.append(f"swarm:{channel}")

        await self._pubsub.subscribe(*redis_channels)

        for ch in redis_channels:
            self._subscriptions[ch] = callback

        print(f"[BROKER] Inscrito em: {redis_channels}")

    async def listen(self) -> None:
        """Loop de escuta de mensagens."""
        if self._pubsub is None:
            raise RuntimeError("Nao inscrito em nenhum canal")

        self._running = True
        print("[BROKER] Iniciando loop de escuta...")

        async for message in self._pubsub.listen():
            if not self._running:
                break

            if message["type"] == "message":
                channel = message["channel"]
                data = message["data"]

                try:
                    msg = Message.from_json(data)
                    callback = self._subscriptions.get(channel)
                    if callback:
                        await callback(msg)
                except Exception as e:
                    print(f"[BROKER] Erro processando mensagem: {e}")

    async def collect(
        self,
        task_id: str,
        timeout_seconds: int = 30
    ) -> Optional[Message]:
        """
        Coleta resultado de uma tarefa.

        Args:
            task_id: ID da tarefa
            timeout_seconds: Timeout em segundos

        Returns:
            Mensagem de resultado ou None se timeout
        """
        await self.connect()

        result_key = f"swarm:results:{task_id}"
        start_time = asyncio.get_event_loop().time()

        while True:
            result = await self._client.get(result_key)
            if result:
                await self._client.delete(result_key)
                return Message.from_json(result)

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout_seconds:
                return None

            await asyncio.sleep(0.5)

    async def store_result(
        self,
        task_id: str,
        result: Dict[str, Any],
        status: str = "success"
    ) -> None:
        """
        Armazena resultado de uma tarefa.

        Args:
            task_id: ID da tarefa
            result: Resultado
            status: Status (success, partial, failed)
        """
        await self.connect()

        message = Message(
            type=MessageType.RESULT,
            id=task_id,
            to_agent="orchestrator",
            payload={"status": status, "result": result}
        )

        result_key = f"swarm:results:{task_id}"
        await self._client.setex(result_key, 300, message.to_json())

        # Notificar orchestrator
        await self._client.publish("swarm:results:orchestrator", message.to_json())

        # Remover de pendentes
        await self._client.delete(f"swarm:pending:{task_id}")

    async def broadcast(
        self,
        action: str,
        message: str = ""
    ) -> str:
        """
        Envia broadcast para todos os workers.

        Args:
            action: Acao (pause, resume, shutdown, etc)
            message: Mensagem adicional

        Returns:
            ID do broadcast
        """
        msg = Message(
            type=MessageType.BROADCAST,
            to_agent="*",
            payload={"action": action, "message": message},
            metadata={"priority": Priority.HIGH.value, "ttl": 60000}
        )

        await self.publish("broadcast", msg)
        return msg.id

    async def heartbeat(self) -> None:
        """Envia heartbeat para registro de atividade."""
        await self.connect()

        key = f"swarm:heartbeat:{config.agent_id}"
        timestamp = datetime.utcnow().timestamp()
        await self._client.setex(key, config.heartbeat_ttl, str(timestamp))

    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica saude de todos os workers.

        Returns:
            Status de cada worker
        """
        await self.connect()

        workers = []
        keys = await self._client.keys("swarm:heartbeat:*")
        now = datetime.utcnow().timestamp()

        for key in keys:
            worker_name = key.replace("swarm:heartbeat:", "")
            last_seen = await self._client.get(key)

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

        return {
            "workers": workers,
            "total": len(workers),
            "healthy": sum(1 for w in workers if w["status"] == "alive"),
            "unhealthy": sum(1 for w in workers if w["status"] != "alive")
        }

    async def set_state(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Salva estado compartilhado.

        Args:
            key: Chave
            value: Valor
            ttl_seconds: TTL opcional
        """
        await self.connect()

        full_key = f"swarm:state:{key}"
        value_str = json.dumps(value) if not isinstance(value, str) else value

        if ttl_seconds:
            await self._client.setex(full_key, ttl_seconds, value_str)
        else:
            await self._client.set(full_key, value_str)

    async def get_state(self, key: str) -> Optional[Any]:
        """
        Recupera estado compartilhado.

        Args:
            key: Chave

        Returns:
            Valor ou None
        """
        await self.connect()

        full_key = f"swarm:state:{key}"
        value = await self._client.get(full_key)

        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None


# Instancia global
broker = MessageBroker()
