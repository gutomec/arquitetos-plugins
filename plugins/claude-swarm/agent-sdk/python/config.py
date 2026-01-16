"""
Claude Swarm - Configuration
Configuracoes centralizadas para o sistema de swarm.
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class SwarmConfig(BaseSettings):
    """Configuracoes do Swarm."""

    # Redis
    redis_host: str = Field(default="localhost", alias="SWARM_REDIS_HOST")
    redis_port: int = Field(default=6379, alias="SWARM_REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="SWARM_REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="SWARM_REDIS_DB")

    # Agent
    agent_id: str = Field(default="unknown", alias="SWARM_AGENT_ID")
    agent_type: str = Field(default="worker", alias="SWARM_AGENT_TYPE")

    # Anthropic
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-sonnet-4-20250514", alias="CLAUDE_MODEL")
    orchestrator_model: str = Field(default="claude-opus-4-5-20251101", alias="ORCHESTRATOR_MODEL")

    # Timeouts
    task_timeout: int = Field(default=300000, alias="SWARM_TASK_TIMEOUT")  # 5 min
    collect_timeout: int = Field(default=30, alias="SWARM_COLLECT_TIMEOUT")  # 30 sec
    heartbeat_interval: int = Field(default=10, alias="SWARM_HEARTBEAT_INTERVAL")  # 10 sec
    heartbeat_ttl: int = Field(default=60, alias="SWARM_HEARTBEAT_TTL")  # 60 sec

    # Swarm
    max_workers: int = Field(default=10, alias="SWARM_MAX_WORKERS")
    checkpoint_interval: int = Field(default=60000, alias="SWARM_CHECKPOINT_INTERVAL")

    # Logging
    log_level: str = Field(default="INFO", alias="SWARM_LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def redis_url(self) -> str:
        """Constroi URL de conexao Redis."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


class AgentConfig(BaseSettings):
    """Configuracoes especificas de cada tipo de agente."""

    # Worker types e suas configuracoes
    WORKER_CONFIGS = {
        "orchestrator": {
            "model": "claude-opus-4-5-20251101",
            "max_tokens": 8192,
            "temperature": 0.7,
            "tools": ["swarm_publish", "swarm_collect", "swarm_broadcast", "swarm_health_check", "swarm_state_set", "swarm_state_get"]
        },
        "analyst": {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "temperature": 0.5,
            "tools": ["swarm_state_get", "swarm_store_result", "read_file", "search_code"]
        },
        "coder": {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 8192,
            "temperature": 0.3,
            "tools": ["swarm_state_get", "swarm_store_result", "read_file", "write_file", "edit_file"]
        },
        "reviewer": {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "temperature": 0.4,
            "tools": ["swarm_state_get", "swarm_store_result", "read_file", "search_code"]
        },
        "tester": {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "temperature": 0.2,
            "tools": ["swarm_state_get", "swarm_store_result", "read_file", "write_file", "run_command"]
        },
        "researcher": {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "temperature": 0.6,
            "tools": ["swarm_state_get", "swarm_store_result", "web_search", "web_fetch"]
        }
    }

    @classmethod
    def get_config(cls, agent_type: str) -> dict:
        """Retorna configuracao para um tipo de agente."""
        return cls.WORKER_CONFIGS.get(agent_type, cls.WORKER_CONFIGS["analyst"])


# Instancia global
config = SwarmConfig()
agent_config = AgentConfig()
