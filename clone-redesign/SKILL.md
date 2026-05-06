---
name: clone-redesign
description: Clona e redesenha paginas web existentes. Use quando o usuario pedir para clonar, redesenhar, recriar ou fazer uma versao melhorada de uma pagina/site existente a partir de URL ou screenshot.
---

# Clone e Redesign de Paginas

Extrai conteudo completo, baixa assets e reconstroi paginas web com design system melhorado. Arquivo unico HTML com CSS inline, imagens locais, sem dependencias externas alem do Google Fonts.

## Quando Usar

- Usuario pede para clonar/copiar uma pagina
- Usuario pede redesign de uma pagina existente
- Usuario compartilha URL ou screenshot e quer uma versao nova
- Usuario quer recriar pagina de concorrente com estilo proprio

## Processo (6 Etapas)

### Etapa 1: Coletar Conteudo

Usar WebFetch na URL com dois prompts separados:

**Prompt 1 - Imagens:**
Extrair TODAS as URLs de imagens (img src, background-image, srcset, video poster, logos, webp/jpg/png)

**Prompt 2 - Conteudo:**
Extrair TODO o texto da pagina preservando estrutura de secoes (headings, paragrafos, botoes, labels, depoimentos, FAQ, precos, garantia, bio, footer)

Se a pagina for grande e o conteudo vier truncado, usar os HTMLs clonados locais (se existirem na pasta do cliente) para complementar.

### Etapa 2: Baixar Assets

Criar pasta de assets e baixar todas as imagens via curl:

```bash
mkdir -p "[pasta-projeto]/assets"
cd "[pasta-projeto]/assets"
curl -sL -o nome-descritivo.webp "URL_COMPLETA"
```

Regras de nomenclatura:
- Renomear para nomes descritivos (background-mobile.webp, g1-back.webp, selo-04.webp)
- Manter extensao original
- Verificar tamanho dos arquivos apos download (ls -la)

### Etapa 3: Revisar Assets Visuais

Ler as imagens baixadas com o Read tool para entender o conteudo visual:
- Fotos de pessoas (quem aparece, contexto)
- Screenshots de produto/plataforma
- Icones e selos
- Backgrounds e texturas

Isso informa onde usar cada imagem no redesign.

### Etapa 4: Escolher Design System

Perguntar ao usuario qual padrao visual usar, ou inferir do contexto:

- Se for cliente Julia/Luigi: usar `landing-julia-laranja` ou `landing-julia-pro-academy`
- Se for cliente Primia: usar `landing-primia`
- Se for outro cliente: perguntar ou criar padrao novo baseado nas cores/fontes extraidas

### Etapa 5: Construir Redesign

Gerar arquivo HTML unico com:

1. **CSS variables** do design system escolhido
2. **Estrutura de secoes** seguindo a ordem da pagina original
3. **Copy completa** da pagina original (preservar todo o texto, adaptar formatacao)
4. **Imagens locais** referenciadas como `assets/nome.webp`
5. **Componentes interativos** (FAQ accordion, scroll reveal, mascaras de input)
6. **Responsividade** completa (3-4 breakpoints)

O redesign DEVE:
- Preservar 100% do conteudo textual original
- Usar as imagens baixadas nos contextos corretos
- Melhorar a estrutura visual e hierarquia
- Remover dependencia de page builders (Elementor, WordPress)
- Carregar instantaneamente (HTML puro + CSS inline)
- Ser totalmente responsivo

O redesign NAO deve:
- Inventar conteudo que nao existe na pagina original
- Remover secoes sem pedir ao usuario
- Mudar precos, nomes ou dados factuais
- Adicionar funcionalidades que a pagina original nao tem (a menos que pedido)

### Etapa 6: Salvar e Informar

Salvar na pasta do cliente com nome descritivo:
```
clientes/[cliente]/[nome-projeto]/index.html
clientes/[cliente]/[nome-projeto]/assets/
```

Informar ao usuario:
- Caminho do arquivo
- Lista de secoes incluidas
- Diferencas do redesign vs original
- Quais imagens foram usadas e onde

## Checklist de Conteudo

Ao extrair de uma pagina de vendas/captura, garantir que capturou:

- [ ] Alert bar / urgencia
- [ ] Headline principal (H1)
- [ ] Sub-headline / descricao
- [ ] Prova social (numeros, depoimentos)
- [ ] Dores / pain points (lista completa)
- [ ] Diagnostico / virada emocional
- [ ] Comparacao (antes vs depois, ou vs concorrente)
- [ ] Historia de origem / bio do criador
- [ ] Conteudo do produto (modulos, fases, features)
- [ ] Ancoragem de preco (valor percebido)
- [ ] Oferta (preco real, parcelas, bonus)
- [ ] Trust badges (seguranca, garantia)
- [ ] Garantia (texto completo)
- [ ] FAQ (todas as perguntas E respostas)
- [ ] CTA final / fechamento
- [ ] Footer (links, creditos)

## Fallbacks

Se WebFetch falhar (403, timeout):
- Usar screenshots/PDFs que o usuario ja tenha
- Usar HTMLs clonados na pasta do cliente
- Pedir ao usuario para colar o conteudo manualmente

Se imagens falharem no download:
- Usar placeholder (div com background-color + texto descritivo)
- Informar ao usuario quais imagens faltaram
- Sugerir que o usuario baixe manualmente
