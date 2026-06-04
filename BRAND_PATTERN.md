# Padrão Editorial, Visual e Operacional — @grupo.supraam
> **Documento mestre de referência.** Atualizado a cada feature nova.
> Última atualização: 2026-06-03

---

## 1. Identidade Visual

### Paleta de cores (atualizada para casar com supraam.com.br)
| Cor | Hex | Uso |
|-----|-----|-----|
| Navy principal | `#0a2540` | Background principal (deep institutional) |
| Navy escuro | `#051529` | Sombra inferior do gradiente |
| Navy lighter | `#0e3357` | Topo do gradiente radial |
| Dourado principal | `#d4af5a` | Headlines de destaque, numeração, kicker, marca |
| Dourado suave | `#b8954a` | Variação para detalhes |
| Creme | `#f4ead5` | Corpo de texto sobre navy |
| Branco | `#ffffff` | Headlines principais |

### Tipografia
- **Headlines**: Playfair Display 700 (serifada, peso editorial)
- **Body / kicker / footer**: Inter 300/400/600 (sans-serif moderna)
- Tamanhos: hook=110px, content=68px, data=56px, body=30px, kicker=14px, footer=14px

### Elementos visuais
- Barra dourada fina de 8px no topo
- Círculos decorativos transparentes (5% opacidade) — um inferior direito (700x700), um superior esquerdo (500x500)
- Marca **SA** no canto inferior direito (56x56, borda dourada) + texto "SUPRA AM / SOLUÇÕES INTEGRADAS"
- Paginador `01 / 07` no canto inferior esquerdo, cor creme, opacidade 50%

---

## 2. Estrutura Editorial

### Pilares (3x/semana — editorial)
| Dia | Pilar | Função |
|-----|-------|--------|
| **Segunda 9h** | Técnico-regulatório | Autoridade. PDDE/FNDE, Resolução, Portaria 448, vedações, prestação de contas |
| **Quarta 13h** | Catálogo/produto | Conversão suave. "Como escolher", checklists, comparativos. SEM expor inventário |
| **Sexta 18h** | Mercado/regional | Posicionamento. Censo escolar, Norte, inclusão, logística fluvial |

### Frequência
**3x/semana** (não diário, não a cada 3 dias). Dias fixos > intervalo fixo.

### Horários
- BR: Seg 9h, Qua 13h, Sex 18h
- UTC: Seg 12h, Qua 16h, Sex 21h

### Pilar extra: NEWS (fura fila)
Quando aparece notícia gov.br relevante, vai pra `content/news_queue/` e publica antes da fila regular. Sem dia fixo.

---

## 3. Tipos de Slide

### `hook` (Capa)
Primeiro slide do carrossel. Vertical de impacto.
- Label "SUPRA AM" com linha dourada
- Headline grande Playfair (110px)
- Subhead em creme (32px, max 820px)
- Footer pequeno: "Carrossel — Supra AM"

### `content` (Conteúdo)
Slide intermediário com kicker + título + corpo.
- Kicker numerado em quadro com borda dourada: "1 / Subtema"
- Headline Playfair 68px
- Corpo Inter 30px, line-height 1.55, máx 880px de largura
- Suporta `\n` pra quebra de linha

### `data` ou `list` (Lista numerada)
Para destacar 3-5 itens.
- Kicker + headline (56px)
- Lista com numeração em Playfair dourado (01, 02, 03)
- Divisor dourado fino entre itens

### `comparison` (Comparativo 3 colunas)
Para comparar opções (ex: Lousa vs Projetor vs TV).
- 3 colunas com fundo translúcido e borda dourada
- Nome de cada coluna em Playfair dourado
- Linhas de comparação em creme

### `program` (Programa Supra AM) ⭐
Slide de oferta institucional — penúltimo do carrossel (antes do CTA).
- Kicker "PROGRAMA SUPRA AM" com linha dourada nas pontas
- Headline 60px Playfair (nome do kit/programa)
- Descrição curta (26px, creme, 300 weight)
- 4 bullets com checkmark dourado
- Link `supraam.com.br` em badge com borda dourada

### `news` (Notícia gov.br) ⭐ NOVO
Slide especial pra posts de notícia detectados pelo monitor.
- Badge dourado pulsante "NOVIDADE FNDE/MEC"
- Headline Playfair 70px (título da publicação)
- Resumo creme 28px (max 880px)
- Linha de fonte: "Fonte: GOV.BR · DD MMM YYYY"

### `cta` (Chamada pra ação)
Último slide do carrossel.
- Centralizado verticalmente
- Headline pergunta direta
- Body com instrução **+ menção a `supraam.com.br`** ("Visite supraam.com.br pra ver todos os kits.")
- **Em posts NEWS**: também menciona "Cadastre-se na newsletter"
- Botão dourado com `@grupo.supraam`

---

## 4. Estrutura de Carrossel

### Carrossel editorial padrão (6-8 slides)
```
1. Hook (capa)
2-5. Content / Data / List (corpo educativo)
6. Program (kit/programa específico do supraam.com.br)
7. CTA (DM ou comentário + supraam.com.br)
```

### Carrossel NEWS (4-5 slides)
```
1. News (badge + headline + fonte)
2. Content opcional (contexto se houver 2o parágrafo)
3. Content (impacto pra escola — gen�rico mas certeiro)
4. Program (Conte com a Supra AM)
5. CTA (Blog + Newsletter)
```

### Card único (1 slide)
Tipo `list` (5 itens em geral). Direto, sem build-up. Footer aponta pra `supraam.com.br`.

---

## 5. Caption (Legenda)

### Estrutura editorial
```
[Linha 1 — hook curto, máx 80 caracteres]

[Parágrafo 1 — contexto do problema/tema]

[Parágrafo 2 — o que o post entrega]

[Linha de CTA — "Salve" / "Comenta" / "Chama no direct"]

Conheça todos os nossos kits em supraam.com.br

[Hashtags — 5 a 8, sempre quebra de linha antes]
```

### Estrutura NEWS
```
Novidade FNDE/MEC: [título da publicação]

[descrição se houver]

Fonte: [GOV.BR / fonte oficial]
Análise completa no blog: supraam.com.br/blog/[slug]
Cadastre-se na newsletter em supraam.com.br pra receber novidades como essa no e-mail.

Conheça nossos kits em supraam.com.br

[Hashtags fixas: #FNDE #PDDE #NovidadeFNDE etc.]
```

> **Site CTA é padrão fixo em toda caption** — drives traffic pro supraam.com.br. Nunca remover.

---

## 6. Hashtags

### Base (sempre presentes em todo post)
`#PDDE #FNDE #GestaoEscolar #EducacaoAmazonas`

### Por pilar (adicionar 2-4 do pilar do post)
**Técnico**: `#ComprasPublicas #Portaria448 #ResolucaoFNDE #UnidadeExecutora`
**Catálogo**: `#MobiliarioEscolar #TecnologiaNaEducacao #SRM #InclusaoEscolar #BrinquedoPedagogico`
**Regional**: `#EducacaoNoNorte #CensoEscolar #EscolaRibeirinha #AmazonasEducacao #LogisticaEducacional`
**News**: `#NovidadeFNDE #EducacaoNoNorte` (base + variação por tema)

---

## 7. Restrições editoriais

❌ **NÃO postar:**
- Fotos de equipe, escritório, processos internos
- Números internos (qtd clientes, faturamento, equipe)
- "Vendemos pra escola X" / nomes de clientes
- Memes, GIFs, gírias
- Conteúdo de "promoção / desconto"

✅ **PODE postar:**
- Conteúdo técnico autoral
- Comparativos
- Dados públicos (Censo INEP, IBGE, FNDE)
- Referências a kits/programas do supraam.com.br via slide `program`
- Notícias .gov.br + grandes mídias (curadoria automática)
- Opiniões técnicas com responsabilidade

---

## 8. Arquitetura técnica do sistema

### Repos
| Repo | URL | Conteúdo |
|------|-----|----------|
| supra-instagram-bot | https://github.com/VictorRamonOl/supra-instagram-bot | Sistema de publicação (público pra raw URLs funcionarem) |
| Site_Fnde | https://github.com/VictorRamonOl/Site_Fnde | Site Next.js (privado), hospedado Vercel |

### Workflows GitHub Actions
| Workflow | Cron | Função |
|----------|------|--------|
| `publish.yml` | Seg 12h UTC / Qua 16h UTC / Sex 21h UTC + workflow_dispatch | Publica próximo da fila no Instagram |
| `monitor.yml` | Toda hora `:15` + workflow_dispatch | Busca Google News, gera post de notícia, commita nos 2 repos, dispara publish |

### Pastas
```
Insta_Supra/
├── BRAND_PATTERN.md             ← este documento
├── SETUP_GITHUB.md              ← setup do PAT/secrets
├── .env                         ← credenciais locais (gitignored)
├── .github/workflows/
│   ├── publish.yml              ← cron de publish
│   └── monitor.yml              ← cron de news monitor
├── scripts/
│   ├── publish_instagram.py     ← publica 1 post na API IG
│   ├── publish_next_approved.py ← worker: pega próximo da fila (news_queue ou approved)
│   ├── refresh_token.py         ← renova token long-lived
│   ├── generate_slides.py       ← renderiza HTML→PNG
│   ├── approve_batch.py         ← move pending→approved em lote
│   ├── build_review.py          ← gera review HTML
│   ├── build_feed_preview.py    ← simula grid do feed IG
│   ├── templates/slide_template.html ← CSS dos slides
│   └── news/
│       ├── monitor.py           ← busca Google News RSS
│       └── generate_post.py     ← gera slides + blog entry de notícia
├── state/
│   └── seen_articles.json       ← URLs já processadas
├── content/
│   ├── _specs/
│   │   └── batch_001.json       ← spec dos 12 posts do batch atual
│   ├── editorial_calendar_v1.md ← calendário editorial humano
│   ├── pending/                 ← rascunhos aguardando aprovação
│   ├── approved/                ← fila regular (Seg/Qua/Sex)
│   ├── news_queue/              ← fila prioritária (fura ordem)
│   └── published/               ← histórico do que já foi pro ar
```

### Secrets (GitHub Actions)
| Secret | Valor | Onde gerar |
|--------|-------|------------|
| `INSTAGRAM_USER_ID` | `17841437968295675` | Painel Meta SupraBot |
| `INSTAGRAM_ACCESS_TOKEN` | `IGAA...` long-lived 60d | Painel Meta → Use case → Generate tokens |
| `INSTAGRAM_APP_SECRET` | `781bfe34f29fa3c18a3a0a728c23de32` | Painel Meta → App secret |
| `GH_REPO_PAT` | `github_pat_...` | https://github.com/settings/personal-access-tokens/new |

---

## 9. Sistema de Notícias (NEW)

### Como funciona
1. **Cron a cada hora** (`monitor.yml` `:15min`)
2. Faz 10 buscas Google News RSS com queries do nosso nicho (FNDE+PDDE, Educação Conectada, SRM, etc.)
3. **Filtra** por:
   - Fonte confiável (`.gov.br`, agenciabrasil, G1, Folha, Valor, Estadão, Globo, etc.)
   - Relevância (precisa ter pelo menos 1 keyword: fnde, pdde, escolas, repasse, etc.)
   - Blocklist (exclui: vestibular, ENEM, ensino superior, particular)
4. **Dedup** via `state/seen_articles.json`
5. **Processa máximo 1 nova por execução** (evita spam)
6. **Gera post Instagram**: 4-5 slides PNG + post.json em `content/news_queue/`
7. **Adiciona entrada no blog**: anexa em `Site_FNDE/src/data/news.ts`
8. **Commita nos 2 repos** automaticamente
9. **Dispara `publish.yml`** pra postar no IG imediatamente

### Onde ajustar comportamento
- Keywords: `scripts/news/monitor.py` → variável `QUERIES`
- Trust domains: `scripts/news/monitor.py` → `TRUSTED_DOMAINS`
- Blocklist: `scripts/news/monitor.py` → `BLOCKLIST`
- Template do post: `scripts/news/generate_post.py` → `build_slides()` e `build_caption()`

---

## 10. Newsletter (próximas etapas)

### Estado atual
- Site tem form de inscrição (`Site_FNDE/src/components/blog/NewsletterForm.tsx`)
- Rota `api/newsletter/route.ts` recebe email e envia notificação via **Resend** pra equipe
- **NÃO armazena leads** (TODO no código original)

### Plano de evolução (não implementado ainda)
1. **Persistir leads**: 
   - Opção A: arquivo JSON `Site_FNDE/src/data/subscribers.json` (simples, sem DB)
   - Opção B: Resend Audiences (lista nativa do Resend)
2. **Broadcast no news**: 
   - Quando `monitor.yml` gera post de notícia, também dispara email via Resend pros inscritos
   - Email link → blog post da notícia (`supraam.com.br/blog/[slug]`)
3. **Newsletter form CTA**: 
   - Já mencionado em todo slide CTA dos posts NEWS
   - Já mencionado em toda caption NEWS

---

## 11. Sequência de produção (batches futuros)

Pra produzir um novo batch editorial (ex: batch 002):

1. Abrir Claude Code e dizer: **"produz batch 002 com mais 12 posts seguindo o BRAND_PATTERN.md"**
2. Claude lê este arquivo + memória do projeto + identifica gaps no calendário
3. Escreve specs em `content/_specs/batch_NNN.json`
4. Roda `generate_slides.py` pra produzir PNGs
5. Roda `build_review.py` + `build_feed_preview.py`
6. Usuário aprova em lote via `approve_batch.py --all`
7. Cron `publish.yml` publica conforme cronograma

---

## 12. Comandos de referência

```powershell
# Sempre setar PATH (terminal novo)
$env:Path += ";C:\Program Files\GitHub CLI"

# === BATCH EDITORIAL ===

# Gerar slides de um batch
python scripts/generate_slides.py --batch content/_specs/batch_001.json

# Só alguns (--only)
python scripts/generate_slides.py --batch content/_specs/batch_001.json --only 03,06

# Página de revisão
python scripts/build_review.py --open

# Feed preview
python scripts/build_feed_preview.py

# Aprovar (move pending → approved)
python scripts/approve_batch.py --ids 01,02,03
python scripts/approve_batch.py --all
python scripts/approve_batch.py --reject 05

# === NEWS ===

# Buscar notícias manualmente (dry-run)
python -m scripts.news.monitor --dry-run --limit 5

# Buscar e gerar 1 post de notícia
python -m scripts.news.monitor --limit 1

# === PUBLISH ===

# Publicar manualmente
python scripts/publish_next_approved.py

# Renovar token (auto, mas pode forçar)
python scripts/refresh_token.py --force

# === GITHUB ACTIONS ===

# Ver histórico
gh run list --workflow=publish.yml
gh run list --workflow=monitor.yml

# Disparar manualmente
gh workflow run publish.yml
gh workflow run monitor.yml

# Watch em tempo real
gh run watch

# Pausar/voltar
gh workflow disable publish.yml
gh workflow enable publish.yml

# Atualizar token Instagram
gh secret set INSTAGRAM_ACCESS_TOKEN --body "NOVO_TOKEN"
```

---

## 13. Troubleshooting

### "API access blocked" no publish
Token foi invalidado. Solução:
1. Abrir `https://developers.facebook.com/apps/947575161589456/use_cases/customize/?use_case_enum=MANAGE_MESSAGING_AND_CONTENT_ON_INSTAGRAM`
2. Seção 2 "Generate access tokens" → Remove e Add account de novo
3. Logar como @grupo.supraam, autorizar
4. Copiar token IGAA novo
5. No PowerShell:
   ```powershell
   gh secret set INSTAGRAM_ACCESS_TOKEN --body "NOVO_TOKEN"
   gh workflow run publish.yml
   ```
6. Atualizar `.env` local com mesmo token + data
7. Rodar `python scripts/refresh_token.py --force` pra trocar pra long-lived

### Cron não disparou
1. Verificar workflows ativos: `gh workflow list`
2. Se "disabled": `gh workflow enable publish.yml`
3. Ver últimos runs: `gh run list --workflow=publish.yml`

### News monitor não acha nada
1. Limpar state: `rm state/seen_articles.json`
2. Rodar dry-run: `python -m scripts.news.monitor --dry-run --limit 5`
3. Se ainda vazio, Google News pode ter mudado HTML — ver `monitor.py` queries

### Token vai expirar (60 dias)
- `scripts/publish_next_approved.py` chama `refresh_token.py` antes de cada publish
- Refresh automático quando token tem >25 dias
- Se passar de 60 dias sem refresh, precisa gerar novo no painel Meta

---

## 14. Métricas de sucesso (primeiros 90 dias)

- Crescimento: 16 → 300 seguidores
- Engajamento médio: >4% (alto pra B2B)
- Salvos: >20% das curtidas (sinal de "vou usar isso")
- DMs qualificadas: >2/mês de gestores reais
- Inscritos newsletter: meta a definir após implementação

---

## 15. Histórico de mudanças

| Data | O que mudou |
|------|-------------|
| 2026-06-02 | Setup inicial: Meta API, token long-lived, 12 posts batch 001, GitHub Actions cron, repo público pra raw URLs |
| 2026-06-02 | Adicionado slide `program` (referência kit Supra) em todos os carrosseis |
| 2026-06-02 | Ajustado navy pra `#0a2540` (mais próximo do site) |
| 2026-06-02 | Adicionado CTA `supraam.com.br` em captions + CTA slides + footer single cards |
| 2026-06-03 | **Sistema de Notícias**: monitor Google News RSS, gerador de post + blog entry, fila prioritária, cross-repo push |
| 2026-06-03 | Tipo de slide `news` adicionado |
| 2026-06-03 | Token regenerado após "API access blocked"; post 02 Logística publicado |
| 2026-06-03 | CTA newsletter adicionado em posts NEWS (slide + caption) |
