FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY knowledge_base_agent/ knowledge_base_agent/

# Install dependencies with full document support
RUN uv pip install --system -e ".[full]"

# Environment variables (override at runtime)
ENV ANTHROPIC_API_KEY=""
ENV KB_POSTGRES_URL="postgresql://postgres:postgres@postgres:5432/knowledge_base"
ENV KB_MILVUS_URI="http://milvus:19530"
ENV KB_NEO4J_URI="bolt://neo4j:7687"
ENV KB_NEO4J_USER="neo4j"
ENV KB_NEO4J_PASS=""
ENV KB_MINIO_ENDPOINT="minio:9000"
ENV KB_MINIO_ACCESS_KEY="minioadmin"
ENV KB_MINIO_SECRET_KEY="minioadmin"
ENV GOOGLE_API_KEY=""
ENV COHERE_API_KEY=""

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "from knowledge_base_agent import KnowledgeBaseAgent; print('OK')" || exit 1

CMD ["python", "-c", "from knowledge_base_agent import KnowledgeBaseAgent; import asyncio; asyncio.run(KnowledgeBaseAgent().health_check())"]
