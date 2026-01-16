# Skill: Embedding Selection

Guia para escolher entre provedores de embedding (Google vs Cohere) no sistema Hybrid Knowledge Base.

## Overview

O sistema suporta dois provedores de embedding de alta qualidade. Esta skill ajuda a escolher o mais adequado para cada caso de uso.

## Provedores Disponíveis

### Google (text-embedding-004)

| Caracteristica | Valor |
|----------------|-------|
| *Modelo* | text-embedding-004 |
| *Dimensoes* | 768 |
| *Max tokens* | 2048 |
| *Task types* | RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, SEMANTIC_SIMILARITY |
| *Idiomas* | 100+ idiomas |
| *Custo* | ~$0.00025/1K tokens |

*Pontos fortes*:
- Alta qualidade para ingles e portugues
- Boa separacao semantica
- Otimizado para retrieval
- Integracao nativa com Gemini

### Cohere (embed-v4)

| Caracteristica | Valor |
|----------------|-------|
| *Modelo* | embed-v4 |
| *Dimensoes* | 1024 |
| *Max tokens* | 512 |
| *Input types* | search_document, search_query, classification |
| *Idiomas* | 100+ idiomas |
| *Custo* | ~$0.0001/1K tokens |

*Pontos fortes*:
- Excelente multilingue
- Custo mais baixo
- Bom para classificacao
- Compression nativa (binary, int8)

## Decision Matrix

```
                    ┌─────────────────────────────────────────┐
                    │         EMBEDDING SELECTION             │
                    └─────────────────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
    ┌───────────────┐        ┌───────────────┐        ┌───────────────┐
    │   Quality     │        │     Cost      │        │   Features    │
    │   Priority    │        │   Priority    │        │   Priority    │
    └───────────────┘        └───────────────┘        └───────────────┘
            │                         │                         │
            ▼                         ▼                         ▼
        GOOGLE                    COHERE                   DEPENDS
   text-embedding-004           embed-v4              (ver detalhes)
```

## When to Use Each

### Use Google (text-embedding-004) quando:

1. *Qualidade e prioridade maxima*
   - Documentos criticos de negocios
   - Bases de conhecimento empresariais
   - Conteudo juridico/regulatorio

2. *Contexto longo*
   - Chunks > 512 tokens
   - Documentos tecnicos extensos

3. *Integracao com Gemini*
   - Usando Gemini para geracao
   - Ecossistema Google Cloud

4. *Retrieval de precisao*
   - Quando recall/precision sao criticos
   - Documentacao tecnica

### Use Cohere (embed-v4) quando:

1. *Custo e prioridade*
   - Alto volume de documentos
   - Orcamento limitado
   - POCs e prototipacao

2. *Classificacao*
   - Categorizacao de documentos
   - Routing de queries

3. *Compressao necessaria*
   - Storage limitado
   - Latencia critica

4. *Multilingue intensivo*
   - Muitos idiomas misturados
   - Traducao cruzada

## Configuration Examples

### Google Setup

```python
import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)

# Para documentos (ingestao)
result = genai.embed_content(
    model="models/text-embedding-004",
    content=text,
    task_type="RETRIEVAL_DOCUMENT"
)
embedding = result['embedding']  # 768 dims

# Para queries (busca)
result = genai.embed_content(
    model="models/text-embedding-004",
    content=query,
    task_type="RETRIEVAL_QUERY"
)
```

### Cohere Setup

```python
import cohere

co = cohere.Client(COHERE_API_KEY)

# Para documentos (ingestao)
response = co.embed(
    texts=[text],
    model="embed-v4",
    input_type="search_document"
)
embedding = response.embeddings[0]  # 1024 dims

# Para queries (busca)
response = co.embed(
    texts=[query],
    model="embed-v4",
    input_type="search_query"
)
```

## Hybrid Strategy

### Dual Embedding (Producao)

```python
async def get_dual_embedding(text: str) -> dict:
    """Gera embeddings de ambos provedores."""
    google_emb = await google_embed(text)
    cohere_emb = await cohere_embed(text)

    return {
        "google": google_emb,  # Para retrieval primario
        "cohere": cohere_emb   # Para fallback/comparacao
    }
```

### Fallback Strategy

```python
async def get_embedding_with_fallback(text: str) -> list:
    """Google como primario, Cohere como fallback."""
    try:
        return await google_embed(text)
    except Exception as e:
        logger.warning(f"Google failed: {e}, falling back to Cohere")
        return await cohere_embed(text)
```

### A/B Testing

```python
def select_provider(query: str) -> str:
    """Seleciona provider baseado em caracteristicas da query."""

    # Queries curtas: Cohere (mais rapido)
    if len(query) < 100:
        return "cohere"

    # Queries tecnicas: Google (maior precisao)
    technical_keywords = ["api", "code", "function", "error"]
    if any(kw in query.lower() for kw in technical_keywords):
        return "google"

    # Default: Google
    return "google"
```

## Performance Comparison

### Latency

| Provider | p50 | p95 | p99 |
|----------|-----|-----|-----|
| Google | 50ms | 120ms | 200ms |
| Cohere | 40ms | 100ms | 150ms |

### Quality (MTEB Benchmark)

| Provider | Retrieval | Classification | Clustering |
|----------|-----------|----------------|------------|
| Google | 68.5 | 72.3 | 45.2 |
| Cohere | 67.2 | 74.1 | 46.8 |

### Cost (per 1M tokens)

| Provider | Standard | With Compression |
|----------|----------|------------------|
| Google | $0.25 | N/A |
| Cohere | $0.10 | $0.025 (binary) |

## Best Practices

### DO

1. *Consistencia*
   - Use o mesmo provider para documento e query
   - Nao misture embeddings de provedores diferentes

2. *Task type correto*
   - RETRIEVAL_DOCUMENT para ingestao
   - RETRIEVAL_QUERY para busca
   - Nunca use tipos genericos

3. *Batch quando possivel*
   - Agrupe embeddings para reduzir latencia
   - Max batch: 100 textos

4. *Cache embeddings*
   - Armazene embeddings gerados
   - Evite re-calcular

### DON'T

1. *Nao misture dimensoes*
   - Google (768) e Cohere (1024) sao incompativeis
   - Cada collection deve ter dimensao fixa

2. *Nao ignore rate limits*
   - Google: 1500 req/min
   - Cohere: 10000 req/min

3. *Nao use texto muito longo*
   - Trunque ou chunkeie antes de embedar
   - Respeite limites de tokens

## Troubleshooting

### Erro: Dimensoes incompativeis

*Causa*: Mistura de provedores na mesma collection
*Solucao*: Criar collections separadas ou padronizar provider

### Erro: Rate limit exceeded

*Causa*: Muitas requisicoes simultaneas
*Solucao*: Implementar backoff exponencial e batching

### Erro: Embeddings de baixa qualidade

*Causa*: Task type incorreto
*Solucao*: Usar RETRIEVAL_DOCUMENT/QUERY em vez de generico

### Erro: Custo alto

*Causa*: Re-embedding desnecessario
*Solucao*: Implementar cache de embeddings
