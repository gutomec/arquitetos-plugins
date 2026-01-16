# Skill: Chunking Strategies

Guia completo de estrategias de chunking para o sistema Hybrid Knowledge Base.

## Overview

Esta skill fornece orientacao sobre como dividir documentos em chunks otimizados para embedding e retrieval no sistema GraphRAG com Milvus e Neo4j.

## When to Use

- Antes de ingerir novos documentos
- Quando resultados de busca nao sao satisfatorios
- Ao otimizar performance de retrieval
- Quando trabalhando com novos tipos de documentos

## Chunking Strategies

### 1. Fixed-Size Chunking

*Quando usar*: FAQs, documentos curtos, conteudo homogeneo

```python
chunk_size = 500  # caracteres
chunk_overlap = 50  # 10% overlap
```

*Pros*:
- Simples e previsivel
- Baixo custo computacional
- Chunks uniformes

*Cons*:
- Pode quebrar contexto semantico
- Nao respeita estrutura do documento

### 2. Recursive Character Splitting (Recomendado)

*Quando usar*: Documentos estruturados, textos tecnicos, maioria dos casos

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80,
    separators=["\n\n", "\n", ". ", ", ", " ", ""]
)
```

*Pros*:
- Preserva estrutura hierarquica
- Respeita paragrafos e sentencas
- Bom balance entre contexto e tamanho

*Cons*:
- Chunks de tamanho variavel
- Requer ajuste por tipo de documento

### 3. Semantic Chunking

*Quando usar*: Documentos complexos, qualidade maxima de retrieval

```python
from langchain_experimental.text_splitter import SemanticChunker

chunker = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)
```

*Pros*:
- Chunks semanticamente coerentes
- Melhor qualidade de retrieval (+30% recall)
- Contexto preservado

*Cons*:
- Custo computacional alto (gera embeddings intermediarios)
- Latencia maior na ingestao

### 4. Document-Aware Chunking

*Quando usar*: PDFs estruturados, documentos com headers/sections

```python
# Por tipo de documento
strategies = {
    "markdown": split_by_headers,
    "pdf": split_by_pages_and_sections,
    "code": split_by_functions,
    "legal": split_by_articles
}
```

## Configuration Guide

### Chunk Size Selection

| Content Type | Recommended Size | Overlap |
|--------------|------------------|---------|
| FAQs | 200-300 chars | 10% |
| Technical docs | 400-500 chars | 15-20% |
| Legal documents | 500-600 chars | 20% |
| Narratives | 600-800 chars | 10% |
| Code | By function/class | 0% |

### Token Considerations

```python
# Aproximacao: 1 token ≈ 4 caracteres (ingles)
# Para portugues: 1 token ≈ 3.5 caracteres

# Limites de contexto
max_context_tokens = 8192  # Typical LLM
chunks_per_query = 5
tokens_per_chunk = max_context_tokens / chunks_per_query  # ~1600

# Convertendo para caracteres
ideal_chunk_chars = tokens_per_chunk * 3.5  # ~560 chars para PT
```

## Best Practices

### DO

1. *Testar com dados reais*
   - Avalie retrieval quality com queries reais
   - Compare diferentes configuracoes

2. *Ajustar por dominio*
   - Documentos tecnicos: chunks menores, mais overlap
   - Narrativas: chunks maiores, menos overlap

3. *Preservar metadados*
   - Mantenha referencia ao documento pai
   - Inclua posicao/indice do chunk

4. *Considerar re-chunking*
   - Documentos importantes podem ter multiplas granularidades

### DON'T

1. *Nao usar one-size-fits-all*
   - Cada tipo de documento pode precisar de configuracao diferente

2. *Nao ignorar estrutura*
   - Headers, listas, tabelas sao sinais importantes

3. *Nao fragmentar demais*
   - Chunks muito pequenos perdem contexto
   - Minimo: 100 caracteres

4. *Nao esquecer overlap*
   - Sem overlap, informacao nas bordas se perde

## Troubleshooting

### Problema: Resultados irrelevantes

*Causa provavel*: Chunks muito grandes
*Solucao*: Reduzir chunk_size para 300-400 chars

### Problema: Contexto insuficiente

*Causa provavel*: Chunks muito pequenos
*Solucao*: Aumentar chunk_size ou overlap

### Problema: Chunks quebram no meio de sentencas

*Causa provavel*: Separadores inadequados
*Solucao*: Usar RecursiveCharacterTextSplitter com separadores corretos

### Problema: Ingestao lenta

*Causa provavel*: Semantic chunking muito granular
*Solucao*: Usar recursive splitting em vez de semantic

## Examples

### Example 1: Documento Tecnico

```python
# Para documentacao de API
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=100,  # 25% - maior overlap para tecnico
    separators=[
        "\n## ",      # Headers principais
        "\n### ",     # Subheaders
        "\n\n",       # Paragrafos
        "\n",         # Linhas
        ". ",         # Sentencas
        " "           # Palavras
    ]
)
```

### Example 2: Documento Legal

```python
# Para contratos/regulamentos
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=120,  # 20%
    separators=[
        "\nArt.",     # Artigos
        "\n§",        # Paragrafos legais
        "\n\n",       # Secoes
        ". ",         # Sentencas
    ]
)
```

### Example 3: Codigo Fonte

```python
from langchain.text_splitter import Language

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=0  # Sem overlap para codigo
)
```

## Metrics

### Como Avaliar Qualidade do Chunking

1. *Retrieval Precision*: % de chunks recuperados que sao relevantes
2. *Retrieval Recall*: % de chunks relevantes que foram recuperados
3. *Context Coverage*: Informacao necessaria esta presente?
4. *Chunk Coherence*: Cada chunk faz sentido isoladamente?

### Targets

| Metric | Good | Excellent |
|--------|------|-----------|
| Precision | > 70% | > 85% |
| Recall | > 60% | > 80% |
| Avg chunk tokens | 100-400 | 200-300 |
