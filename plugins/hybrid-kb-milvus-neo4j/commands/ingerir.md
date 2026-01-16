# Command: /ingerir

Ingere documentos no sistema Hybrid Knowledge Base.

## Usage

```
/ingerir <conteudo_ou_path>
/ingerir --batch <diretorio>
/ingerir --url <url>
```

## Description

Este comando processa e ingere documentos no sistema GraphRAG hibrido, realizando:
1. Chunking semantico do texto
2. Geracao de embeddings (Google ou Cohere)
3. Armazenamento vetorial no Milvus
4. Criacao de nodes e relacionamentos no Neo4j

## Arguments

| Argument | Description |
|----------|-------------|
| `<conteudo>` | Texto do documento a ser ingerido |
| `<path>` | Caminho para arquivo (PDF, MD, TXT) |
| `--batch <dir>` | Processa todos arquivos de um diretorio |
| `--url <url>` | Baixa e processa documento de URL |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--provider` | google | Provedor de embedding (google, cohere) |
| `--collection` | documents | Nome da colecao Milvus |
| `--chunk-size` | 400 | Tamanho do chunk em caracteres |
| `--overlap` | 80 | Overlap entre chunks |
| `--extract-entities` | true | Extrair entidades para o grafo |
| `--title` | - | Titulo do documento |
| `--source` | - | Fonte/origem do documento |

## Examples

### Example 1: Ingerir texto direto

```
/ingerir Este e um documento sobre machine learning.
O aprendizado de maquina e uma area da IA...
```

### Example 2: Ingerir arquivo

```
/ingerir /path/to/documento.pdf
```

### Example 3: Ingerir com opcoes

```
/ingerir /path/to/documento.md --provider cohere --chunk-size 300 --title "Guia de ML"
```

### Example 4: Batch ingestion

```
/ingerir --batch /path/to/documentos/
```

### Example 5: Ingerir de URL

```
/ingerir --url https://example.com/documento.pdf
```

## Output

```markdown
## Document Ingestion Report

**Status**: Success
**Document ID**: abc123def456
**Title**: Guia de ML

### Processing Stats
- Original size: 15,000 chars
- Chunks created: 38
- Avg chunk size: 395 chars
- Overlap: 20%

### Embedding
- Provider: Google (text-embedding-004)
- Dimensions: 768
- Time: 2.3s

### Storage
- Milvus: 38 vectors inserted
- Neo4j: 1 Document + 38 Chunk nodes

### Entities Extracted
- Concepts: 12
- Organizations: 3
- Topics: 5
```

## MCP Tools Used

- `ingest_document` - Para ingestao individual
- `ingest_batch` - Para processamento em lote
- `build_knowledge_graph` - Para extracao de entidades

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| File not found | Path invalido | Verificar caminho do arquivo |
| Unsupported format | Formato nao suportado | Usar PDF, MD, TXT, HTML |
| API rate limit | Muitas requisicoes | Aguardar e tentar novamente |
| Connection error | Database offline | Verificar com /health |

## Related Commands

- `/buscar` - Buscar documentos ingeridos
- `/schema` - Analisar schema apos ingestao
- `/health` - Verificar status dos servicos
