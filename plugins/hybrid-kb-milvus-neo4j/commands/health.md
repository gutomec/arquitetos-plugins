# Command: /health

Verifica o status de saude do sistema Hybrid Knowledge Base.

## Usage

```
/health
/health --verbose
/health --service <nome>
```

## Description

Este comando verifica o status de todos os componentes do sistema:
- Milvus (vector database)
- Neo4j (graph database)
- etcd (metadata store)
- Google API (embedding)
- Cohere API (embedding)

## Arguments

| Argument | Description |
|----------|-------------|
| (nenhum) | Status resumido de todos servicos |
| `--verbose` | Status detalhado com metricas |
| `--service <nome>` | Status de servico especifico |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--json` | false | Output em formato JSON |
| `--watch` | false | Monitoramento continuo |
| `--interval` | 30s | Intervalo de monitoramento |

## Services

| Service | Check | Healthy When |
|---------|-------|--------------|
| Milvus | Connection + Collections | Connected, collections acessiveis |
| Neo4j | Connection + Query | Connected, queries funcionando |
| etcd | Cluster status | Leader eleito, cluster saudavel |
| Google API | API key present | Key configurada e valida |
| Cohere API | API key present | Key configurada e valida |

## Examples

### Example 1: Status rapido

```
/health
```

### Example 2: Status detalhado

```
/health --verbose
```

### Example 3: Servico especifico

```
/health --service neo4j
```

### Example 4: Monitoramento continuo

```
/health --watch --interval 60s
```

## Output

### Quick Status

```markdown
## System Health

**Timestamp**: 2024-01-16T10:30:00Z
**Overall Status**: HEALTHY

| Service | Status |
|---------|--------|
| Milvus | HEALTHY |
| Neo4j | HEALTHY |
| etcd | HEALTHY |
| Google API | CONFIGURED |
| Cohere API | CONFIGURED |
```

### Verbose Output

```markdown
## System Health Report

**Timestamp**: 2024-01-16T10:30:00Z
**Overall Status**: HEALTHY

---

### Milvus
**Status**: HEALTHY
**URI**: http://localhost:19530

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Connection | OK | - | OK |
| Collections | 3 | - | OK |
| Total vectors | 15,678 | - | OK |
| Search latency p99 | 42ms | 50ms | OK |
| Insert latency p99 | 15ms | 100ms | OK |

---

### Neo4j
**Status**: HEALTHY
**URI**: bolt://localhost:7687
**Database**: neo4j

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Connection | OK | - | OK |
| Nodes | 22,344 | - | OK |
| Relationships | 28,035 | - | OK |
| Query cache hit | 85% | 70% | OK |
| Store size | 256MB | 10GB | OK |

---

### etcd
**Status**: HEALTHY
**Cluster**: 3 members

| Metric | Value | Status |
|--------|-------|--------|
| Leader | node1 | OK |
| DB size | 12MB | OK |
| Keys | 1,234 | OK |

---

### Embedding APIs

#### Google API
**Status**: CONFIGURED
**Model**: text-embedding-004

| Check | Status |
|-------|--------|
| API Key | Present |
| Quota | OK |

#### Cohere API
**Status**: CONFIGURED
**Model**: embed-v4

| Check | Status |
|-------|--------|
| API Key | Present |
| Rate limit | OK |

---

### Performance Summary

| Operation | p50 | p95 | p99 | Target |
|-----------|-----|-----|-----|--------|
| Vector search | 25ms | 38ms | 42ms | <50ms |
| Graph query | 45ms | 78ms | 95ms | <100ms |
| Hybrid search | 85ms | 145ms | 178ms | <200ms |

---

### Recommendations
No issues detected. System operating normally.
```

### Degraded Status

```markdown
## System Health Report

**Status**: DEGRADED

### Issues Detected

#### Neo4j
**Status**: DEGRADED
**Issue**: High query latency

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Query latency p99 | 250ms | 100ms | WARN |

**Recommended Actions**:
1. Check active connections
2. Review slow queries
3. Consider adding indices

---

### Alerts
- Query latency exceeds threshold

### Impact
- `graph_search`: Degraded performance
- `hybrid_search`: Slower than normal
```

### Critical Status

```markdown
## System Health Report

**Status**: CRITICAL

### Services Down

#### Milvus
**Status**: UNREACHABLE
**Error**: Connection refused (http://localhost:19530)

**Troubleshooting**:
```bash
# Check container
docker ps | grep milvus

# Restart service
docker-compose restart milvus

# Check logs
docker logs milvus-standalone --tail 100
```

### Impact
- `vector_search`: UNAVAILABLE
- `hybrid_search`: UNAVAILABLE
- `ingest_document`: UNAVAILABLE

### Immediate Action Required
1. Verify Milvus container is running
2. Check etcd connectivity
3. Review system resources
```

## MCP Tools Used

- `health_check` - Verificacao completa de saude

## Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| HEALTHY | All services operational | None |
| CONFIGURED | API key present (not tested) | None |
| DEGRADED | Performance issues | Investigate |
| UNREACHABLE | Cannot connect | Immediate action |
| CRITICAL | Multiple failures | Emergency action |

## Related Commands

- `/schema` - Ver estrutura do sistema
- `/buscar` - Testar funcionalidade de busca
- `/ingerir` - Testar funcionalidade de ingestao
