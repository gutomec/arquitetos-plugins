---
description: Inicia o processo completo de criacao de uma landing page de alta conversao
---

# /criar-landing

## Objetivo

Este comando inicia o processo completo de criacao de uma landing page matadora, convocando o sistema multi-agente de especialistas.

## Uso

```
/criar-landing $ARGUMENTS
```

Onde `$ARGUMENTS` pode ser uma breve descricao do que voce quer promover, ou deixe em branco para uma conversa guiada.

## Exemplos

```
/criar-landing curso de programacao para iniciantes
/criar-landing software de gestao financeira para PMEs
/criar-landing
```

## Processo de Execucao

### Passo 1: Ativar Orquestrador

Convoque o agente `landing-orchestrator` usando o Task tool:

```
Task: Convocar landing-orchestrator para iniciar discovery
```

O orquestrador vai:
1. Conversar com o usuario para entender o projeto
2. Coletar informacoes sobre produto, publico, tom de voz
3. Salvar brief em arquivo

### Passo 2: Sequencia de Especialistas

Apos o discovery, o orquestrador convoca em sequencia:

1. *copywriter-supreme*
   - Input: Brief do discovery
   - Output: Copy de todas as secoes

2. *ui-designer-2026*
   - Input: Copy + preferencias visuais
   - Output: Design specification

3. *animator-60fps*
   - Input: Design specs
   - Output: Codigo de animacoes

4. *backend-builder*
   - Input: Requisitos de lead capture
   - Output: API + Admin dashboard

5. *landing-integrator*
   - Input: Todos os outputs
   - Output: Projeto Next.js completo

### Passo 3: Entrega Final

O integrador entrega:
- Projeto Next.js funcional
- Instrucoes de instalacao
- Comandos para rodar localmente
- Setup do admin

## Output Esperado

```
landing-page/
├── src/
│   ├── app/
│   │   ├── page.tsx          # Landing page
│   │   ├── admin/            # Dashboard
│   │   └── api/              # API routes
│   ├── components/           # Componentes React
│   └── lib/                  # Utilities
├── package.json
├── tailwind.config.ts
└── README.md
```

## Dicas

- Quanto mais detalhes voce fornecer no discovery, melhor o resultado
- Tenha em mente seu publico-alvo antes de comecar
- Prepare depoimentos e numeros se tiver
- Defina cores se ja tiver identidade visual

## Validacoes

Antes de finalizar, o sistema valida:
- [ ] Todos os textos estao completos
- [ ] Animacoes rodam a 60fps
- [ ] API de leads funciona
- [ ] Admin dashboard operacional
- [ ] Responsivo em mobile
