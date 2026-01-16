# Media Forge

Sistema multi-agente para geracao de imagens e videos de alta qualidade usando as melhores tecnologias de 2026.

## Instalacao

```bash
# Adicionar marketplace (se ainda nao adicionou)
/plugin marketplace add seu-usuario/arquitetos-plugins

# Instalar plugin
/plugin install media-forge@arquitetos-plugins
```

## Configuracao

Configure as variaveis de ambiente antes de usar:

```bash
export FAL_KEY="sua-chave"           # fal.ai/dashboard/keys
export GEMINI_API_KEY="sua-chave"    # aistudio.google.com/apikey
export OPENAI_API_KEY="sua-chave"    # platform.openai.com/api-keys
```

## Comandos Disponiveis

| Comando | Descricao |
|---------|-----------|
| `/gerar-imagem` | Cria imagens a partir de texto |
| `/gerar-video` | Cria videos a partir de texto |
| `/animar-imagem` | Transforma imagem em video |
| `/batch-imagens` | Gera multiplas imagens em paralelo |
| `/editar-imagem` | Modifica imagens existentes |

## Exemplos

```bash
# Gerar imagem
/gerar-imagem um gato laranja dormindo em uma almofada

# Gerar video com audio (Veo 3)
/gerar-video --audio cena de cafe com conversa entre amigos

# Batch de imagens
/batch-imagens gato dormindo | cachorro correndo | passaro voando

# Animar foto
/animar-imagem ./retrato.jpg pessoa sorrindo suavemente
```

## Modelos Suportados

### Imagem
- Imagen 4 (fotorrealismo)
- FLUX Kontext (texto em imagem)
- Ideogram V3 (design grafico)
- DALL-E 3 (criatividade)
- Nano Banana Pro (versatil)

### Video
- Veo 3 (com audio nativo)
- Kling 2.1 Master (movimento fluido)
- Luma Ray 2 (cinematico)

## Licenca

MIT
