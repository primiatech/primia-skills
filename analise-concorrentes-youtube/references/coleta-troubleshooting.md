# Coleta — Troubleshooting

Guia de problemas comuns na fase de coleta e como resolver. Leia quando algo falhar — a maioria dos erros tem solução conhecida.

## YouTube Data API

### `quotaExceeded` — cota esgotada

A API tem cota diária de **10.000 unidades por projeto** no plano gratuito. Custos típicos:

| Operação | Custo (unidades) |
|---|---|
| `channels.list` | 1 |
| `playlistItems.list` (50 vídeos) | 1 |
| `videos.list` (até 50 IDs) | 1 |
| `commentThreads.list` (100 comentários) | 1 |
| `search.list` | **100** |

**Estimativa por execução (Modo Padrão, 3 canais, 50 vídeos cada, top 10 com 150 comentários):**
- Resolução: 3 × 1 = 3
- Listagem de uploads: 3 × 1 = 3
- Listagem de vídeos: 3 × 1 = 3
- Estatísticas: 3 × (50/50) = 3
- Comentários: 3 × 10 × 2 (paginação) = 60

Total: ~72 unidades. **Cabe folgado** numa cota de 10k.

**Quando estoura mesmo assim:**
- Search da API (ao resolver canal pelo nome) custa 100 unidades cada — evite passar nomes vagos. Prefira `@handle` ou URL direta.
- Múltiplas execuções no mesmo dia somam — o reset é à meia-noite Pacific Time.

**Soluções:**
1. Esperar reset (00:00 PT = 04:00 ou 05:00 BRT, dependendo do horário de verão).
2. Usar outra API key (criar projeto novo no Google Cloud Console).
3. Pedir aumento de cota (formulário no Google Cloud, demora dias).
4. Rodar em Modo Sem-API com fallback yt-dlp (perde comentários).

### `commentsDisabled` — comentários desabilitados

Criador desabilitou comentários no vídeo específico. **Pule e siga** — não é erro fatal. Documente no relatório que tal vídeo ficou sem análise de comentário.

### Canal não encontrado

- Verifique se está usando o `@handle` correto (com arroba).
- Tente a URL completa: `https://www.youtube.com/@nomedocanal`.
- Cole o channel ID direto se tiver (formato `UC...` com 24 chars).
- Canais muito pequenos (<100 inscritos) às vezes não aparecem no `forHandle` — use `search.list` como fallback (já implementado).

## Transcrições

### "No transcripts found for this video"

Causas:
1. Criador desabilitou legendas automáticas (raro).
2. Vídeo é muito recente (legendas demoram horas pra serem geradas).
3. Vídeo está em idioma que a API não suporta auto-legenda.
4. Conteúdo do vídeo é majoritariamente música/sem fala.

**Solução**: o script tenta fallback com `yt-dlp`. Se ambos falharem:
- Pule o vídeo.
- Documente: "Transcrição indisponível para [video_id]".
- Análise daquele vídeo fica restrita a título + descrição + comentários.

### Transcrição vem em inglês quando o vídeo é em português

Acontece quando o YouTube classificou erroneamente o idioma. O script tenta `pt-BR` → `pt` → `en` em ordem. Se trouxer inglês, **traduza mentalmente** durante a análise mas **mantenha o original** no arquivo (transparência).

### Hook (primeiros 30s) saiu vazio

O `transcript-api` retorna timestamps em segundos. Vídeos onde o segmento 0 começa em `start=2.5` ou similar podem ter o filtro `start < 30` cortando demais — o script já trata isso, mas se acontecer, abra o `transcript_full.txt` e use os primeiros 80-100 caracteres como hook manualmente.

## yt-dlp (Modo Sem-API)

### Erro `Sign in to confirm you're not a bot`

YouTube as vezes exige verificação. Soluções:
1. Esperar 30-60 minutos.
2. Usar VPN/IP diferente.
3. Se persistir, é necessário usar a API oficial.

### Listing de canal vem incompleto

Em canais muito grandes, o `extract_flat` pode pular vídeos. Se você notar muito menos vídeos do que esperado, aumente `playlistend` no script (já configurado pra `max_videos`, mas em casos extremos vale subir).

### yt-dlp lento demais

A hidratação por vídeo (uma chamada por vídeo) é o gargalo. Em Modo Sem-API com 50 vídeos, demora ~3-5 minutos só nessa etapa. Considere reduzir `--max-videos` se o tempo for problema.

## Thumbnails

### `403 Forbidden` ao baixar

YouTube bloqueia user-agents suspeitos. O script já manda User-Agent de browser. Se persistir, é provavelmente rate limit — espere 5 min e re-rode.

### Thumbnail volta como imagem cinza/quebrada

O `maxresdefault.jpg` nem sempre existe (canal pequeno, vídeo antigo). O script faz fallback automático para `hqdefault` → `mqdefault`. Se nada funcionar, registre `null` e siga.

## Comentários

### Volume vem muito menor que o esperado

`order=relevance` na API só retorna comentários que o YouTube considera relevantes. Vídeos pequenos (poucos comentários totais) podem trazer só 20-30 mesmo pedindo 150. **Não é bug** — é feature do YouTube.

### Comentários todos parecem ser respostas (replies)

Verifique o campo `is_reply` — se true, é resposta a outro. O script já inclui top 3 replies por comentário-pai, mas se o cliente quer só comentários top-level, filtre por `is_reply == False`.

## Geração de entregáveis

### `.docx` muito grande (>50MB)

Provavelmente são as thumbnails embutidas. Reduza `width_cm` na função `add_image_safe` ou pule thumbnails pra ganhar tamanho.

### `.pptx` corrompido ao abrir

Geralmente é problema de imagem inválida. Verifique se as thumbnails baixaram corretamente — arquivos de 0 bytes quebram o pptx. O `download_thumbnails.py` valida tamanho mínimo (>1000 bytes), mas confira manualmente no diretório `thumbnails/`.

### `.xlsx` com colunas espremidas

Reabra com `autosize` ajustando o `max_width` no script. Padrão é 60-90 caracteres dependendo da aba — ajuste se necessário.

## Análise estratégica (Etapa 8)

### "Não consigo identificar padrão"

É possível que **não exista padrão**. Diga isso no relatório:

> "Os 10 vídeos top do canal X usam hooks variados sem dominância clara — possível indicação de que o canal está em fase de teste ou que a viralidade veio de fatores externos (distribuição, sazonalidade)."

Honestidade > forçar conclusão.

### Comentários todos genéricos ("ótimo vídeo")

Sinaliza dois cenários:
1. Audiência passiva (canal de entretenimento, não de transformação) → menos útil pra infoproduto.
2. Comentários comprados/bots → desconfie. Cheque se há padrão suspeito (mesmas frases curtas).

Documente no relatório: "Análise de avatar limitada para o canal X — comentários majoritariamente genéricos."
