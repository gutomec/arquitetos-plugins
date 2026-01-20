# /buscar-jurisprudencia

Busca jurisprudencia em tribunais brasileiros usando Agent Browser.

## Uso

```
/buscar-jurisprudencia [termo] --tribunal=[stf|stj|tst|trt4|tjsp] --perspectiva=[defesa|acusacao|julgamento]
```

## Exemplos

```bash
# Buscar no STF
/buscar-jurisprudencia adicional de periculosidade --tribunal=stf

# Buscar no TST com perspectiva de defesa
/buscar-jurisprudencia dano moral trabalhista --tribunal=tst --perspectiva=defesa

# Buscar em multiplos tribunais
/buscar-jurisprudencia vinculo empregaticio motorista aplicativo --tribunal=stf,stj,tst
```

## Workflow

$ARGUMENTS

1. Verificar se agent-browser esta rodando:
```bash
curl -s http://localhost:3100/health
```

2. Se nao estiver rodando, orientar:
```bash
docker-compose up -d agent-browser
```

3. Executar busca no(s) tribunal(is) especificado(s)

4. Para cada tribunal:
   - Abrir pagina de busca
   - Preencher termo de busca
   - Submeter busca
   - Aguardar resultados
   - Capturar snapshot
   - Extrair jurisprudencia relevante
   - Capturar screenshot

5. Compilar resultados

6. Fechar navegador

7. Retornar resultados no formato JSON estruturado

## Tribunais Disponiveis

| Tribunal | Descricao |
|----------|-----------|
| stf | Supremo Tribunal Federal |
| stj | Superior Tribunal de Justica |
| tst | Tribunal Superior do Trabalho |
| trt4 | TRT 4a Regiao (Rio Grande do Sul) |
| tjsp | Tribunal de Justica de Sao Paulo |
| jusbrasil | Portal JusBrasil |

## Perspectivas 3-P

| Perspectiva | Descricao |
|-------------|-----------|
| defesa | Filtra apenas jurisprudencia favoravel |
| acusacao | Filtra apenas jurisprudencia desfavoravel |
| julgamento | Apresenta tudo com analise imparcial |

## Output Esperado

```json
{
  "termo_busca": "...",
  "tribunais": ["stf", "tst"],
  "perspectiva": "defesa",
  "resultados": [
    {
      "tribunal": "TST",
      "tipo": "sumula",
      "identificacao": "Sumula 191",
      "ementa": "...",
      "url": "https://...",
      "impacto": "favoravel"
    }
  ],
  "screenshots": ["/tmp/stf_busca.png"]
}
```
