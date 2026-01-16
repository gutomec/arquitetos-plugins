"""
Embedding Service - Milvus Vector Operations
=============================================
"""

from typing import List, Optional, Literal
import logging
import hashlib

from pymilvus import MilvusClient, DataType
import google.generativeai as genai
import cohere

from ..core.config import KBConfig

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Manages embeddings and Milvus operations."""

    DIMENSIONS = {
        "google": 768,   # text-embedding-004
        "cohere": 1024   # embed-v4
    }

    def __init__(self, config: KBConfig):
        self.config = config
        self.milvus = MilvusClient(uri=config.milvus_uri)
        self._cohere_client = None

        if config.google_api_key:
            genai.configure(api_key=config.google_api_key)

    async def generate_embedding(
        self,
        text: str,
        provider: Literal["google", "cohere"] = "google"
    ) -> List[float]:
        """Generate embedding for text."""
        try:
            if provider == "google":
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                return result['embedding']
            else:
                if self._cohere_client is None:
                    self._cohere_client = cohere.Client(self.config.cohere_api_key)
                response = self._cohere_client.embed(
                    texts=[text],
                    model="embed-english-v3.0",
                    input_type="search_document"
                )
                return response.embeddings[0]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    async def generate_query_embedding(
        self,
        query: str,
        provider: Literal["google", "cohere"] = "google"
    ) -> List[float]:
        """Generate embedding for query."""
        try:
            if provider == "google":
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=query,
                    task_type="RETRIEVAL_QUERY"
                )
                return result['embedding']
            else:
                if self._cohere_client is None:
                    self._cohere_client = cohere.Client(self.config.cohere_api_key)
                response = self._cohere_client.embed(
                    texts=[query],
                    model="embed-english-v3.0",
                    input_type="search_query"
                )
                return response.embeddings[0]
        except Exception as e:
            logger.error(f"Query embedding error: {e}")
            raise

    async def create_collection(
        self,
        collection_name: str,
        provider: Literal["google", "cohere"] = "google"
    ):
        """Create a Milvus collection."""
        dim = self.DIMENSIONS[provider]

        if self.milvus.has_collection(collection_name):
            logger.info(f"Collection {collection_name} already exists")
            return

        self.milvus.create_collection(
            collection_name=collection_name,
            dimension=dim,
            metric_type="COSINE",
            auto_id=False
        )
        logger.info(f"Created collection: {collection_name} (dim={dim})")

    async def delete_collection(self, collection_name: str):
        """Delete a Milvus collection."""
        if self.milvus.has_collection(collection_name):
            self.milvus.drop_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")

    async def insert_vectors(
        self,
        collection_name: str,
        vectors: List[dict]
    ) -> List[str]:
        """
        Insert vectors into collection.

        vectors: List of dicts with 'id', 'vector', 'text', 'metadata'
        """
        if not vectors:
            return []

        self.milvus.insert(collection_name=collection_name, data=vectors)
        logger.info(f"Inserted {len(vectors)} vectors into {collection_name}")
        return [v['id'] for v in vectors]

    async def delete_vectors(
        self,
        collection_name: str,
        ids: List[str]
    ):
        """Delete vectors by IDs."""
        if not ids:
            return

        self.milvus.delete(
            collection_name=collection_name,
            filter=f"id in {ids}"
        )
        logger.info(f"Deleted {len(ids)} vectors from {collection_name}")

    async def search(
        self,
        collection_name: str,
        query: str,
        provider: Literal["google", "cohere"] = "google",
        top_k: int = 10
    ) -> List[dict]:
        """Search for similar vectors."""
        try:
            query_embedding = await self.generate_query_embedding(query, provider)

            results = self.milvus.search(
                collection_name=collection_name,
                data=[query_embedding],
                limit=top_k,
                output_fields=["text", "file_id", "chunk_index", "metadata"]
            )

            formatted = []
            for hits in results:
                for hit in hits:
                    formatted.append({
                        "id": hit.get("id"),
                        "score": hit.get("distance", 0),
                        "text": hit.get("entity", {}).get("text", ""),
                        "file_id": hit.get("entity", {}).get("file_id", ""),
                        "chunk_index": hit.get("entity", {}).get("chunk_index", 0),
                        "metadata": hit.get("entity", {}).get("metadata", {}),
                        "source": "vector"
                    })

            return formatted
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def health_check(self) -> dict:
        """Check Milvus health."""
        try:
            collections = self.milvus.list_collections()
            return {
                "status": "healthy",
                "uri": self.config.milvus_uri,
                "collection_count": len(collections)
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
