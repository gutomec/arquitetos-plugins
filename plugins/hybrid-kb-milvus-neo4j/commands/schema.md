# Command: /schema

Analisa o schema do sistema Hybrid Knowledge Base.

## Usage

```
/schema
/schema --neo4j
/schema --milvus
/schema --validate
```

## Description

Este comando analisa e exibe o schema completo do sistema, incluindo:
- Node labels e properties do Neo4j
- Relationship types e contagens
- Collections e campos do Milvus
- Indices e constraints
- Validacao de consistencia

## Arguments

| Argument | Description |
|----------|-------------|
| (nenhum) | Analise completa de ambos |
| `--neo4j` | Apenas schema do Neo4j |
| `--milvus` | Apenas collections do Milvus |
| `--validate` | Validar consistencia cross-database |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--collection` | - | Collection especifica (Milvus) |
| `--detailed` | false | Incluir todas propriedades |
| `--stats` | true | Incluir estatisticas de contagem |

## Examples

### Example 1: Analise completa

```
/schema
```

### Example 2: Apenas Neo4j

```
/schema --neo4j --detailed
```

### Example 3: Collection especifica

```
/schema --milvus --collection documents
```

### Example 4: Validar consistencia

```
/schema --validate
```

## Output

### Full Schema Analysis

```markdown
## Schema Analysis Report

**Timestamp**: 2024-01-16T10:30:00Z

---

### Neo4j Schema

#### Node Labels (3)
| Label | Count | Properties |
|-------|-------|------------|
| Document | 1,234 | id, title, source, doc_type, created_at |
| Chunk | 15,678 | id, content, index |
| Entity | 5,432 | id, name, type, description |

#### Relationships (3)
| Type | Count | Pattern |
|------|-------|---------|
| HAS_CHUNK | 15,678 | Document → Chunk |
| MENTIONS | 8,901 | Chunk → Entity |
| RELATED_TO | 3,456 | Entity → Entity |

#### Indices (4)
- document_id (UNIQUE)
- chunk_id (UNIQUE)
- entity_type (BTREE)
- document_content (FULLTEXT)

#### Constraints (3)
- Document.id IS UNIQUE
- Chunk.id IS UNIQUE
- Entity.id IS UNIQUE

---

### Milvus Collections

#### Collection: documents
| Field | Type | Description |
|-------|------|-------------|
| id | VARCHAR(64) | Primary key |
| vector | FLOAT_VECTOR(768) | Embedding |
| content | VARCHAR | Chunk content |
| doc_id | VARCHAR | Parent document |
| chunk_index | INT64 | Position |
| title | VARCHAR | Title |
| source | VARCHAR | Source |
| doc_type | VARCHAR | Type |
| created_at | VARCHAR | Timestamp |

**Statistics**:
- Vectors: 15,678
- Index: HNSW (M=16, ef=256)
- Partitions: technical, legal, general

---

### Schema Health
- Node/Relationship ratio: 1:1.8 (healthy)
- Index coverage: 100%
- Orphan detection: 0 orphans

### Recommendations
1. Consider adding index on Entity.description for full-text search
2. Partition usage is balanced
```

### Validation Output

```markdown
## Data Consistency Report

### Cross-Database Sync
| Database | Documents | Status |
|----------|-----------|--------|
| Milvus | 1,234 | - |
| Neo4j | 1,234 | - |
| **Difference** | 0 | SYNCED |

### Orphan Detection
- Orphan chunks: 0
- Orphan entities: 0

### Referential Integrity
- Document → Chunk: 100% intact
- Chunk → Entity: 100% intact

### Overall Status: HEALTHY
```

## MCP Tools Used

- `analyze_schema` - Analise do schema Neo4j
- `analyze_collections` - Analise das collections Milvus
- `validate_consistency` - Validacao cross-database

## Schema Guidelines

### Recommended Structure

```
Neo4j (Relationships)          Milvus (Vectors)
├── Document                   ├── documents
│   └── HAS_CHUNK → Chunk     │   ├── id (= Chunk.id)
│                              │   ├── vector
├── Entity                     │   └── metadata
│   ├── MENTIONS ← Chunk      │
│   └── RELATED_TO → Entity   └── (outras collections)
```

### Best Practices

| Metric | Recommended | Current |
|--------|-------------|---------|
| Node types | 3-7 | Check |
| Relationship types | 5-15 | Check |
| Index coverage | 100% | Check |
| Constraint coverage | All PKs | Check |

## Related Commands

- `/ingerir` - Adicionar dados
- `/buscar` - Consultar dados
- `/health` - Status dos servicos
