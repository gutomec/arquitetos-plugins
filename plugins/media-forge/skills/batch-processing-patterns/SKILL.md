---
name: batch-processing-patterns
description: Padroes e estrategias para processamento em lote de imagens e videos. Use quando precisar gerar multiplas midias em paralelo.
allowed-tools:
  - Read
  - Write
  - TodoWrite
---

# Batch Processing Patterns

Guia de padroes para processamento eficiente de multiplas imagens e videos.

---

## Conceitos Fundamentais

### Paralelismo vs Sequencial

*Paralelo*: Multiplas requisicoes simultaneas
- Mais rapido
- Requer gerenciamento de rate limits
- Pode falhar parcialmente

*Sequencial*: Uma requisicao por vez
- Mais lento
- Mais seguro
- Facil de debugar

### Rate Limits por Modelo

| Modelo | Req/min | Max Paralelo |
|--------|---------|--------------|
| Imagen 4 | 60 | 5 |
| FLUX | 120 | 10 |
| Ideogram | 60 | 5 |
| Recraft | 100 | 8 |
| DALL-E 3 | 15 | 3 |
| Veo 3 | 20 | 3 |
| Kling | 30 | 3 |

---

## Padroes de Entrada

### Padrao 1: Lista Simples
```
prompt1
prompt2
prompt3
```

*Processamento*:
```javascript
const prompts = input.split('\n').filter(p => p.trim());
const results = await Promise.all(
  prompts.map(prompt => generateImage(prompt))
);
```

### Padrao 2: JSON Estruturado
```json
{
  "model": "imagen4",
  "settings": {
    "size": "16:9",
    "quality": "high"
  },
  "items": [
    {"prompt": "...", "id": "001"},
    {"prompt": "...", "id": "002"}
  ]
}
```

*Processamento*:
```javascript
const { model, settings, items } = JSON.parse(input);
const results = await batchProcess(items, model, settings);
```

### Padrao 3: Variacoes de Tema
```json
{
  "base_prompt": "A cat",
  "variations": [
    "sleeping on a couch",
    "playing with yarn",
    "looking out window"
  ],
  "model": "flux_dev"
}
```

*Processamento*:
```javascript
const fullPrompts = variations.map(v => `${base_prompt} ${v}`);
const results = await Promise.all(
  fullPrompts.map(prompt => generate(prompt, model))
);
```

### Padrao 4: Grid de Combinacoes
```json
{
  "subjects": ["cat", "dog", "rabbit"],
  "styles": ["realistic", "cartoon", "watercolor"],
  "model": "recraft_v3"
}
```

*Processamento*:
```javascript
const combinations = [];
for (const subject of subjects) {
  for (const style of styles) {
    combinations.push({ subject, style });
  }
}
// Gera 9 imagens (3x3)
```

---

## Estrategias de Execucao

### Estrategia 1: Chunked Parallel
*Dividir em grupos para respeitar rate limits*

```javascript
async function chunkedParallel(items, chunkSize, processor) {
  const results = [];

  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);
    const chunkResults = await Promise.all(
      chunk.map(item => processor(item))
    );
    results.push(...chunkResults);

    // Pausa entre chunks se necessario
    if (i + chunkSize < items.length) {
      await sleep(1000);
    }
  }

  return results;
}

// Uso
await chunkedParallel(prompts, 5, generateWithImagen4);
```

### Estrategia 2: Queue com Workers
*Fila de trabalho com N workers*

```javascript
async function queueWithWorkers(items, numWorkers, processor) {
  const queue = [...items];
  const results = [];
  const workers = [];

  async function worker() {
    while (queue.length > 0) {
      const item = queue.shift();
      if (item) {
        const result = await processor(item);
        results.push(result);
      }
    }
  }

  for (let i = 0; i < numWorkers; i++) {
    workers.push(worker());
  }

  await Promise.all(workers);
  return results;
}

// Uso: 5 workers processando em paralelo
await queueWithWorkers(prompts, 5, generateImage);
```

### Estrategia 3: Rate Limited
*Controle preciso de taxa*

```javascript
async function rateLimited(items, requestsPerMinute, processor) {
  const delay = 60000 / requestsPerMinute;
  const results = [];

  for (const item of items) {
    const start = Date.now();
    const result = await processor(item);
    results.push(result);

    const elapsed = Date.now() - start;
    if (elapsed < delay) {
      await sleep(delay - elapsed);
    }
  }

  return results;
}

// Uso: maximo 60 req/min
await rateLimited(prompts, 60, generateImage);
```

---

## Tratamento de Erros

### Padrao: Retry com Backoff Exponencial
```javascript
async function withRetry(fn, maxRetries = 3, baseDelay = 1000) {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        await sleep(delay);
      }
    }
  }

  throw lastError;
}

// Uso
const result = await withRetry(() => generateImage(prompt));
```

### Padrao: Fallback para Outro Modelo
```javascript
const fallbackChain = ['imagen4', 'flux_dev', 'sd35'];

async function withFallback(prompt, models) {
  for (const model of models) {
    try {
      return await generate(prompt, model);
    } catch (error) {
      console.log(`${model} falhou, tentando proximo...`);
    }
  }
  throw new Error('Todos os modelos falharam');
}
```

### Padrao: Partial Success
```javascript
async function batchWithPartialSuccess(items, processor) {
  const results = await Promise.allSettled(
    items.map(item => processor(item))
  );

  const successes = results
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value);

  const failures = results
    .filter(r => r.status === 'rejected')
    .map((r, i) => ({ index: i, error: r.reason }));

  return { successes, failures };
}
```

---

## Reporting de Progresso

### Estrutura de Report
```javascript
const report = {
  started: new Date().toISOString(),
  total: items.length,
  completed: 0,
  failed: 0,
  results: [],
  errors: [],

  update(result) {
    if (result.success) {
      this.completed++;
      this.results.push(result);
    } else {
      this.failed++;
      this.errors.push(result);
    }
    this.progress = `${this.completed + this.failed}/${this.total}`;
  },

  summary() {
    return {
      total: this.total,
      completed: this.completed,
      failed: this.failed,
      successRate: `${(this.completed / this.total * 100).toFixed(1)}%`,
      duration: Date.now() - new Date(this.started).getTime()
    };
  }
};
```

### Formato de Output
```markdown
## Resultado do Batch

**Total**: 10 itens
**Sucesso**: 9 (90%)
**Falha**: 1 (10%)
**Tempo**: 45 segundos

### Arquivos Gerados
1. ✓ output_001.png - "Cat sleeping"
2. ✓ output_002.png - "Dog running"
3. ✗ output_003.png - ERRO: Rate limit exceeded
...

### Erros
- Item 3: Rate limit - retry em 60s
```

---

## Templates de Batch

### Template: Variacoes de Produto
```json
{
  "type": "product_variations",
  "product": "smartphone",
  "angles": ["front", "back", "side", "45-degree"],
  "backgrounds": ["white", "gradient", "lifestyle"],
  "model": "imagen4",
  "settings": {
    "size": "1:1",
    "style": "product photography"
  }
}
```

### Template: Social Media Pack
```json
{
  "type": "social_pack",
  "content": "Summer promotion",
  "formats": [
    {"platform": "instagram_post", "size": "1:1"},
    {"platform": "instagram_story", "size": "9:16"},
    {"platform": "facebook_cover", "size": "16:9"},
    {"platform": "twitter", "size": "16:9"}
  ],
  "model": "ideogram_v3"
}
```

### Template: Video Series
```json
{
  "type": "video_series",
  "theme": "Product showcase",
  "episodes": [
    {"title": "Intro", "duration": 5, "style": "dramatic"},
    {"title": "Features", "duration": 10, "style": "informative"},
    {"title": "CTA", "duration": 5, "style": "energetic"}
  ],
  "model": "veo3"
}
```

---

## Otimizacao de Custos

### Estrategias
1. *Prototipo com modelo barato*: SD 3.5 ou Magi
2. *Producao com modelo premium*: Imagen 4 ou Veo 3
3. *Agrupar por modelo*: Menos overhead de conexao
4. *Cache de resultados*: Evitar duplicatas
5. *Batch sizing otimo*: Balancear velocidade vs custo

### Calculadora de Custo
```javascript
function estimateCost(items, model) {
  const costs = {
    imagen4: 0.04,
    imagen4_fast: 0.02,
    flux: 0.03,
    sd35: 0.01,
    dalle3: 0.04,
    veo3: 0.10,
    kling: 0.08
  };

  return items.length * (costs[model] || 0.05);
}
```
