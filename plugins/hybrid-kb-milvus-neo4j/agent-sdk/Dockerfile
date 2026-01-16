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
COPY hybrid_kb/ hybrid_kb/

# Install dependencies
RUN uv pip install --system -e .

# Environment variables (override at runtime)
ENV ANTHROPIC_API_KEY=""
ENV MILVUS_URI="http://milvus:19530"
ENV NEO4J_URI="bolt://neo4j:7687"
ENV NEO4J_USER="neo4j"
ENV NEO4J_PASS=""
ENV GOOGLE_API_KEY=""
ENV COHERE_API_KEY=""

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "from hybrid_kb import HybridKBOrchestrator; print('OK')" || exit 1

# Default command - interactive mode
CMD ["hybrid-kb", "interactive"]
