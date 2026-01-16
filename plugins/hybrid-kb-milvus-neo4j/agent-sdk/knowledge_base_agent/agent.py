"""
Knowledge Base Agent - Main Subagent Class
===========================================
Agente self-contained que pode ser usado como subagente em qualquer sistema.
"""

import anthropic
from typing import Optional, List, Any, Dict, Union
from uuid import UUID
import uuid
import json
import logging
import hashlib
from datetime import datetime

from .core.config import KBConfig, get_config
from .core.models import (
    DatabaseManager, get_db, User, KnowledgeBase, KBFile, KBChunk,
    KBVisibility, FileStatus, FileType
)
from .storage import StorageManager
from .processing import FileProcessor, EmbeddingService, GraphService

logger = logging.getLogger(__name__)


# ============================================================================
# TOOL DEFINITIONS (for parent agents)
# ============================================================================

KB_TOOL_DEFINITIONS = [
    {
        "name": "kb_create",
        "description": "Create a new knowledge base for storing and searching documents. Returns the created KB with its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the knowledge base"},
                "description": {"type": "string", "description": "Optional description"},
                "visibility": {"type": "string", "enum": ["private", "global"], "default": "private",
                              "description": "private = only owner can access, global = all users can access"},
                "user_id": {"type": "string", "description": "User ID (external ID from parent system)"},
                "embedding_provider": {"type": "string", "enum": ["google", "cohere"], "default": "google"}
            },
            "required": ["name", "user_id"]
        }
    },
    {
        "name": "kb_list",
        "description": "List knowledge bases accessible to a user. Returns both owned and global KBs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User ID to list KBs for"},
                "include_global": {"type": "boolean", "default": True, "description": "Include global KBs"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "kb_delete",
        "description": "Delete a knowledge base and all its files. Removes data from Milvus, Neo4j, Minio, and PostgreSQL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "kb_id": {"type": "string", "description": "Knowledge base ID to delete"},
                "user_id": {"type": "string", "description": "User ID (must be owner)"}
            },
            "required": ["kb_id", "user_id"]
        }
    },
    {
        "name": "kb_upload_file",
        "description": "Upload a file to a knowledge base. Supports PDF, DOCX, XLSX, PPTX, MD, TXT, CSV, JSON, HTML, and ZIP files. ZIP files are automatically extracted.",
        "input_schema": {
            "type": "object",
            "properties": {
                "kb_id": {"type": "string", "description": "Knowledge base ID"},
                "filename": {"type": "string", "description": "Name of the file"},
                "content_base64": {"type": "string", "description": "File content as base64 string"},
                "user_id": {"type": "string", "description": "User ID (must have access to KB)"}
            },
            "required": ["kb_id", "filename", "content_base64", "user_id"]
        }
    },
    {
        "name": "kb_upload_from_url",
        "description": "Upload a file to a knowledge base from a URL (e.g., Minio presigned URL).",
        "input_schema": {
            "type": "object",
            "properties": {
                "kb_id": {"type": "string", "description": "Knowledge base ID"},
                "filename": {"type": "string", "description": "Name to give the file"},
                "url": {"type": "string", "description": "URL to download the file from"},
                "user_id": {"type": "string", "description": "User ID"}
            },
            "required": ["kb_id", "filename", "url", "user_id"]
        }
    },
    {
        "name": "kb_list_files",
        "description": "List files in a knowledge base.",
        "input_schema": {
            "type": "object",
            "properties": {
                "kb_id": {"type": "string", "description": "Knowledge base ID"},
                "user_id": {"type": "string", "description": "User ID"},
                "status": {"type": "string", "enum": ["pending", "processing", "completed", "failed"],
                          "description": "Filter by status"}
            },
            "required": ["kb_id", "user_id"]
        }
    },
    {
        "name": "kb_delete_file",
        "description": "Delete a file from a knowledge base. Removes vectors from Milvus and nodes from Neo4j.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_id": {"type": "string", "description": "File ID to delete"},
                "user_id": {"type": "string", "description": "User ID"}
            },
            "required": ["file_id", "user_id"]
        }
    },
    {
        "name": "kb_search",
        "description": "Search across knowledge bases using semantic, graph, or hybrid search. Returns relevant chunks with scores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "user_id": {"type": "string", "description": "User ID"},
                "kb_ids": {"type": "array", "items": {"type": "string"},
                          "description": "Specific KB IDs to search (optional, searches all accessible if not provided)"},
                "top_k": {"type": "integer", "default": 10, "description": "Number of results to return"},
                "search_type": {"type": "string", "enum": ["vector", "graph", "hybrid"], "default": "hybrid"}
            },
            "required": ["query", "user_id"]
        }
    },
    {
        "name": "kb_get_upload_url",
        "description": "Get a presigned URL for uploading a file directly to storage. Use this for large files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "kb_id": {"type": "string", "description": "Knowledge base ID"},
                "filename": {"type": "string", "description": "Name of the file"},
                "user_id": {"type": "string", "description": "User ID"}
            },
            "required": ["kb_id", "filename", "user_id"]
        }
    },
    {
        "name": "kb_process_file",
        "description": "Trigger processing of an uploaded file (chunking, embedding, indexing). Called after upload via presigned URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_id": {"type": "string", "description": "File ID to process"},
                "user_id": {"type": "string", "description": "User ID"}
            },
            "required": ["file_id", "user_id"]
        }
    },
    {
        "name": "kb_health",
        "description": "Check health of all KB infrastructure components.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


def get_kb_tools() -> List[dict]:
    """Get tool definitions for use in parent agents."""
    return KB_TOOL_DEFINITIONS


# ============================================================================
# KNOWLEDGE BASE AGENT
# ============================================================================

class KnowledgeBaseAgent:
    """
    Self-contained Knowledge Base Agent.

    Can be used as:
    1. A subagent (call .run() with natural language)
    2. Direct API (call methods like .create_knowledge_base())
    3. Tool provider (use get_kb_tools() in parent agent)

    Auto-initializes all infrastructure on first use.
    """

    def __init__(
        self,
        config: KBConfig = None,
        api_key: str = None,
        auto_init: bool = True
    ):
        self.config = config or get_config()
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self._initialized = False

        # Services (lazy init)
        self._db: Optional[DatabaseManager] = None
        self._storage: Optional[StorageManager] = None
        self._processor: Optional[FileProcessor] = None
        self._embeddings: Optional[EmbeddingService] = None
        self._graph: Optional[GraphService] = None

        if auto_init:
            self.initialize()

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def initialize(self) -> bool:
        """
        Initialize all infrastructure.
        Creates database tables, Minio buckets, etc.
        Safe to call multiple times.
        """
        if self._initialized:
            return True

        try:
            logger.info("Initializing Knowledge Base Agent infrastructure...")

            # Initialize database
            self._db = get_db()
            self._db.initialize()

            # Initialize storage
            self._storage = StorageManager(self.config)

            # Initialize embeddings
            self._embeddings = EmbeddingService(self.config)

            # Initialize graph
            self._graph = GraphService(self.config)

            # Initialize processor
            self._processor = FileProcessor(
                config=self.config,
                storage=self._storage,
                embeddings=self._embeddings,
                graph=self._graph,
                db=self._db
            )

            self._initialized = True
            logger.info("Knowledge Base Agent initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize KB Agent: {e}")
            raise

    def _ensure_initialized(self):
        """Ensure agent is initialized before operations."""
        if not self._initialized:
            self.initialize()

    # =========================================================================
    # USER MANAGEMENT
    # =========================================================================

    def _get_or_create_user(self, external_id: str, name: str = None) -> User:
        """Get or create a user by external ID."""
        self._ensure_initialized()

        session = self._db.get_session()
        try:
            user = session.query(User).filter(User.external_id == external_id).first()
            if not user:
                user = User(
                    external_id=external_id,
                    name=name or external_id
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created user: {external_id}")
            return user
        finally:
            session.close()

    # =========================================================================
    # KNOWLEDGE BASE OPERATIONS
    # =========================================================================

    async def create_knowledge_base(
        self,
        user_id: str,
        name: str,
        description: str = None,
        visibility: str = "private",
        embedding_provider: str = "google",
        tags: List[str] = None,
        metadata: dict = None
    ) -> dict:
        """Create a new knowledge base."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            kb = KnowledgeBase(
                name=name,
                description=description,
                visibility=KBVisibility(visibility),
                owner_id=user.id,
                embedding_provider=embedding_provider,
                chunk_size=self.config.default_chunk_size,
                chunk_overlap=self.config.default_chunk_overlap,
                tags=tags or [],
                metadata=metadata or {}
            )

            # Generate Milvus collection name
            session.add(kb)
            session.flush()  # Get the ID
            kb.milvus_collection = KnowledgeBase.generate_collection_name(kb.id)

            # Create Milvus collection
            await self._embeddings.create_collection(
                kb.milvus_collection,
                kb.embedding_provider
            )

            session.commit()
            session.refresh(kb)

            logger.info(f"Created knowledge base: {name} (ID: {kb.id})")

            return {
                "id": str(kb.id),
                "name": kb.name,
                "description": kb.description,
                "visibility": kb.visibility.value,
                "milvus_collection": kb.milvus_collection,
                "embedding_provider": kb.embedding_provider,
                "created_at": kb.created_at.isoformat()
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create KB: {e}")
            raise
        finally:
            session.close()

    async def list_knowledge_bases(
        self,
        user_id: str,
        include_global: bool = True
    ) -> List[dict]:
        """List knowledge bases accessible to a user."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            query = session.query(KnowledgeBase).filter(
                (KnowledgeBase.owner_id == user.id) |
                (KnowledgeBase.visibility == KBVisibility.GLOBAL if include_global else False)
            )

            kbs = query.all()

            return [{
                "id": str(kb.id),
                "name": kb.name,
                "description": kb.description,
                "visibility": kb.visibility.value,
                "file_count": kb.file_count,
                "chunk_count": kb.chunk_count,
                "total_size_bytes": kb.total_size_bytes,
                "is_owner": kb.owner_id == user.id,
                "created_at": kb.created_at.isoformat()
            } for kb in kbs]
        finally:
            session.close()

    async def delete_knowledge_base(
        self,
        kb_id: str,
        user_id: str
    ) -> dict:
        """Delete a knowledge base and all its data."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            kb = session.query(KnowledgeBase).filter(
                KnowledgeBase.id == UUID(kb_id),
                KnowledgeBase.owner_id == user.id
            ).first()

            if not kb:
                return {"success": False, "error": "Knowledge base not found or access denied"}

            # Delete from Milvus
            try:
                await self._embeddings.delete_collection(kb.milvus_collection)
            except Exception as e:
                logger.warning(f"Failed to delete Milvus collection: {e}")

            # Delete from Neo4j
            try:
                await self._graph.delete_kb_nodes(str(kb.id))
            except Exception as e:
                logger.warning(f"Failed to delete Neo4j nodes: {e}")

            # Delete files from Minio
            try:
                self._storage.delete_kb_files(str(user.id), str(kb.id))
            except Exception as e:
                logger.warning(f"Failed to delete Minio files: {e}")

            # Delete from PostgreSQL (cascades to files and chunks)
            session.delete(kb)
            session.commit()

            logger.info(f"Deleted knowledge base: {kb_id}")

            return {"success": True, "deleted_kb_id": kb_id}
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete KB: {e}")
            raise
        finally:
            session.close()

    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================

    async def upload_file(
        self,
        kb_id: str,
        user_id: str,
        filename: str,
        content: bytes,
        process_immediately: bool = True
    ) -> dict:
        """Upload and optionally process a file."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            # Verify access to KB
            kb = session.query(KnowledgeBase).filter(
                KnowledgeBase.id == UUID(kb_id),
                (KnowledgeBase.owner_id == user.id) |
                (KnowledgeBase.visibility == KBVisibility.GLOBAL)
            ).first()

            if not kb:
                return {"success": False, "error": "Knowledge base not found or access denied"}

            # Determine file type
            ext = filename.lower().split('.')[-1] if '.' in filename else 'other'
            file_type = FileType(ext) if ext in [e.value for e in FileType] else FileType.OTHER
            mime_type = self._storage.get_mime_type(filename)

            # Create file record
            file = KBFile(
                knowledge_base_id=kb.id,
                filename=filename,
                original_filename=filename,
                file_type=file_type,
                mime_type=mime_type,
                size_bytes=len(content),
                status=FileStatus.PENDING
            )

            session.add(file)
            session.flush()

            # Upload to Minio
            object_key = self._storage.generate_object_key(
                str(user.id), str(kb.id), str(file.id), filename
            )
            self._storage.upload_file(object_key, content)
            file.minio_object_key = object_key

            session.commit()
            session.refresh(file)

            result = {
                "success": True,
                "file_id": str(file.id),
                "filename": filename,
                "size_bytes": len(content),
                "status": file.status.value
            }

            # Process file if requested
            if process_immediately:
                process_result = await self._processor.process_file(str(file.id))
                result["processing"] = process_result

            return result

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to upload file: {e}")
            raise
        finally:
            session.close()

    async def get_upload_url(
        self,
        kb_id: str,
        user_id: str,
        filename: str
    ) -> dict:
        """Get a presigned URL for direct file upload."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            # Verify access
            kb = session.query(KnowledgeBase).filter(
                KnowledgeBase.id == UUID(kb_id),
                (KnowledgeBase.owner_id == user.id) |
                (KnowledgeBase.visibility == KBVisibility.GLOBAL)
            ).first()

            if not kb:
                return {"success": False, "error": "Knowledge base not found or access denied"}

            # Determine file type
            ext = filename.lower().split('.')[-1] if '.' in filename else 'other'
            file_type = FileType(ext) if ext in [e.value for e in FileType] else FileType.OTHER

            # Create pending file record
            file = KBFile(
                knowledge_base_id=kb.id,
                filename=filename,
                original_filename=filename,
                file_type=file_type,
                mime_type=self._storage.get_mime_type(filename),
                status=FileStatus.PENDING
            )

            session.add(file)
            session.flush()

            # Generate object key and presigned URL
            object_key = self._storage.generate_object_key(
                str(user.id), str(kb.id), str(file.id), filename
            )
            file.minio_object_key = object_key

            upload_url = self._storage.get_presigned_upload_url(object_key)

            session.commit()

            return {
                "success": True,
                "file_id": str(file.id),
                "upload_url": upload_url,
                "upload_method": "PUT",
                "minio_object_key": object_key,
                "expires_in_seconds": 3600
            }

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to get upload URL: {e}")
            raise
        finally:
            session.close()

    async def list_files(
        self,
        kb_id: str,
        user_id: str,
        status: str = None
    ) -> List[dict]:
        """List files in a knowledge base."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            kb = session.query(KnowledgeBase).filter(
                KnowledgeBase.id == UUID(kb_id),
                (KnowledgeBase.owner_id == user.id) |
                (KnowledgeBase.visibility == KBVisibility.GLOBAL)
            ).first()

            if not kb:
                return []

            query = session.query(KBFile).filter(KBFile.knowledge_base_id == kb.id)

            if status:
                query = query.filter(KBFile.status == FileStatus(status))

            files = query.all()

            return [{
                "id": str(f.id),
                "filename": f.filename,
                "file_type": f.file_type.value,
                "size_bytes": f.size_bytes,
                "status": f.status.value,
                "chunk_count": f.chunk_count,
                "error_message": f.error_message,
                "created_at": f.created_at.isoformat()
            } for f in files]

        finally:
            session.close()

    async def delete_file(
        self,
        file_id: str,
        user_id: str
    ) -> dict:
        """Delete a file and its vectors/nodes."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            file = session.query(KBFile).join(KnowledgeBase).filter(
                KBFile.id == UUID(file_id),
                (KnowledgeBase.owner_id == user.id) |
                (KnowledgeBase.visibility == KBVisibility.GLOBAL)
            ).first()

            if not file:
                return {"success": False, "error": "File not found or access denied"}

            kb = file.knowledge_base

            # Delete vectors from Milvus
            chunk_ids = [str(c.milvus_id) for c in file.chunks if c.milvus_id]
            if chunk_ids:
                await self._embeddings.delete_vectors(kb.milvus_collection, chunk_ids)

            # Delete nodes from Neo4j
            await self._graph.delete_file_nodes(str(file.id))

            # Delete from Minio
            if file.minio_object_key:
                self._storage.delete_file(file.minio_object_key)

            # Update KB stats
            kb.file_count = max(0, kb.file_count - 1)
            kb.chunk_count = max(0, kb.chunk_count - file.chunk_count)
            kb.total_size_bytes = max(0, kb.total_size_bytes - file.size_bytes)

            # Delete from PostgreSQL
            session.delete(file)
            session.commit()

            return {"success": True, "deleted_file_id": file_id}

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete file: {e}")
            raise
        finally:
            session.close()

    # =========================================================================
    # SEARCH
    # =========================================================================

    async def search(
        self,
        query: str,
        user_id: str,
        kb_ids: List[str] = None,
        top_k: int = 10,
        search_type: str = "hybrid"
    ) -> dict:
        """Search across knowledge bases."""
        self._ensure_initialized()

        user = self._get_or_create_user(user_id)
        session = self._db.get_session()

        try:
            # Get accessible KBs
            kb_query = session.query(KnowledgeBase).filter(
                (KnowledgeBase.owner_id == user.id) |
                (KnowledgeBase.visibility == KBVisibility.GLOBAL)
            )

            if kb_ids:
                kb_query = kb_query.filter(KnowledgeBase.id.in_([UUID(id) for id in kb_ids]))

            kbs = kb_query.all()

            if not kbs:
                return {"query": query, "results": [], "total": 0}

            all_results = []

            for kb in kbs:
                if search_type in ["vector", "hybrid"]:
                    # Vector search
                    vector_results = await self._embeddings.search(
                        kb.milvus_collection,
                        query,
                        kb.embedding_provider,
                        top_k
                    )
                    for r in vector_results:
                        r["kb_id"] = str(kb.id)
                        r["kb_name"] = kb.name
                    all_results.extend(vector_results)

                if search_type in ["graph", "hybrid"]:
                    # Graph search
                    graph_results = await self._graph.search(
                        query,
                        str(kb.id),
                        top_k
                    )
                    for r in graph_results:
                        r["kb_id"] = str(kb.id)
                        r["kb_name"] = kb.name
                        r["source"] = "graph"
                    all_results.extend(graph_results)

            # Sort by score and limit
            all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            all_results = all_results[:top_k]

            return {
                "query": query,
                "results": all_results,
                "total": len(all_results),
                "search_type": search_type
            }

        finally:
            session.close()

    # =========================================================================
    # HEALTH CHECK
    # =========================================================================

    async def health_check(self) -> dict:
        """Check health of all infrastructure."""
        self._ensure_initialized()

        return {
            "postgres": self._db.health_check(),
            "milvus": self._embeddings.health_check() if self._embeddings else {"status": "not_initialized"},
            "neo4j": self._graph.health_check() if self._graph else {"status": "not_initialized"},
            "minio": self._storage.health_check() if self._storage else {"status": "not_initialized"},
            "agent": {"status": "healthy", "initialized": self._initialized}
        }

    # =========================================================================
    # TOOL EXECUTION (for parent agents)
    # =========================================================================

    async def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a KB tool by name. Used when called as a subagent."""
        self._ensure_initialized()

        tool_methods = {
            "kb_create": lambda i: self.create_knowledge_base(
                user_id=i["user_id"],
                name=i["name"],
                description=i.get("description"),
                visibility=i.get("visibility", "private"),
                embedding_provider=i.get("embedding_provider", "google")
            ),
            "kb_list": lambda i: self.list_knowledge_bases(
                user_id=i["user_id"],
                include_global=i.get("include_global", True)
            ),
            "kb_delete": lambda i: self.delete_knowledge_base(
                kb_id=i["kb_id"],
                user_id=i["user_id"]
            ),
            "kb_upload_file": lambda i: self._upload_from_base64(
                kb_id=i["kb_id"],
                user_id=i["user_id"],
                filename=i["filename"],
                content_base64=i["content_base64"]
            ),
            "kb_list_files": lambda i: self.list_files(
                kb_id=i["kb_id"],
                user_id=i["user_id"],
                status=i.get("status")
            ),
            "kb_delete_file": lambda i: self.delete_file(
                file_id=i["file_id"],
                user_id=i["user_id"]
            ),
            "kb_search": lambda i: self.search(
                query=i["query"],
                user_id=i["user_id"],
                kb_ids=i.get("kb_ids"),
                top_k=i.get("top_k", 10),
                search_type=i.get("search_type", "hybrid")
            ),
            "kb_get_upload_url": lambda i: self.get_upload_url(
                kb_id=i["kb_id"],
                user_id=i["user_id"],
                filename=i["filename"]
            ),
            "kb_health": lambda i: self.health_check()
        }

        if tool_name not in tool_methods:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            result = await tool_methods[tool_name](tool_input)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": str(e)}

    async def _upload_from_base64(
        self,
        kb_id: str,
        user_id: str,
        filename: str,
        content_base64: str
    ) -> dict:
        """Upload file from base64 content."""
        import base64
        content = base64.b64decode(content_base64)
        return await self.upload_file(kb_id, user_id, filename, content)

    # =========================================================================
    # NATURAL LANGUAGE INTERFACE (subagent mode)
    # =========================================================================

    async def run(self, message: str, user_id: str = "default") -> str:
        """
        Process a natural language request.
        Use this when the agent is called as a subagent.
        """
        self._ensure_initialized()

        # Add user context to the message
        system_prompt = f"""You are the Knowledge Base Agent, a specialized subagent for managing multi-tenant knowledge bases.

You have access to the following tools:
- kb_create: Create a new knowledge base
- kb_list: List accessible knowledge bases
- kb_delete: Delete a knowledge base
- kb_upload_file: Upload a file (base64)
- kb_list_files: List files in a KB
- kb_delete_file: Delete a file
- kb_search: Search across knowledge bases
- kb_get_upload_url: Get presigned upload URL
- kb_health: Check system health

Current user ID: {user_id}

Always include the user_id in tool calls. Respond in Portuguese if the user message is in Portuguese."""

        messages = [{"role": "user", "content": message}]

        response = self.client.messages.create(
            model=self.config.claude_model,
            max_tokens=4096,
            system=system_prompt,
            tools=KB_TOOL_DEFINITIONS,
            messages=messages
        )

        # Process tool calls
        while response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    result = await self.execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str)
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            response = self.client.messages.create(
                model=self.config.claude_model,
                max_tokens=4096,
                system=system_prompt,
                tools=KB_TOOL_DEFINITIONS,
                messages=messages
            )

        # Extract final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                final_text += block.text

        return final_text
