"""
Database Models - Auto-creating PostgreSQL Schema
==================================================
Modelos SQLAlchemy com auto-criação de tabelas.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid
import logging

from sqlalchemy import (
    create_engine, Column, String, Text, Boolean, DateTime, Integer,
    ForeignKey, Enum as SQLEnum, JSON, BigInteger, Index
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

from .config import get_config

logger = logging.getLogger(__name__)

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class KBVisibility(str, Enum):
    """Visibility levels for knowledge bases."""
    PRIVATE = "private"   # Only owner's agents can access
    GLOBAL = "global"     # All agents can access


class FileStatus(str, Enum):
    """Processing status for files."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileType(str, Enum):
    """Supported file types."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    MD = "md"
    TXT = "txt"
    ZIP = "zip"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    OTHER = "other"


# ============================================================================
# MODELS
# ============================================================================

class User(Base):
    """User model for multi-tenancy."""
    __tablename__ = "kb_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), unique=True, index=True)  # ID from parent system
    name = Column(String(255))
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    knowledge_bases = relationship("KnowledgeBase", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.external_id}>"


class KnowledgeBase(Base):
    """Knowledge base model."""
    __tablename__ = "kb_knowledge_bases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    visibility = Column(SQLEnum(KBVisibility), default=KBVisibility.PRIVATE)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("kb_users.id", ondelete="CASCADE"), nullable=False)

    # Configuration
    embedding_provider = Column(String(50), default="google")
    chunk_size = Column(Integer, default=512)
    chunk_overlap = Column(Integer, default=50)

    # Storage references
    milvus_collection = Column(String(255), unique=True)

    # Statistics (updated on file changes)
    file_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    total_size_bytes = Column(BigInteger, default=0)

    # Metadata
    tags = Column(ARRAY(String), default=[])
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="knowledge_bases")
    files = relationship("KBFile", back_populates="knowledge_base", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_kb_owner_visibility", "owner_id", "visibility"),
        Index("ix_kb_visibility", "visibility"),
    )

    def __repr__(self):
        return f"<KnowledgeBase {self.name}>"

    @staticmethod
    def generate_collection_name(kb_id: uuid.UUID) -> str:
        """Generate a valid Milvus collection name."""
        return f"kb_{str(kb_id).replace('-', '_')}"


class KBFile(Base):
    """File model for uploaded documents."""
    __tablename__ = "kb_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("kb_knowledge_bases.id", ondelete="CASCADE"), nullable=False)

    # File info
    filename = Column(String(512), nullable=False)
    original_filename = Column(String(512), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    mime_type = Column(String(255))
    size_bytes = Column(BigInteger, default=0)

    # Storage
    minio_bucket = Column(String(255), default="knowledge-base")
    minio_object_key = Column(String(1024))

    # Processing status
    status = Column(SQLEnum(FileStatus), default=FileStatus.PENDING)
    error_message = Column(Text)
    processed_at = Column(DateTime(timezone=True))

    # Results
    chunk_count = Column(Integer, default=0)
    entity_count = Column(Integer, default=0)
    text_preview = Column(Text)  # First 500 chars

    # For ZIP contents
    parent_file_id = Column(UUID(as_uuid=True), ForeignKey("kb_files.id", ondelete="CASCADE"))
    is_from_zip = Column(Boolean, default=False)

    # Metadata
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="files")
    chunks = relationship("KBChunk", back_populates="file", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_file_kb_status", "knowledge_base_id", "status"),
    )

    def __repr__(self):
        return f"<KBFile {self.filename}>"


class KBChunk(Base):
    """Chunk model for tracking processed chunks."""
    __tablename__ = "kb_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("kb_files.id", ondelete="CASCADE"), nullable=False)

    # Chunk info
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64))

    # Vector reference
    milvus_id = Column(String(255))

    # Graph reference
    neo4j_node_id = Column(String(255))

    # Metadata
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    file = relationship("KBFile", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunk_file", "file_id"),
        Index("ix_chunk_milvus", "milvus_id"),
    )


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """
    Manages database connections and auto-initialization.

    Usage:
        db = DatabaseManager()
        db.initialize()  # Auto-creates tables

        with db.session() as session:
            # Use session
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_engine'):
            config = get_config()
            self._engine = create_engine(
                config.postgres_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )

    def initialize(self) -> bool:
        """
        Create all tables if they don't exist.
        Safe to call multiple times.
        """
        if DatabaseManager._initialized:
            return True

        try:
            Base.metadata.create_all(bind=self._engine)
            DatabaseManager._initialized = True
            logger.info("Database tables created/verified successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    def session(self):
        """Get a database session context manager."""
        return self._SessionLocal()

    def get_session(self):
        """Get a new session (caller must close)."""
        return self._SessionLocal()

    @property
    def engine(self):
        return self._engine

    def health_check(self) -> dict:
        """Check database health."""
        try:
            from sqlalchemy import text
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


def get_db() -> DatabaseManager:
    """Get the database manager singleton."""
    return DatabaseManager()
