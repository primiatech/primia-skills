# primia-design

Versão 1.1.0
Autor: Primia

Skill que gera um design system completo (tokens, style guide visual e componentes base) a partir de imagens, PDFs e URLs de referência. Roda em sandbox Claude.ai e em Claude Code local nas três plataformas (Windows, macOS, Linux).

## Índice

- [O que essa skill faz](#o-que-essa-skill-faz)
- [Pré-requisitos](#pré-requisitos)
- [Como instalar](#como-instalar)
- [Como usar](#como-usar)
- [Onde os arquivos ficam salvos](#onde-os-arquivos-ficam-salvos)
- [Resolução de problemas](#resolução-de-problemas)
- [Estrutura dos arquivos](#estrutura-dos-arquivos)

## O que essa skill faz

Você manda uma referência visual (PDF de manual de marca, link de um site, imagem com a paleta) e a skill devolve um design system pronto pra usar em projeto real.

A skill faz tudo de forma autônoma. Não pergunta nada. Você descreve o que quer em português coloquial e ela executa o pipeline inteiro: extrai cores, tipografia, espaçamentos, gera escalas semânticas, checa contraste WCAG, e empacota tudo em formatos prontos.

O que ela entrega ao final:

- design-tokens.json no padrão W3C
- tokens.css com as CSS variables
- tokens.scss com SCSS variables e maps
- tailwind.config.js pronto pra Tailwind
- figma-tokens.json pra plugin Tokens Studio do Figma
- styleguide.html visual completo, abre no navegador
- 6 componentes HTML prontos (button, input, card, badge, alert, typography)
- README.md, decisions.md e conflicts.md explicando cada decisão

## Pré-requisitos

Você precisa ter Python 3.10 ou mais novo instalado. Pra confirmar, abra o terminal e rode:

```
python --version
```

Se aparecer algo tipo `Python 3.10.x` ou maior, está tudo certo. Se der erro de comando não encontrado, no Windows tente:

```
py --version
```

Se nem `python` nem `py` funcionarem, é sinal de que o Python não está instalado. Baixe em [python.org/downloads](https://www.python.org/downloads/) e durante a instalação marque a caixa "Add Python to PATH".

Você também vai precisar do `pip` (que vem junto com o Python na maioria dos casos) e de uma conexão com a internet pra baixar as dependências e o navegador headless.

## Como instalar

### Passo 1: extrair a skill

Clone o repositório `primiatech/primia-skills` ou descompacte o arquivo `primia-design.zip` que você recebeu, dentro do diretório de skills do seu Claude Code. O caminho típico é:

- macOS/Linux: `~/.claude/skills/primia-design/`
- Windows: `%USERPROFILE%\.claude\skills\primia-design\`

Confirme que dentro da pasta `primia-design/` existem os arquivos `SKILL.md`, `scripts/requirements.txt`, e os subdiretórios `references/` e `assets/`.

### Passo 2: criar virtualenv

Um virtualenv isola as dependências dessa skill das outras coisas que você roda na máquina. É opcional mas muito recomendado.

Entre no diretório da skill:

```
cd ~/.claude/skills/primia-design
```

Crie o ambiente:

```
python -m venv .venv
```

Ative (escolha conforme seu sistema):

- Windows (cmd ou PowerShell): `.venv\Scripts\activate`
- macOS e Linux: `source .venv/bin/activate`

Quando o ambiente está ativo, você vê `(.venv)` no início do prompt do terminal.

### Passo 3: instalar dependências

Com o virtualenv ativo, rode:

```
pip install -r scripts/requirements.txt
```

Isso baixa as bibliotecas Python que a skill usa. Demora um pouco na primeira vez. Se você está em sandbox Claude.ai e não pode usar virtualenv, rode:

```
pip install --break-system-packages -r scripts/requirements.txt
```

### Passo 4: instalar o Chromium do Playwright

Esse passo é obrigatório e fácil de esquecer. O Playwright é uma biblioteca que controla um navegador headless pra extrair tokens de sites SPA (React, Vue, Next.js, etc). Pra ele funcionar, você precisa baixar o navegador uma vez:

```
python -m playwright install chromium
```

Isso baixa cerca de 150MB e só precisa rodar uma única vez por máquina. Se você pular esse passo, qualquer URL de site moderno vai falhar com erro `Executable doesn't exist`.

### Passo 5: confirmar instalação

Pra ter certeza que tudo deu certo, rode (com o virtualenv ativo):

```
python -c "import requests, bs4, PIL, numpy, sklearn, pypdf, playwright; print('OK')"
```

Se aparecer `OK`, está pronto. Se der erro de import, volte pro passo 3 e veja a mensagem de erro.

## Como usar

A skill é detectada automaticamente pelo Claude quando você faz um pedido que envolve referências visuais. Você não precisa chamar ela pelo nome. Frases que disparam a skill:

- "Faz um design system desse PDF aqui"
- "Extrai a paleta desse site: https://exemplo.com"
- "Pega as cores e fontes dessa imagem"
- "Cria um style guide baseado no manual de marca anexo"
- "Tira a identidade visual dessa landing page"
- "Replica o visual da Stripe num design system"
- "Tenho 3 referências (PDF, site e logo). Monta um design system unificado, e usa o PDF como fonte da verdade"

Você pode misturar fontes na mesma conversa. A skill aceita PDF, imagem e URL juntos e funde tudo aplicando uma hierarquia. Por padrão, PDF tem prioridade, depois URL, depois imagem. Você pode mudar isso no próprio pedido falando coisas como "use o site como referência principal".

A skill nunca pergunta antes de rodar. Ela escolhe um default razoável, executa, e explica cada decisão num arquivo `decisions.md` que vem no resultado.

## Onde os arquivos ficam salvos

Em sandbox Claude.ai, os outputs vão pra `/mnt/user-data/outputs/<nome-do-projeto>/`.

Em ambiente local, depende do que você (ou o Claude) configurou. Defaults razoáveis:

- macOS e Linux: `~/Documentos/design-system/outputs/<nome-do-projeto>/`
- Windows: `C:\Users\<seu-usuario>\Documentos\design-system\outputs\<nome-do-projeto>\`
- Se nada foi especificado: `./design-system/outputs/<nome-do-projeto>/` na pasta atual

Dentro da pasta do projeto, você vai encontrar:

```
<nome-do-projeto>/
├── README.md            (resumo do que foi gerado)
├── decisions.md         (cada decisão e o porquê)
├── conflicts.md         (divergências entre fontes, se houve)
├── styleguide.html      (visualização completa, abre no navegador)
├── tokens/              (5 formatos de tokens)
├── components/          (6 componentes HTML/CSS prontos)
└── brand-assets/        (logos e imagens extraídos)
```

O primeiro arquivo a olhar sempre é o `styleguide.html`. Abra ele no navegador pra ver o resultado visual. Depois leia `decisions.md` pra entender o que a skill decidiu.

## Resolução de problemas

### Erro: "Executable doesn't exist" ao processar URL

Significa que o navegador Chromium do Playwright não foi instalado. Rode:

```
python -m playwright install chromium
```

A skill cai num modo de fallback (extração estática) quando isso acontece, mas resultados de sites SPA ficam parciais. Instalar o Chromium resolve.

### Erro: ModuleNotFoundError

Significa que alguma dependência não foi instalada. Confira que o virtualenv está ativo (você deve ver `(.venv)` no terminal) e rode de novo:

```
pip install -r scripts/requirements.txt
```

Se persistir, veja qual módulo está faltando na mensagem de erro e instale ele especificamente:

```
pip install <nome-do-modulo>
```

### Erro: "externally managed environment" no pip

Acontece em distribuições Linux modernas (Ubuntu 23+, Debian 12+) e em macOS quando você não está num virtualenv. A solução é criar um virtualenv como descrito no passo 2 da instalação.

Se não puder usar virtualenv (sandbox Claude.ai, por exemplo), use a flag:

```
pip install --break-system-packages -r scripts/requirements.txt
```

### Erro: comando 'python' não encontrado (Windows)

Tente `py` no lugar de `python`. No Windows, dependendo de como o Python foi instalado, o comando pode ser um ou outro. Os comandos do passo de instalação ficam:

```
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r scripts/requirements.txt
py -m playwright install chromium
```

### A skill não está sendo detectada quando faço o pedido

Confirme que a pasta `primia-design/` está dentro do diretório de skills do Claude Code (`~/.claude/skills/` ou `%USERPROFILE%\.claude\skills\`) e que o arquivo `SKILL.md` existe lá dentro com o frontmatter intacto.

Em alguns casos pode ser necessário reiniciar o Claude Code pra ele detectar skills novas.

### O styleguide.html abre mas algumas cores estão erradas

O styleguide carrega as CSS variables do `tokens/tokens.css`. Se você abriu o styleguide.html sozinho (movendo de pasta), pode ter quebrado o caminho relativo. Mantenha os arquivos no diretório original ou abra o styleguide a partir da pasta do projeto.

## Estrutura dos arquivos

```
primia-design/
├── SKILL.md                      (instruções da skill pro Claude)
├── README.md                     (este arquivo)
├── .gitignore
├── scripts/
│   ├── requirements.txt          (dependências Python)
│   ├── extract_from_url.py
│   ├── extract_from_image.py
│   ├── extract_from_pdf.py
│   ├── merge_sources.py
│   ├── analyze_colors.py
│   ├── analyze_typography.py
│   ├── analyze_spacing.py
│   ├── check_contrast.py
│   ├── generate_outputs.py
│   └── generate_styleguide.py
├── references/                   (documentação consultiva)
│   ├── token-naming.md
│   ├── intermediate-format.md
│   ├── conflict-resolution.md
│   ├── output-formats.md
│   ├── modular-scales.md
│   └── component-templates.md
└── assets/
    ├── components/               (templates dos componentes HTML)
    ├── readme-template.md        (template do README do output)
    └── decisions-template.md     (template do decisions.md do output)
```

Os scripts em `scripts/` são puros, recebem todos os caminhos via flags (--input, --output, etc) e podem rodar manualmente fora do contexto de skill. Os arquivos em `references/` são consultados pelo Claude quando ele precisa entender alguma convenção. Os arquivos em `assets/` são templates copiados pro output final.

Pra ver a documentação completa do funcionamento da skill, abra o `SKILL.md`.
