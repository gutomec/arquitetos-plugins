"""
Hybrid KB Orchestrator - Main Coordinator
==========================================
Orquestrador principal que coordena todos os agentes do sistema.
"""

import anthropic
from typing import Optional, Literal
import json
import logging
import re
from .tools import HybridKBTools, TOOL_DEFINITIONS
from .agents import (
    IngestionAgent,
    RetrievalAgent,
    SchemaAnalystAgent,
    HealthMonitorAgent,
    AGENT_REGISTRY
)
from .skills import Skills

logger = logging.getLogger(__name__)


class HybridKBOrchestrator:
    """
    Orquestrador central do sistema Hybrid Knowledge Base.

    Coordena os agentes especializados e roteia requisições
    para o agente mais apropriado.

    Uso:
        orchestrator = HybridKBOrchestrator()
        result = await orchestrator.process("Busque documentos sobre IA")
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str = None,
        milvus_uri: str = None,
        neo4j_uri: str = None,
        neo4j_user: str = None,
        neo4j_pass: str = None,
        google_api_key: str = None,
        cohere_api_key: str = None
    ):
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

        # Initialize shared tools
        self.tools = HybridKBTools(
            milvus_uri=milvus_uri,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_pass=neo4j_pass,
            google_api_key=google_api_key,
            cohere_api_key=cohere_api_key
        )

        # Initialize agents with shared tools
        self.agents = {
            "ingestion": IngestionAgent(tools=self.tools, model=model, api_key=api_key),
            "retrieval": RetrievalAgent(tools=self.tools, model=model, api_key=api_key),
            "schema": SchemaAnalystAgent(tools=self.tools, model=model, api_key=api_key),
            "health": HealthMonitorAgent(tools=self.tools, model=model, api_key=api_key)
        }

        self.conversation_history = []

    def get_system_prompt(self) -> str:
        """System prompt for the orchestrator."""
        return """You are the KB Orchestrator, the central coordinator of the Hybrid Knowledge Base system.

## Your Role
Coordinate all workflows in the GraphRAG hybrid system:
1. Analyze user requests to determine intent
2. Route to the appropriate specialized agent
3. Execute operations using available tools
4. Provide comprehensive responses

## Request Classification

| Intent | Indicators | Action |
|--------|------------|--------|
| INGEST | "ingerir", "adicionar", "processar documento" | Use ingest tools or delegate to ingestion agent |
| SEARCH | "buscar", "encontrar", "pesquisar", "similar" | Use search tools or delegate to retrieval agent |
| ANALYZE | "analisar schema", "estatísticas", "estrutura" | Use analysis tools or delegate to schema agent |
| MONITOR | "health", "status", "saúde", "verificar" | Use health tools or delegate to health agent |

## Available Tools
You have access to all system tools:
- **Ingestion**: ingest_document, build_knowledge_graph
- **Retrieval**: vector_search, graph_search, hybrid_search, multi_hop_reasoning
- **Analysis**: analyze_schema, analyze_collections
- **Monitoring**: health_check

## Query Routing for Search

| Query Type | Strategy | Example |
|------------|----------|---------|
| Semantic/Conceptual | vector_search | "documentos sobre machine learning" |
| Structural/Relational | graph_search | "quem escreveu sobre NLP" |
| Complex/Multi-entity | hybrid_search | "papers sobre ML citando autores de Stanford" |

## Response Guidelines

1. **Always explain** your routing decision
2. **Use the most specific tool** for the task
3. **Provide structured responses** with clear sections
4. **Include metadata** (counts, scores, sources)
5. **Handle errors gracefully** with helpful messages

## Response Format

### For Ingestion
```markdown
## Ingestion Report
**Status**: Success/Failure
**Document ID**: {id}
**Chunks**: {count}
**Entities**: {count}
```

### For Search
```markdown
## Search Results
**Query**: {query}
**Strategy**: {vector|graph|hybrid}
**Results**: {count}

### Top Results
1. [Score: X.XX] Title - Preview...
```

### For Analysis
```markdown
## Schema Analysis
**Nodes**: {types and counts}
**Relationships**: {types and counts}
**Collections**: {names and stats}
```

### For Health
```markdown
## System Health
**Status**: Healthy/Degraded/Critical
**Milvus**: {status}
**Neo4j**: {status}
**Embeddings**: {status}
```
"""

    def classify_intent(self, message: str) -> Literal["ingest", "search", "analyze", "monitor", "general"]:
        """Classify the user's intent based on the message."""
        message_lower = message.lower()

        # Ingestion patterns
        if any(word in message_lower for word in ["ingerir", "adicionar", "processar documento", "importar", "indexar"]):
            return "ingest"

        # Search patterns
        if any(word in message_lower for word in ["buscar", "encontrar", "pesquisar", "similar", "procurar", "query", "search"]):
            return "search"

        # Analysis patterns
        if any(word in message_lower for word in ["analisar", "schema", "estatística", "estrutura", "collection", "analyze"]):
            return "analyze"

        # Health patterns
        if any(word in message_lower for word in ["health", "status", "saúde", "verificar", "check", "monitor"]):
            return "monitor"

        return "general"

    async def process(self, user_message: str, delegate_to_agent: bool = False) -> str:
        """
        Process a user request.

        Args:
            user_message: The user's request
            delegate_to_agent: If True, delegate to specialized agent instead of handling directly

        Returns:
            The response string
        """
        intent = self.classify_intent(user_message)

        if delegate_to_agent and intent in self.agents:
            # Delegate to specialized agent
            agent = self.agents[intent]
            return await agent.run(user_message)

        # Handle directly using tools
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        max_turns = 10
        for _ in range(max_turns):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.get_system_prompt(),
                tools=TOOL_DEFINITIONS,
                messages=self.conversation_history
            )

            # Process response
            assistant_content = []
            tool_results = []

            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                    # Execute tool
                    tool_method = getattr(self.tools, block.name, None)
                    if tool_method:
                        result = await tool_method(**block.input)
                        result_json = json.dumps(result.dict() if hasattr(result, 'dict') else result)
                    else:
                        result_json = json.dumps({"error": f"Tool {block.name} not found"})

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_json
                    })

            # Add assistant message
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_content
            })

            # If there were tool calls, add results and continue
            if tool_results:
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                # No more tool calls, return final response
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text
                return final_text

            if response.stop_reason == "end_turn":
                break

        return "Max turns reached without completion."

    async def ingest(self, content: str, metadata: dict = None) -> str:
        """Convenience method for document ingestion."""
        prompt = f"Ingira este documento: {content[:500]}..."
        if metadata:
            prompt += f"\nMetadados: {json.dumps(metadata)}"
        return await self.process(prompt)

    async def search(self, query: str, strategy: str = "auto") -> str:
        """Convenience method for search."""
        if strategy == "vector":
            prompt = f"Faça uma busca semântica por: {query}"
        elif strategy == "graph":
            prompt = f"Busque no grafo de conhecimento: {query}"
        elif strategy == "hybrid":
            prompt = f"Faça uma busca híbrida (vector + graph) por: {query}"
        else:
            prompt = f"Busque no knowledge base: {query}"
        return await self.process(prompt)

    async def analyze(self) -> str:
        """Convenience method for schema analysis."""
        return await self.process("Analise o schema do knowledge base (Neo4j e Milvus)")

    async def health(self) -> str:
        """Convenience method for health check."""
        return await self.process("Verifique a saúde de todos os componentes do sistema")

    def get_skill(self, skill_name: str) -> str:
        """Get a specific skill's knowledge."""
        return Skills.get(skill_name)

    def list_skills(self) -> list:
        """List all available skills."""
        return list(Skills.all().keys())

    def close(self):
        """Close all connections."""
        self.tools.close()
