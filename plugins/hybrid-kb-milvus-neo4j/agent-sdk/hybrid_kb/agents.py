"""
Hybrid KB Agents - Specialized AI Agents
========================================
Agentes especializados para operações no sistema Hybrid KB.
"""

import anthropic
from typing import Optional, List, Any
import json
import logging
from .tools import HybridKBTools, TOOL_DEFINITIONS
from .skills import Skills

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all Hybrid KB agents."""

    def __init__(
        self,
        name: str,
        role: str,
        tools: HybridKBTools = None,
        model: str = "claude-sonnet-4-20250514",
        api_key: str = None
    ):
        self.name = name
        self.role = role
        self.tools = tools or HybridKBTools()
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.conversation_history = []

    def get_system_prompt(self) -> str:
        """Override in subclasses."""
        return f"You are {self.name}, a {self.role}."

    def get_available_tools(self) -> List[dict]:
        """Override to specify which tools this agent can use."""
        return TOOL_DEFINITIONS

    async def process_tool_call(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a tool call and return the result."""
        tool_method = getattr(self.tools, tool_name, None)
        if tool_method:
            return await tool_method(**tool_input)
        return {"error": f"Tool {tool_name} not found"}

    async def run(self, user_message: str, max_turns: int = 10) -> str:
        """Run the agent with the given user message."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        for _ in range(max_turns):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.get_system_prompt(),
                tools=self.get_available_tools(),
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
                    result = await self.process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result.dict() if hasattr(result, 'dict') else result)
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


class IngestionAgent(BaseAgent):
    """Agent specialized in document ingestion."""

    def __init__(self, tools: HybridKBTools = None, **kwargs):
        super().__init__(
            name="Ingestion Agent",
            role="Document Processing Specialist",
            tools=tools,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return f"""You are the Ingestion Agent, specialized in document processing for the Hybrid Knowledge Base.

## Your Role
Process documents through the complete ingestion pipeline:
1. Analyze document structure and content type
2. Apply appropriate chunking strategy
3. Generate embeddings using the best provider
4. Store vectors in Milvus
5. Extract entities and build knowledge graph in Neo4j

## Available Knowledge
{Skills.chunking_strategies()}

{Skills.embedding_selection()}

## Guidelines
- Always validate document content before processing
- Choose chunking strategy based on document type
- Select embedding provider based on content language
- Report detailed statistics after ingestion
- Handle errors gracefully with clear messages

## Response Format
After ingestion, provide:
- Document ID
- Number of chunks created
- Entities extracted
- Storage confirmation (Milvus + Neo4j)
"""

    def get_available_tools(self) -> List[dict]:
        return [t for t in TOOL_DEFINITIONS if t["name"] in [
            "ingest_document", "build_knowledge_graph", "health_check"
        ]]


class RetrievalAgent(BaseAgent):
    """Agent specialized in search and retrieval."""

    def __init__(self, tools: HybridKBTools = None, **kwargs):
        super().__init__(
            name="Retrieval Agent",
            role="Search and Retrieval Specialist",
            tools=tools,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return f"""You are the Retrieval Agent, specialized in search and retrieval from the Hybrid Knowledge Base.

## Your Role
Execute searches using the optimal strategy:
1. Analyze the query to determine best approach
2. Route to vector, graph, or hybrid search
3. Process and rank results
4. Provide relevant context for answers

## Query Routing Decision Matrix
{Skills.query_optimization()}

## Search Strategies

### Vector Search
Use for: Semantic similarity, conceptual queries
- "documents about machine learning"
- "papers similar to this topic"

### Graph Search
Use for: Structural queries, relationships
- "who authored this paper"
- "topics connected to deep learning"

### Hybrid Search
Use for: Complex queries needing both
- "papers about ML citing Stanford authors"

## Guidelines
- Always explain your routing decision
- Use appropriate top_k based on query specificity
- Apply relevance thresholds
- Provide confidence scores with results

## Response Format
Present results with:
- Search strategy used
- Number of results found
- Ranked results with scores
- Graph context if using hybrid
"""

    def get_available_tools(self) -> List[dict]:
        return [t for t in TOOL_DEFINITIONS if t["name"] in [
            "vector_search", "graph_search", "hybrid_search", "multi_hop_reasoning"
        ]]


class SchemaAnalystAgent(BaseAgent):
    """Agent specialized in schema analysis."""

    def __init__(self, tools: HybridKBTools = None, **kwargs):
        super().__init__(
            name="Schema Analyst",
            role="Knowledge Graph Schema Expert",
            tools=tools,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return f"""You are the Schema Analyst, expert in knowledge graph schema design and analysis.

## Your Role
Analyze and optimize the schema of the Hybrid Knowledge Base:
1. Examine Neo4j node types and relationships
2. Analyze Milvus collections and indexes
3. Identify optimization opportunities
4. Suggest schema improvements

## Schema Design Knowledge
{Skills.schema_design()}

## Analysis Tasks
- Node type distribution and usage
- Relationship patterns and cardinality
- Index effectiveness
- Data quality metrics
- Consistency between Milvus and Neo4j

## Guidelines
- Provide actionable recommendations
- Quantify issues with metrics
- Prioritize improvements by impact
- Consider query patterns in recommendations

## Response Format
Present analysis with:
- Current schema overview
- Statistics (nodes, relationships, vectors)
- Quality metrics
- Recommendations with priority
"""

    def get_available_tools(self) -> List[dict]:
        return [t for t in TOOL_DEFINITIONS if t["name"] in [
            "analyze_schema", "analyze_collections", "graph_search"
        ]]


class HealthMonitorAgent(BaseAgent):
    """Agent specialized in system health monitoring."""

    def __init__(self, tools: HybridKBTools = None, **kwargs):
        super().__init__(
            name="Health Monitor",
            role="System Health Specialist",
            tools=tools,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return """You are the Health Monitor, responsible for monitoring the Hybrid Knowledge Base system health.

## Your Role
Monitor and report on system health:
1. Check connectivity to all components
2. Validate data consistency
3. Monitor performance metrics
4. Alert on issues

## Components to Monitor
- **Milvus**: Vector database health, collection stats
- **Neo4j**: Graph database health, query performance
- **Embeddings**: API availability, rate limits
- **etcd**: Metadata service (if configured)

## Health Thresholds
| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Milvus latency | < 50ms | 50-200ms | > 200ms |
| Neo4j latency | < 100ms | 100-500ms | > 500ms |
| API availability | 100% | 99%+ | < 99% |

## Guidelines
- Run health checks proactively
- Provide clear status summaries
- Suggest remediation for issues
- Track trends over time

## Response Format
Present health status with:
- Overall system status (healthy/degraded/critical)
- Component-by-component status
- Any active issues
- Recommendations
"""

    def get_available_tools(self) -> List[dict]:
        return [t for t in TOOL_DEFINITIONS if t["name"] in [
            "health_check", "analyze_schema", "analyze_collections"
        ]]


# Agent registry for orchestrator
AGENT_REGISTRY = {
    "ingestion": IngestionAgent,
    "retrieval": RetrievalAgent,
    "schema": SchemaAnalystAgent,
    "health": HealthMonitorAgent
}
