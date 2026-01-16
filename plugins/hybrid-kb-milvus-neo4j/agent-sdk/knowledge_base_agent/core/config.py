"""
Configuration - Auto-initialization and Connection Management
==============================================================
Gerencia conexões e auto-inicialização de toda a infraestrutura.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class KBConfig:
    """
    Configuração centralizada do Knowledge Base Agent.

    Todas as conexões são configuradas via variáveis de ambiente ou parâmetros.
    A infraestrutura é auto-inicializada no primeiro uso.
    """

    # PostgreSQL
    postgres_url: str = field(
        default_factory=lambda: os.getenv(
            "KB_POSTGRES_URL",
            os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/knowledge_base")
        )
    )

    # Milvus
    milvus_uri: str = field(
        default_factory=lambda: os.getenv("KB_MILVUS_URI", os.getenv("MILVUS_URI", "http://localhost:19530"))
    )

    # Neo4j
    neo4j_uri: str = field(
        default_factory=lambda: os.getenv("KB_NEO4J_URI", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    )
    neo4j_user: str = field(
        default_factory=lambda: os.getenv("KB_NEO4J_USER", os.getenv("NEO4J_USER", "neo4j"))
    )
    neo4j_pass: str = field(
        default_factory=lambda: os.getenv("KB_NEO4J_PASS", os.getenv("NEO4J_PASS", "password"))
    )
    neo4j_database: str = field(
        default_factory=lambda: os.getenv("KB_NEO4J_DATABASE", os.getenv("NEO4J_DATABASE", "neo4j"))
    )

    # Minio
    minio_endpoint: str = field(
        default_factory=lambda: os.getenv("KB_MINIO_ENDPOINT", os.getenv("MINIO_ENDPOINT", "localhost:9000"))
    )
    minio_access_key: str = field(
        default_factory=lambda: os.getenv("KB_MINIO_ACCESS_KEY", os.getenv("MINIO_ACCESS_KEY", "minioadmin"))
    )
    minio_secret_key: str = field(
        default_factory=lambda: os.getenv("KB_MINIO_SECRET_KEY", os.getenv("MINIO_SECRET_KEY", "minioadmin"))
    )
    minio_secure: bool = field(
        default_factory=lambda: os.getenv("KB_MINIO_SECURE", "false").lower() == "true"
    )
    minio_bucket: str = field(
        default_factory=lambda: os.getenv("KB_MINIO_BUCKET", "knowledge-base")
    )

    # Redis (optional, for caching)
    redis_url: str = field(
        default_factory=lambda: os.getenv("KB_REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379"))
    )

    # Embeddings
    google_api_key: str = field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY", "")
    )
    cohere_api_key: str = field(
        default_factory=lambda: os.getenv("COHERE_API_KEY", "")
    )
    default_embedding_provider: str = field(
        default_factory=lambda: os.getenv("KB_EMBEDDING_PROVIDER", "google")
    )

    # Claude API
    anthropic_api_key: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    claude_model: str = field(
        default_factory=lambda: os.getenv("KB_CLAUDE_MODEL", "claude-sonnet-4-20250514")
    )

    # Processing
    default_chunk_size: int = 512
    default_chunk_overlap: int = 50
    max_file_size_mb: int = 100

    # Auto-initialization
    auto_init: bool = True
    _initialized: bool = field(default=False, repr=False)

    def __post_init__(self):
        """Validate configuration on creation."""
        if not self.google_api_key and not self.cohere_api_key:
            logger.warning("No embedding API key configured. Set GOOGLE_API_KEY or COHERE_API_KEY.")

    def validate(self) -> dict:
        """Validate all connections and return status."""
        status = {
            "postgres": self._check_postgres(),
            "milvus": self._check_milvus(),
            "neo4j": self._check_neo4j(),
            "minio": self._check_minio(),
            "redis": self._check_redis(),
            "embeddings": self._check_embeddings()
        }
        return status

    def _check_postgres(self) -> dict:
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(self.postgres_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "healthy", "url": self.postgres_url.split("@")[-1]}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_milvus(self) -> dict:
        try:
            from pymilvus import MilvusClient
            client = MilvusClient(uri=self.milvus_uri)
            client.list_collections()
            return {"status": "healthy", "uri": self.milvus_uri}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_neo4j(self) -> dict:
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_pass))
            with driver.session(database=self.neo4j_database) as session:
                session.run("RETURN 1")
            driver.close()
            return {"status": "healthy", "uri": self.neo4j_uri}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_minio(self) -> dict:
        try:
            from minio import Minio
            client = Minio(
                self.minio_endpoint,
                access_key=self.minio_access_key,
                secret_key=self.minio_secret_key,
                secure=self.minio_secure
            )
            client.list_buckets()
            return {"status": "healthy", "endpoint": self.minio_endpoint}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_redis(self) -> dict:
        try:
            import redis
            r = redis.from_url(self.redis_url)
            r.ping()
            return {"status": "healthy", "url": self.redis_url.split("@")[-1] if "@" in self.redis_url else self.redis_url}
        except Exception as e:
            return {"status": "unavailable", "note": "Redis is optional", "error": str(e)}

    def _check_embeddings(self) -> dict:
        providers = []
        if self.google_api_key:
            providers.append("google")
        if self.cohere_api_key:
            providers.append("cohere")
        return {
            "status": "healthy" if providers else "warning",
            "providers": providers,
            "default": self.default_embedding_provider
        }


@lru_cache()
def get_config() -> KBConfig:
    """Get singleton configuration instance."""
    return KBConfig()
