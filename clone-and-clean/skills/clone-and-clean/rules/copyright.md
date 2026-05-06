# Regras de copyright e uso ético

## O que a skill PODE fazer

- Clonar **estrutura HTML/CSS** de páginas de vendas (esqueleto é ideia, não proteção)
- Reproduzir **fontes livres** (Google Fonts, Bunny Fonts, OMGF)
- Baixar **imagens da página** pra uso pessoal/estudo de estrutura
- Extrair **copy** pra biblioteca pessoal de referência do usuário

## O que a skill NÃO pode fazer

- Reproduzir copy literalmente em páginas publicadas publicamente sem permissão
- Reutilizar fotos de pessoas reais (depoimentos, fotos da mentora) em lançamentos de outros clientes — essas são **sempre** placeholders a serem trocados
- Hospedar assets com marca/logotipo do cliente original em ambiente produtivo de terceiros
- Replicar depoimentos com nome, foto e @ de pessoas reais

## Comportamento seguro padrão

Ao gerar `clean/`:
- Fotos de pessoas (cris-*, daniela-*, wesley-*, ale-*) → renomear pra `depoimento-1.avif`, `mentora-principal.avif`, etc no template
- No README do `clean/`, incluir aviso explícito: **"Fotos de pessoas e nomes usados nos depoimentos são do cliente original. Substitua por materiais próprios antes de publicar."**
- No `copy.md`, incluir aviso: **"Este copy é do cliente {nome}. Use como referência de estrutura; adapte/reescreva pro seu cliente antes de publicar."**

## Dados pessoais identificáveis

Nunca extrair/persistir:
- Endereços físicos
- Números de documento (CPF, RG, CNPJ pessoal)
- E-mails pessoais (só corporativos do cliente, e mesmo assim marcar como TODO)
- Dados de cartão/pagamento

Se aparecerem no HTML (às vezes aparecem em código de terceiros), remover na captura.
