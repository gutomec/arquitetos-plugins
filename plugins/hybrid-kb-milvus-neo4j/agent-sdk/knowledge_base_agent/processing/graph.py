"""
Graph Service - Neo4j Knowledge Graph Operations
=================================================
"""

from typing import List, Optional
import logging
import json

from neo4j import GraphDatabase

from ..core.config import KBConfig

logger = logging.getLogger(__name__)


class GraphService:
    """Manages Neo4j knowledge graph operations."""

    def __init__(self, config: KBConfig):
        self.config = config
        self.driver = GraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_pass)
        )
        self.database = config.neo4j_database
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes if they don't exist."""
        try:
            with self.driver.session(database=self.database) as session:
                # Create indexes
                session.run("CREATE INDEX kb_doc_id IF NOT EXISTS FOR (d:Document) ON (d.id)")
                session.run("CREATE INDEX kb_chunk_id IF NOT EXISTS FOR (c:Chunk) ON (c.id)")
                session.run("CREATE INDEX kb_entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)")
                session.run("CREATE INDEX kb_kb_id IF NOT EXISTS FOR (k:KnowledgeBase) ON (k.id)")
                logger.info("Neo4j indexes verified")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")

    async def create_document_node(
        self,
        doc_id: str,
        kb_id: str,
        filename: str,
        metadata: dict = None
    ) -> str:
        """Create a document node in the graph."""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MERGE (k:KnowledgeBase {id: $kb_id})
                MERGE (d:Document {id: $doc_id})
                SET d.filename = $filename,
                    d.kb_id = $kb_id,
                    d.metadata = $metadata,
                    d.created_at = datetime()
                MERGE (k)-[:CONTAINS]->(d)
                RETURN d.id as id
            """, doc_id=doc_id, kb_id=kb_id, filename=filename,
                metadata=json.dumps(metadata or {}))

            record = result.single()
            return record["id"] if record else None

    async def create_chunk_node(
        self,
        chunk_id: str,
        doc_id: str,
        content: str,
        chunk_index: int,
        milvus_id: str = None
    ) -> str:
        """Create a chunk node linked to document."""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (d:Document {id: $doc_id})
                MERGE (c:Chunk {id: $chunk_id})
                SET c.content = $content,
                    c.chunk_index = $chunk_index,
                    c.milvus_id = $milvus_id,
                    c.doc_id = $doc_id
                MERGE (d)-[:HAS_CHUNK]->(c)
                RETURN c.id as id
            """, chunk_id=chunk_id, doc_id=doc_id, content=content[:2000],
                chunk_index=chunk_index, milvus_id=milvus_id)

            record = result.single()
            return record["id"] if record else None

    async def extract_and_create_entities(
        self,
        doc_id: str,
        content: str,
        entity_types: List[str] = None
    ) -> int:
        """Extract entities from content and create nodes."""
        if entity_types is None:
            entity_types = ["Person", "Organization", "Concept", "Topic"]

        # Simple entity extraction (replace with LLM in production)
        entities = self._extract_entities(content)

        with self.driver.session(database=self.database) as session:
            for entity in entities:
                session.run("""
                    MATCH (d:Document {id: $doc_id})
                    MERGE (e:Entity {name: $name})
                    SET e.type = $type
                    MERGE (d)-[:MENTIONS]->(e)
                """, doc_id=doc_id, name=entity["name"], type=entity["type"])

        return len(entities)

    def _extract_entities(self, content: str) -> List[dict]:
        """Simple entity extraction. Replace with NER/LLM in production."""
        entities = []
        words = content.split()

        for word in words[:100]:  # Limit for performance
            if len(word) > 3 and word[0].isupper() and word.isalpha():
                entities.append({"name": word, "type": "Entity"})

        # Deduplicate
        seen = set()
        unique = []
        for e in entities:
            if e["name"] not in seen:
                seen.add(e["name"])
                unique.append(e)

        return unique[:20]

    async def delete_file_nodes(self, file_id: str):
        """Delete all nodes related to a file."""
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (d:Document {id: $file_id})
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                DETACH DELETE c, d
            """, file_id=file_id)
            logger.info(f"Deleted graph nodes for file: {file_id}")

    async def delete_kb_nodes(self, kb_id: str):
        """Delete all nodes related to a knowledge base."""
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (k:KnowledgeBase {id: $kb_id})
                OPTIONAL MATCH (k)-[:CONTAINS]->(d:Document)
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                DETACH DELETE c, d, k
            """, kb_id=kb_id)
            logger.info(f"Deleted graph nodes for KB: {kb_id}")

    async def search(
        self,
        query: str,
        kb_id: str,
        top_k: int = 10
    ) -> List[dict]:
        """Search the knowledge graph."""
        with self.driver.session(database=self.database) as session:
            # Full-text search on chunk content
            result = session.run("""
                MATCH (k:KnowledgeBase {id: $kb_id})-[:CONTAINS]->(d:Document)-[:HAS_CHUNK]->(c:Chunk)
                WHERE c.content CONTAINS $query OR d.filename CONTAINS $query
                RETURN c.id as chunk_id, c.content as content, c.chunk_index as chunk_index,
                       d.id as file_id, d.filename as filename
                LIMIT $limit
            """, kb_id=kb_id, query=query, limit=top_k)

            results = []
            for record in result:
                results.append({
                    "id": record["chunk_id"],
                    "text": record["content"],
                    "chunk_index": record["chunk_index"],
                    "file_id": record["file_id"],
                    "filename": record["filename"],
                    "score": 0.5,  # Placeholder score
                    "source": "graph"
                })

            return results

    async def get_related_entities(
        self,
        doc_id: str,
        max_depth: int = 2
    ) -> List[dict]:
        """Get entities related to a document."""
        with self.driver.session(database=self.database) as session:
            result = session.run(f"""
                MATCH (d:Document {{id: $doc_id}})-[:MENTIONS]->(e:Entity)
                OPTIONAL MATCH (e)-[r*1..{max_depth}]-(related:Entity)
                RETURN e.name as entity, e.type as type,
                       collect(DISTINCT related.name) as related_entities
                LIMIT 20
            """, doc_id=doc_id)

            return [dict(record) for record in result]

    def close(self):
        """Close the driver."""
        self.driver.close()

    def health_check(self) -> dict:
        """Check Neo4j health."""
        try:
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            return {"status": "healthy", "uri": self.config.neo4j_uri}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
