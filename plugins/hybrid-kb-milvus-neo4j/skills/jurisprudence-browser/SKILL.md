# Jurisprudence Browser - Busca de Jurisprudencia via Agent Browser

Skill para busca automatizada de jurisprudencia em tribunais brasileiros usando Vercel Agent Browser.

## Quando Usar

Use esta skill quando precisar:
- Buscar jurisprudencia diretamente nos sites dos tribunais
- Acessar STF, STJ, TST, TRT-4, TJSP, JusBrasil
- Navegar e extrair decisoes de sites juridicos
- Automatizar pesquisas em bases de jurisprudencia

## Prerequisitos

O servico agent-browser deve estar rodando:
```bash
docker-compose up agent-browser
```

API disponivel em: `http://localhost:3100`

## API Endpoints

### Verificar Saude
```bash
curl http://localhost:3100/health
```

### Listar Tribunais Disponiveis
```bash
curl http://localhost:3100/courts
```

Tribunais suportados:
- **stf**: Supremo Tribunal Federal
- **stj**: Superior Tribunal de Justica
- **tst**: Tribunal Superior do Trabalho
- **trt4**: TRT 4a Regiao (RS)
- **tjsp**: Tribunal de Justica de Sao Paulo
- **jusbrasil**: JusBrasil

### Busca em Tribunal Especifico
```bash
curl -X POST http://localhost:3100/search/stf \
  -H "Content-Type: application/json" \
  -d '{"query": "adicional de periculosidade", "perspective": "defesa"}'
```

### Busca Multi-Tribunal
```bash
curl -X POST http://localhost:3100/search/multi \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vinculo empregaticio motorista aplicativo",
    "courts": ["stf", "stj", "tst"],
    "perspective": "julgamento"
  }'
```

## Comandos Agent Browser Disponiveis

### Navegacao
```bash
# Abrir URL
curl -X POST http://localhost:3100/open -d '{"url": "https://stf.jus.br"}'

# Fechar navegador
curl -X POST http://localhost:3100/close
```

### Snapshot e Interacao
```bash
# Obter snapshot da pagina (elementos com refs @e1, @e2, etc)
curl http://localhost:3100/snapshot?interactive=true

# Clicar em elemento
curl -X POST http://localhost:3100/click -d '{"ref": "@e5"}'

# Preencher campo
curl -X POST http://localhost:3100/fill -d '{"ref": "@e3", "value": "dano moral trabalhista"}'

# Pressionar tecla
curl -X POST http://localhost:3100/press -d '{"key": "Enter"}'
```

### Capturas
```bash
# Screenshot
curl "http://localhost:3100/screenshot?path=/tmp/resultado.png&full=true"

# Scroll
curl -X POST http://localhost:3100/scroll -d '{"direction": "down", "amount": 500}'
```

## Fluxo de Busca Completo

### Exemplo: Buscar no STF

1. Iniciar busca:
```bash
curl -X POST http://localhost:3100/search/stf \
  -d '{"query": "adicional insalubridade grau maximo"}'
```

2. Analisar snapshot retornado e identificar elementos

3. Preencher campo de busca:
```bash
curl -X POST http://localhost:3100/fill \
  -d '{"ref": "@e3", "value": "adicional insalubridade grau maximo"}'
```

4. Submeter busca:
```bash
curl -X POST http://localhost:3100/click -d '{"ref": "@e5"}'
```

5. Aguardar e capturar resultados:
```bash
curl -X POST http://localhost:3100/wait -d '{"text": "resultados", "timeout": 10000}'
curl http://localhost:3100/snapshot?interactive=true
```

6. Capturar screenshot:
```bash
curl "http://localhost:3100/screenshot?path=/tmp/stf_resultados.png&full=true"
```

## Integracao com Sistema 3-Perspectiva

Ao buscar jurisprudencia, especifique a perspectiva:

```json
{
  "query": "dano moral trabalhista quantum",
  "perspective": "defesa"  // ou "acusacao" ou "julgamento"
}
```

O sistema retornara resultados filtrados conforme a perspectiva:
- **defesa**: Apenas jurisprudencia favoravel ao cliente
- **acusacao**: Apenas jurisprudencia desfavoravel (riscos)
- **julgamento**: Toda jurisprudencia com analise imparcial

## Exemplo de Uso em Claude Code

```javascript
// Buscar jurisprudencia sobre adicional de periculosidade
const response = await fetch('http://localhost:3100/search/tst', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'adicional periculosidade base calculo',
    perspective: 'defesa'
  })
});

const data = await response.json();
console.log(data.snapshot);
// Analise o snapshot para identificar elementos e continuar navegacao
```

## Troubleshooting

### Container nao inicia
```bash
# Verificar logs
docker logs hybrid-kb-agent-browser

# Reconstruir
docker-compose build agent-browser
docker-compose up -d agent-browser
```

### Chromium nao instala
O Dockerfile ja inclui instalacao automatica. Se falhar:
```bash
docker exec -it hybrid-kb-agent-browser npx playwright install chromium
```

### Timeout em sites
Alguns tribunais podem ter protecao anti-bot. Use delays:
```bash
# Aguardar apos navegacao
curl -X POST http://localhost:3100/wait -d '{"text": ".", "timeout": 5000}'
```

## Notas de Seguranca

- O servico roda em container isolado
- Screenshots sao salvos em volume temporario
- Nao armazena credenciais ou dados sensiveis
- Use apenas para pesquisa juridica legitima
