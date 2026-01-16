# Command: /buscar

Executa buscas no sistema Hybrid Knowledge Base.

## Usage

```
/buscar <query>
/buscar --vector <query>
/buscar --graph <cypher>
/buscar --hybrid <query>
/buscar --multihop <entity>
```

## Description

Este comando executa buscas no sistema GraphRAG hibrido, suportando:
- Busca vetorial semantica (Milvus)
- Busca estrutural em grafo (Neo4j)
- Busca hibrida combinando ambos
- Raciocinio multi-hop

## Arguments

| Argument | Description |
|----------|-------------|
| `<query>` | Query em linguagem natural |
| `--vector` | Forca busca vetorial |
| `--graph` | Executa query Cypher |
| `--hybrid` | Forca busca hibrida |
| `--multihop` | Inicia travessia multi-hop |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--top-k` | 5 | Numero de resultados |
| `--provider` | google | Provedor de embedding |
| `--collection` | documents | Colecao Milvus |
| `--filter` | - | Filtro de metadados |
| `--max-hops` | 3 | Maximo de hops (multi-hop) |
| `--expand` | true | Expandir contexto via grafo |

## Search Modes

### Vector Search (Semantico)

Busca por similaridade de significado usando embeddings.

```
/buscar --vector Quais sao as melhores praticas de microservicos?
```

*Indicadores*: "similar a", "relacionado a", "sobre"

### Graph Search (Estrutural)

Busca usando queries Cypher no Neo4j.

```
/buscar --graph MATCH (d:Document)-[:HAS_CHUNK]->(c) RETURN d.title, count(c)
```

*Indicadores*: "quem", "quando", "autor de", relacoes explicitas

### Hybrid Search (Combinado)

Combina vector search + graph expansion para contexto rico.

```
/buscar --hybrid Como o trabalho de Hinton influenciou transformers?
```

*Indicadores*: queries complexas, multiplas entidades

### Multi-hop Reasoning

Travessia em cadeia para descobrir conexoes.

```
/buscar --multihop "Geoffrey Hinton" --max-hops 4
```

## Examples

### Example 1: Busca simples

```
/buscar arquitetura de sistemas distribuidos
```

### Example 2: Busca com filtro

```
/buscar machine learning --filter "doc_type == 'technical'" --top-k 10
```

### Example 3: Query Cypher

```
/buscar --graph "MATCH (e:Entity {type: 'PERSON'})-[:AUTHORED]->(d:Document) RETURN e.name, count(d) ORDER BY count(d) DESC"
```

### Example 4: Multi-hop

```
/buscar --multihop "Deep Learning" --max-hops 3 --filter-rel "CITES,RELATED_TO"
```

## Output

```markdown
## Search Results

### Query Analysis
- Original: arquitetura de sistemas distribuidos
- Strategy: hybrid
- Provider: Google

### Results (5 found)

#### 1. [Score: 0.92] Microservices Architecture Guide
**Source**: internal-docs
**Relevance**: high

> Este documento descreve os principios fundamentais de arquitetura
> de microservicos para sistemas distribuidos modernos...

**Graph Context**:
- Related entities: Kubernetes, Docker, API Gateway
- Relationships: DISCUSSES (3), CITES (2)

#### 2. [Score: 0.87] Distributed Systems Patterns
**Source**: arxiv
**Relevance**: high

> Padroes de design para sistemas distribuidos incluindo...

---

### Reasoning Chain
```
Query → Vector (5 chunks) → Graph Expand → 3 related entities → Rerank
```

### Performance
- Vector search: 45ms
- Graph expansion: 78ms
- Total: 123ms
```

## MCP Tools Used

- `vector_search` - Para busca semantica
- `graph_search` - Para queries Cypher
- `hybrid_search` - Para busca combinada
- `multi_hop_reasoning` - Para travessia multi-hop

## Query Routing (Automatico)

O sistema automaticamente classifica a query:

| Indicator | Route |
|-----------|-------|
| "similar to", "like", "about" | vector |
| "who", "when", "authored by" | graph |
| Complex, multiple entities | hybrid |
| "through", "connected to" | multi_hop |

## Related Commands

- `/ingerir` - Adicionar documentos a base
- `/schema` - Ver estrutura do grafo
- `/health` - Status dos servicos
