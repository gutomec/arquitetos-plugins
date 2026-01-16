"""
Knowledge Base Agent - Self-Contained Subagent Module
======================================================
Sistema completo de bases de conhecimento multi-tenant com Milvus, Neo4j e PostgreSQL.

Pode ser usado como subagente em qualquer sistema Claude Agent SDK.

Uso como Subagente:
    from knowledge_base_agent import KnowledgeBaseAgent

    # O agente auto-inicializa toda a infraestrutura
    kb_agent = KnowledgeBaseAgent()

    # Usar como subagente
    result = await kb_agent.run("Crie uma base de conhecimento chamada 'Documentos Legais'")

Uso como Ferramenta em Outro Agente:
    from knowledge_base_agent import get_kb_tools, KnowledgeBaseAgent

    # Obter ferramentas para usar em outro agente
    tools = get_kb_tools()

    # Ou usar diretamente as operações
    kb_agent = KnowledgeBaseAgent()
    kb = await kb_agent.create_knowledge_base(user_id, "Minha KB", visibility="global")
    await kb_agent.upload_file(kb.id, file_content, "documento.pdf")
    results = await kb_agent.search("minha query", user_id=user_id)
"""

from .agent import KnowledgeBaseAgent, get_kb_tools, KB_TOOL_DEFINITIONS
from .core.config import KBConfig
from .core.models import (
    KnowledgeBase,
    KBFile,
    User,
    FileStatus,
    KBVisibility
)

__version__ = "1.0.0"
__all__ = [
    "KnowledgeBaseAgent",
    "get_kb_tools",
    "KB_TOOL_DEFINITIONS",
    "KBConfig",
    "KnowledgeBase",
    "KBFile",
    "User",
    "FileStatus",
    "KBVisibility"
]
