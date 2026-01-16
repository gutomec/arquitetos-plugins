"""
Hybrid Knowledge Base - Agent SDK
=================================
Sistema multi-agente para GraphRAG com Milvus e Neo4j.

Uso:
    from hybrid_kb import HybridKBOrchestrator

    orchestrator = HybridKBOrchestrator()
    result = await orchestrator.process("Busque documentos sobre machine learning")
"""

from .orchestrator import HybridKBOrchestrator
from .agents import (
    IngestionAgent,
    RetrievalAgent,
    SchemaAnalystAgent,
    HealthMonitorAgent
)
from .tools import HybridKBTools
from .skills import Skills

__version__ = "1.0.0"
__all__ = [
    "HybridKBOrchestrator",
    "IngestionAgent",
    "RetrievalAgent",
    "SchemaAnalystAgent",
    "HealthMonitorAgent",
    "HybridKBTools",
    "Skills"
]
