# SYSTEM_MASTER.md — Bíblia do Sistema @grupo.supraam

> **O QUE É ISTO**: Documento mestre consolidado com TUDO que construímos até hoje (2026-06-05) para alavancar a conta @grupo.supraam.
> Toda regra, lógica, schedule, fix e decisão estratégica vive aqui.
> Quando precisar lembrar de algo, leia este arquivo PRIMEIRO. Se faltar detalhe, abra os arquivos específicos referenciados.

---

## 0. Índice rápido

1. [Visão geral do sistema](#1-visão-geral)
2. [Marca, voz e público](#2-marca-voz-e-público)
3. [Stack técnica](#3-stack-técnica)
4. [Arquitetura de arquivos](#4-arquitetura-de-arquivos)
5. [Credenciais e tokens](#5-credenciais-e-tokens)
6. [GitHub Actions (todos os crons)](#6-github-actions-todos-os-crons)
7. [Sistema de POSTS (carrosseis)](#7-sistema-de-posts-carrosseis)
8. [Sistema de STORIES](#8-sistema-de-stories)
9. [Sistema de NEWS MONITOR](#9-sistema-de-news-monitor)
10. [Cross-repo Site_FNDE + Vercel](#10-cross-repo-site_fnde--vercel)
11. [Regras de linguagem (acessibilidade)](#11-regras-de-linguagem-acessibilidade)
12. [Fixes históricos (não repetir)](#12-fixes-históricos-não-repetir)
13. [Estratégia 20k seguidores](#13-estratégia-20k-seguidores)
14. [Pendências e roadmap](#14-pendências-e-roadmap)
15. [Comandos úteis (cheat sheet)](#15-comandos-úteis-cheat-sheet)

---

## 1. Visão geral

**O QUE ESTÁ NO AR HOJE (2026-06-05):**

| Camada | Frequência | Status |
|--------|------------|--------|
| Posts editoriais (carrossel) | Seg 9h + Qua 13h + Sex 18h BR | RODANDO |
| Stories | Todo dia 9h + 18h BR (2x/dia) | RODANDO |
| News monitor (gov.br + mídia) | Toda hora `:15` | RODANDO |
| Auto-refresh token IG | Antes de cada publish | RODANDO |
| Blog Site_FNDE sync | Quando news monitor acha algo | RODANDO |
| Vercel deploy | Push no Site_FNDE → auto | RODANDO |
| **Google Search Console** | Sitemap processado (112 URLs) | RODANDO |
| **Bing Webmaster** | Sitemap processado (112 URLs) | RODANDO |
| **IndexNow → Bing/Yandex** | Auto-notifica em cada news nova | RODANDO |
| Newsletter broadcast | — | PENDENTE |
| Reels pipeline | — | PLANEJADO (REELS_PLAN.md) |
| Meta Ads | — | PLANEJADO p/ 05/07/2026 (ADS_PROPOSTA.md) |

**Volume mensal de presença gerada automaticamente:**
- 12 posts (carrosseis 1080×1080)
- 60 stories (1080×1920)
- até 4 notícias (hard-cap 1/semana)
- = **~75 publicações/mês sem mão humana**

---

## 2. Marca, voz e público

### Identidade @grupo.supraam
- **Empresa**: Supra AM | Soluções Integradas
- **B2G/B2B** materiais escolares (escolar + tecnologia + mobiliário + brinquedos + sistemas)
- **Foco**: escolas públicas + secretarias do Norte (AM/PA/RO/RR/AC/AP/TO)
- **Programas-chave**: PDDE, PDDE Equidade, PDDE Conectividade, FNDE, Fundeb, SRM (Sala de Recursos Multifuncionais)
- **Site**: supraam.com.br · CTA padrão `/orcamento`

### Paleta visual (idêntica ao site)
| Token | Hex | Uso |
|-------|-----|-----|
| `--navy` | `#0a2540` | Bg principal, headers |
| `--gold` | `#d4af5a` | Destaque, botões, dados |
| `--cream` | `#f4ead5` | Texto sobre navy |

> Definidos em `scripts/templates/slide_template.html` e `scripts/templates/story_template.html`.

### Voz
- **Tom**: técnico-acessível. Diretor de escola entende sem dicionário.
- **Sem jargão "burocratês"**: ver §11.
- **Conversão**: cada peça termina sinalizando o site / DM.
- **Tutorial > opinião**: gestor procura passo-a-passo, não "achismo".

### Público-alvo
- Diretor escolar (decisor direto)
- Secretário municipal de educação
- UEx / Caixa Escolar (responsável pela prestação de contas)
- Coordenador pedagógico

---

## 3. Stack técnica

| Camada | Tecnologia | Por quê |
|--------|------------|---------|
| Render slides | Playwright headless Chromium | HTML→PNG fiel, sem Photoshop |
| Hospedagem imagens | Raw GitHub URLs | Catbox bloqueou GH Actions; raw é estável |
| API IG | Graph API v23.0 via `graph.instagram.com` | Instagram Login (não Facebook Login) |
| Token | Long-lived 60 dias + auto-refresh | `ig_refresh_token` endpoint |
| Cron | GitHub Actions schedule | Free tier, zero infra |
| News scrape | Google News RSS | Sem chave de API, robusto |
| Blog | Next.js Site_FNDE no Vercel | Auto-deploy a cada push |
| State | JSON em `state/` | Simples, versionado |

**Tudo Python 3.13 + `requests` + `python-dotenv` + `playwright`.**

---

## 4. Arquitetura de arquivos

```
D:\Documents\0. Automações\Insta_Supra\
├── .env                              # Secrets locais (NUNCA commitar)
├── .github/workflows/
│   ├── publish.yml                   # Cron 3x/sem posts
│   ├── stories.yml                   # Cron 2x/dia stories
│   └── monitor.yml                   # Cron horário news
├── content/
│   ├── _specs/
│   │   ├── batch_002.json            # 12 posts ATIVOS (conversão)
│   │   └── stories.json              # 60 specs (s001-s060)
│   ├── _archive_batch_001/           # Batch antigo (12 editoriais)
│   ├── pending/                      # Posts gerados aguardando review
│   ├── approved/                     # Posts liberados pro worker
│   ├── published/                    # Histórico publicado
│   ├── stories_queue/                # Stories gerados aguardando publish
│   └── images/                       # PNGs renderizados
├── scripts/
│   ├── publish_instagram.py          # Core IG API
│   ├── publish_next_approved.py      # Worker (lê queue + approved)
│   ├── refresh_token.py              # Auto-refresh
│   ├── generate_slides.py            # HTML→PNG carrosseis
│   ├── approve_batch.py              # CLI de aprovação
│   ├── build_feed_preview.py         # Preview HTML feed
│   ├── build_review.py               # HTML de review batch
│   ├── stories/
│   │   ├── generate_story.py         # Renderiza 1 story PNG
│   │   └── publish_story.py          # Commit+push+publish story
│   ├── news/
│   │   ├── monitor.py                # Google News scraper + dedup
│   │   └── generate_post.py          # Gera post IG + blog entry
│   └── templates/
│       ├── slide_template.html       # 1080x1080
│       └── story_template.html       # 1080x1920
├── state/
│   ├── seen_articles.json            # URLs já vistas pelo monitor
│   ├── published_stories.json        # IDs já publicados
│   └── last_token_refresh.json       # Timestamp último refresh
├── _external/Site_FNDE/              # Checkout cross-repo (só em CI)
├── SYSTEM_MASTER.md                  # ESTE ARQUIVO (leia primeiro)
├── BRAND_PATTERN.md                  # Detalhes visuais/editoriais
├── ADS_PROPOSTA.md                   # Plano Meta Ads
├── REELS_PLAN.md                     # Arquitetura futura Reels
└── SETUP_GITHUB.md                   # Setup PAT + gh CLI
```

---

## 5. Credenciais e tokens

### Vivem no `.env` LOCAL e em **GitHub Secrets** do repo:

| Secret | Origem | Onde usar |
|--------|--------|-----------|
| `INSTAGRAM_USER_ID` | `17841437968295675` | Todos os scripts IG |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived (60d) | Todos os scripts IG |
| `INSTAGRAM_APP_SECRET` | `781bfe34f29fa3c18a3a0a728c23de32` | Validação webhook (futuro) |
| `META_APP_ID` | `947575161589456` | Meta App "SupraBot" |
| `INSTAGRAM_APP_ID` | `1310123487938476` | Instagram side |
| `GH_REPO_PAT` | Fine-grained PAT | Checkout cross-repo Site_FNDE |
| `INSTAGRAM_TOKEN_REFRESHED_AT` | `2026-06-03` | Marker pro auto-refresh |

### Regra de refresh
- Token expira em 60 dias.
- `refresh_token.py` roda ANTES de cada publish.
- Se idade > 25 dias, chama `GET /refresh_access_token?grant_type=ig_refresh_token`.
- Atualiza `.env` e `INSTAGRAM_TOKEN_REFRESHED_AT`.

### Como regerar manualmente (se invalidar)
1. https://developers.facebook.com → App "SupraBot"
2. Instagram → API Setup → **Add account** (não "Generate Token" — esse falha)
3. Reautoriza conta `grupo.supraam`
4. Copia token novo → cola em `.env` LOCAL → `gh secret set INSTAGRAM_ACCESS_TOKEN`

---

## 6. GitHub Actions (todos os crons)

### `publish.yml` — posts editoriais
```yaml
schedule:
  - cron: '0 12 * * 1'   # Seg 9h BR (12 UTC)
  - cron: '0 16 * * 3'   # Qua 13h BR (16 UTC)
  - cron: '0 21 * * 5'   # Sex 18h BR (21 UTC)
```
- Roda `publish_next_approved.py`
- Prioridade: `content/news_queue/` > `content/approved/`

### `stories.yml` — stories diários
```yaml
schedule:
  - cron: '0 12 * * *'   # Todo dia 9h BR
  - cron: '0 21 * * *'   # Todo dia 18h BR
```
- Roda `scripts/stories/publish_story.py`
- 2 stories/dia × 30 dias = 60 stories (fila atual cobre todo o mês)

### `monitor.yml` — news scrape
```yaml
schedule:
  - cron: '15 * * * *'   # Toda hora :15
```
- Roda `scripts/news/monitor.py`
- **Hard-cap: máx 1 notícia/semana** (anti-spam crítico)
- Espacamento mínimo: 48h entre notícias
- Faz checkout do `Site_FNDE` via `GH_REPO_PAT` e atualiza `src/data/news.ts`
- Push no Site_FNDE dispara Vercel auto-deploy

---

## 7. Sistema de POSTS (carrosseis)

### batch_002.json — em produção
12 posts focados em CONVERSÃO (não em informar). Pattern fixo:

```
Slide 1: Hook tipo PERGUNTA-DOR
Slide 2: Dado MEC pra credibilidade
Slide 3-5: Tutorial OU kit (valor concreto)
Slide 6: "Programa Supra AM" (sempre presente)
Slide 7: CTA pra /orcamento
```

**Cadência semanal:**
- Seg → Tutorial (passo-a-passo PDDE/SRM)
- Qua → Evergreen (regra/calendário/checklist)
- Sex → Kit (vitrine de produto)

**Lista dos 12 posts ativos:**
| # | Slug | Tema |
|---|------|------|
| 01 | prestar-contas-pdde-sem-rejeicao | Tutorial prestação |
| 02 | vedacoes-pdde-7-itens | O que NÃO pode comprar |
| 03 | kit-pdde-equidade-completo | Vitrine kit |
| 04 | custeio-vs-capital-portaria-448 | Regra 70/30 |
| 05 | calendario-pdde-2026 | Datas-chave |
| 06 | kit-srm-completo | Vitrine SRM |
| 07 | pdde-interativo-passo-a-passo | Tutorial sistema |
| 08 | sinais-fornecedor-furada | Critério escolha |
| 09 | kit-educacao-conectada | Vitrine conectividade |
| 10 | saldo-reprogramado-pdde | Como usar saldo |
| 11 | contrata-mais-brasil-pdde | Programa novo |
| 12 | kit-cantinho-leitura | Vitrine biblioteca |

### Tipos de slide disponíveis
Definidos em `scripts/generate_slides.py` (dict `RENDERERS`):
- `hook` — capa com pergunta-dor
- `content` — texto + bullet
- `data` — número-bomba destacado
- `list` — checklist 5-7 itens
- `comparison` — "ERRADO vs CERTO"
- `program` — slide "Programa Supra AM" (sempre presente)
- `news` — capa de notícia
- `cta` — fechamento com link

### Fluxo
1. Spec JSON em `content/_specs/batch_XXX.json`
2. `generate_slides.py` renderiza PNGs em `content/images/<slug>/`
3. `build_review.py` cria HTML de preview
4. Aprovação manual move pro `content/approved/`
5. Cron `publish.yml` chama `publish_next_approved.py`
6. Move pro `content/published/` após sucesso

---

## 8. Sistema de STORIES

### Fila atual: 60 stories (`content/_specs/stories.json`)

**Distribuição balanceada:**
| Tipo | Qtd | Função |
|------|-----|--------|
| `dica` | 19 | Autoridade técnica |
| `dado` | 18 | Credibilidade |
| `pergunta` | 14 | Engagement (algoritmo) |
| `quote` | 9 | Memorabilidade |

### Schema de cada story
```json
{
  "id": "s001",
  "type": "dica|dado|pergunta|quote",
  "title": "string curto",
  "body": "string até 80 chars",
  "tag": "PDDE|SRM|FNDE|Supra"
}
```

### Render
- Template: `scripts/templates/story_template.html`
- Tamanho: **1080×1920** (vertical)
- Cores: mesma paleta (navy/gold/cream)

### Publicação
- `publish_story.py` faz: render → **commit/push imagem ANTES** → cria container → publica
- Bug histórico crítico: se não commitar antes, IG retorna "Media URI fetch failed".
- Branch reference: usa `master`, não `GITHUB_SHA` (CDN do raw refresca mais rápido).

### Quando esvaziar (após s060)
Workflow loga "sem stories pendentes" e fica parado. Avise: **"bora 60 stories novos"**.

---

## 9. Sistema de NEWS MONITOR

### Como funciona
1. Cron horário `:15` chama `scripts/news/monitor.py`
2. Faz 13 queries no Google News RSS (FNDE, PDDE, Fundeb, MEC, etc.)
3. Filtra por domínios confiáveis (`gov.br`, `agenciagov.ebc.com.br`, G1, UOL, etc.)
4. Ranqueia por keywords de impacto (R$ X bi/mi, "MEC autoriza", "publicada portaria", etc.)
5. Dedup semântico por **valor R$ + assinatura de tema**
6. Compara com `state/seen_articles.json`
7. Aplica hard-cap: **1 notícia/semana, mínimo 48h entre**
8. Se passa: chama `generate_post.py` → cria IG + blog entry
9. Commita Site_FNDE via PAT → Vercel deploy automático

### Por que hard-cap?
**Dia do spam (lembrar)**: postou 7 notícias em 1 dia. Conta virou agregador. Fix: hard-cap.

```python
if published_last_7d >= 1:
    print("[hard-cap] Ja foi publicada 1 noticia nos ultimos 7 dias. Pulando.")
    return []
```

### Detecção de tema (`generate_post.py`)
`detect_theme()` retorna contexto para:
- Fundeb (R$ 4,8 bi caso)
- PDDE Básico
- PDDE Equidade
- PDDE Conectividade
- Contrata+Brasil
- SRM
- Outros (genérico)

Cada tema tem captions, hashtags e bloco CTA customizados.

### Cap de notícias = 4/mês
1 por semana × 4 semanas. Se domínio confiável publicar mais, espera.

---

## 10. Cross-repo Site_FNDE + Vercel

### Arquitetura
```
Insta_Supra (este repo)         Site_FNDE (repo separado)        Vercel
   monitor.yml                      src/data/news.ts                site live
        │                                  ▲                          ▲
        ├── checkout via PAT ──────────────┤                          │
        ├── escreve nova entrada           │                          │
        ├── commit + push ─────────────────┤                          │
        └────────────────────────────────  ▼ ─── auto-deploy ────────┤
```

### Setup
- PAT fine-grained com permissão `contents: write` no Site_FNDE
- Secret: `GH_REPO_PAT`
- Checkout path: `_external/Site_FNDE` (DENTRO do workspace — fora dá erro do `actions/checkout`)
- Env var: `SITE_FNDE_PATH=_external/Site_FNDE`

### Schema BlogPost extension
```ts
type BlogBlock =
  | { kind: "paragraph"; text: string }
  | { kind: "heading"; text: string }
  | { kind: "list"; items: string[] }
  | { kind: "quote"; text: string; cite?: string }
  | { kind: "cta"; title: string; text: string; buttonLabel: string; buttonHref: string };
```

Renderer do `cta` no `Site_FNDE/src/app/blog/[slug]/page.tsx`:
- Bg gradiente navy + borda gold
- Botão gold sólido com link `/orcamento`

### Páginas modificadas no Site_FNDE
- `src/data/blog.ts` — adiciona kind "cta" no union type
- `src/data/news.ts` — gerado automaticamente
- `src/app/blog/page.tsx` — importa newsPosts + merge com editorialPosts
- `src/app/blog/[slug]/page.tsx` — idem + renderer cta

---

## 11. Regras de linguagem (acessibilidade)

> Pedido EXPLÍCITO do usuário em 2026-06-05:
> *"oq e glosada esse nao e um termo comum"*

### Substituições obrigatórias
| Banido | Usar |
|--------|------|
| glosa | rejeição |
| glosada | rejeitada |
| glosar | rejeitar |
| dotação orçamentária | verba |
| empenho | autorização de gasto |
| pregão eletrônico | compra pública online |
| ata de registro de preços | lista de preços já aprovada |
| termo de adjudicação | confirmação de quem ganhou |

### Princípio
Diretor de escola pública lendo no celular **entre uma reunião e outra**. Se precisar abrir dicionário, perdemos a conversa. Termo técnico aparece SÓ se for explicado na hora.

### Checklist antes de publicar
- [ ] Tem "glosa" no texto? Trocar.
- [ ] Tem sigla sem explicar? Adicionar parêntese.
- [ ] Frase tem mais de 18 palavras? Quebrar.
- [ ] Tem voz passiva ("foi realizada")? Trocar pra ativa ("a escola fez").

---

## 12. Fixes históricos (não repetir)

| Bug | Causa raiz | Fix |
|-----|------------|-----|
| `"API access blocked" 200` | Token invalidado | **Add account** flow (não "Generate Token") |
| Catbox.moe `"Invalid uploader"` | Bloqueou IPs GH Actions | Switch pra raw GitHub URLs (repo público) |
| 0x0.st `disabled uploads` | Serviço caiu | Raw GitHub URL é fonte primária |
| Workflow não dispara | Indexing delay primeiro push | Pequeno commit subsequente força reindex |
| Checkout `"not under workspace"` | Path fora do workspace | `_external/Site_FNDE` (dentro) |
| Hashtag duplicada na caption | Append sem checar | Verificar se caption já termina com `#` |
| 7 notícias em 1 dia (spam) | Sem rate-limit | Hard-cap 1/semana + 48h mínimo |
| Blog não renderiza news.ts | Page só importava blog.ts | Merge newsPosts + editorialPosts |
| Duplicatas FNDE vs MEC | URLs diferentes, mesma matéria | Dedup por valor R$ + tema |
| Story "Media URI fetch failed" | Imagem não commitada antes do publish | `commit_and_push_story()` ANTES + sleep 8s + branch `master` |
| Slug com acento (`rejeição`) | Filesystem windows | Normalizar pra ASCII no slugify |

---

## 13. Estratégia 20k seguidores

### Meta de 12 meses
- 20.000 seguidores qualificados (gestores escolares + secretarias Norte)
- 100 orçamentos solicitados/mês via DM/site
- 8-15 clientes novos/mês com ticket médio R$ 30k-100k

### Pilar 1 — Conteúdo (já rodando)
- 12 posts/mês conversão-first (batch_002)
- 60 stories/mês mix técnico+humano
- 4 notícias/mês com bloco CTA

### Pilar 2 — Engagement loops
- Cada post tem Slide 7 com CTA `/orcamento`
- Cada Story tem call-to-action pra DM ou site
- Quotes e Perguntas geram comentários (sinal algoritmo)

### Pilar 3 — Distribuição
- **Orgânico (hoje)**: hashtags + horários de pico
- **Pago (em 30d)**: Meta Ads Cenário A (R$ 200/mês) → ver ADS_PROPOSTA.md
- **Newsletter (pendente)**: capturar emails do site, dispatch mensal

### Pilar 4 — Conversão
- Bio com link único `/orcamento`
- Resposta DM em < 2h (horário comercial)
- WhatsApp Business com auto-resposta

### KPI semanais
| Métrica | Meta |
|---------|------|
| Novos seguidores | 100-200/sem |
| Engajamento médio | > 3% |
| DMs recebidas | 5-10/sem |
| Cliques no link bio | 30-60/sem |
| Orçamentos solicitados | 1-2/sem |

---

## 14. Pendências e roadmap

### Curto prazo (próximos 30 dias)
- [ ] **Newsletter broadcast**: persistir leads do site + dispatch Resend
- [ ] **Bio nova**: "Solicitar orçamento" como CTA primário
- [ ] **Verificar primeiros 30 dias** do batch_002 rodando

### Médio prazo (30-90 dias)
- [ ] **Meta Ads ativação** (05/07/2026): Cenário A R$ 200/mês — ver ADS_PROPOSTA.md
- [ ] **Pixel Meta no Site_FNDE**: rastrear conversões `/orcamento`
- [ ] **Reels pipeline**: HTML→MP4 via Playwright + audio overlay — ver REELS_PLAN.md
- [ ] **batch_003**: 12 posts novos quando batch_002 acabar

### Longo prazo (90d+)
- [ ] **DM bot leve**: auto-resposta com link orçamento
- [ ] **Comentários em contas educação**: lista curada, comentário relevante (NÃO spam)
- [ ] **WhatsApp Business integration**: leads do site direto pro número
- [ ] **Reputação**: solicitar reviews no Google Maps Manaus

---

## 15. Comandos úteis (cheat sheet)

### Local — gerar e revisar
```bash
# Gera slides do batch 002
python -m scripts.generate_slides --spec content/_specs/batch_002.json

# Cria HTML de review
python -m scripts.build_review

# Aprova post (move pro approved/)
python -m scripts.approve_batch <slug>

# Preview do feed
python -m scripts.build_feed_preview
```

### Local — testar publish
```bash
# Publica próximo aprovado (worker)
python -m scripts.publish_next_approved

# Refresh manual do token
python -m scripts.refresh_token

# Story isolado (test)
python -m scripts.stories.publish_story
```

### Local — news
```bash
# Roda monitor 1 vez (sem cron)
python -m scripts.news.monitor

# Gera post da news mais recente
python -m scripts.news.generate_post
```

### GitHub Secrets (gh CLI)
```bash
gh secret set INSTAGRAM_ACCESS_TOKEN --body "IGAA..."
gh secret set GH_REPO_PAT --body "github_pat_..."
gh secret list
```

### GitHub Actions
```bash
# Listar workflows
gh workflow list

# Disparar manualmente
gh workflow run stories.yml
gh workflow run publish.yml
gh workflow run monitor.yml

# Ver últimas execuções
gh run list --workflow=stories.yml --limit 5
gh run view <run_id> --log
```

### Cross-repo
```bash
# Forçar deploy Site_FNDE
cd ../Site_FNDE && git commit --allow-empty -m "trigger redeploy" && git push
```

---

## 15.1 SEO — Search Console + IndexNow (NOVO)

### Google Search Console
- **Propriedade**: `https://supraam.com.br/` verificada via arquivo HTML em `public/google752af23eb18a26a4.html`
- **Sitemap**: `sitemap.xml` processado, 112 URLs detectadas
- **Indexação manual**: 10 URLs prioritárias solicitadas (limite 10-12/dia)

### Bing Webmaster
- **Propriedade**: `supraam.com.br` verificada via login Google
- **Sitemap**: importado automaticamente do robots.txt, 112 URLs

### IndexNow (Bing/Yandex/Seznam/Naver)
- **Chave**: `284142c04864c67111610badd2ccd911ff94b411a3c3dd9759d2bc99d0ae7bd8` (hardcoded em `scripts/news/indexnow.py`)
- **Arquivo validação**: `Site_FNDE/public/<KEY>.txt` (público)
- **Endpoint**: `https://api.indexnow.org/indexnow`

### Fluxo automático (ativado em 2026-06-05)
```
News monitor encontra notícia
  └─> generate_post.py cria slug
       └─> add_pending(url) escreve em state/pending_indexnow.json
            └─> monitor.yml push Site_FNDE pro Vercel
                 └─> Vercel deploy (~60s)
                      └─> sleep 90s + python -m scripts.news.indexnow
                           └─> IndexNow notifica Bing/Yandex/Seznam
                                └─> URLs indexadas em < 1 hora
```

### CLI manual (boost)
```bash
# Notifica URLs específicas
python -m scripts.news.indexnow https://supraam.com.br/blog/algum-slug

# Flush do pending file
python -m scripts.news.indexnow
```

### Comprovação (2026-06-05)
- ✅ Teste 1: 3 URLs → Status 202 ACEITO
- ✅ Teste 2: 20 URLs (todas as prioritárias) → Status 200 ACEITO

---

## 16. Decisões estratégicas (registro)

| Data | Decisão | Por quê |
|------|---------|---------|
| 2026-06-XX | Stack: Python + GH Actions + Vercel | Zero infra, free tier suficiente |
| 2026-06-XX | Raw GitHub URLs como host | Catbox bloqueou, 0x0.st caiu |
| 2026-06-XX | Repo público | Necessário pra raw funcionar; conteúdo é marketing |
| 2026-06-XX | Cron 3x/sem posts | Equilíbrio densidade × spam |
| 2026-06-XX | Hard-cap 1 notícia/sem | Spam day mostrou que precisa |
| 2026-06-XX | batch_002 substitui 001 | 001 era informativo; 002 converte |
| 2026-06-05 | Remover "glosa" do vocabulário | Acessibilidade pro decisor |
| 2026-06-05 | Stories 2x/dia (9h + 18h BR) | Pico de engajamento; 60 stories/mês |
| 2026-06-05 | Ads adiado pra 05/07/2026 | Esperar batch_002 + bio nova |
| 2026-06-05 | GSC + Bing + IndexNow ativados | Site não aparecia no Google; agora 112 URLs registradas + indexação <1h via IndexNow |

---

## 17. Arquivos correlatos (leitura específica)

- **BRAND_PATTERN.md** — detalhes de cada tipo de slide, captions modelo, hashtag stacks
- **ADS_PROPOSTA.md** — 3 cenários Meta Ads, ROI esperado, calendário semanal
- **REELS_PLAN.md** — arquitetura futura HTML→MP4 + audio
- **SETUP_GITHUB.md** — passo-a-passo PAT, gh CLI install, secrets

---

## 18. Princípios mestres (filosofia)

1. **Setup 1 vez, rodar mensal automático** — usuário não revisa semanalmente.
2. **Conversão > vaidade** — métrica que importa é orçamento solicitado.
3. **Acessibilidade > sofisticação** — diretor entende > diretor admira.
4. **Anti-spam é vida** — hard-caps são feature, não bug.
5. **Cross-repo é caminho** — Insta + Blog + Vercel orquestrados.
6. **Tudo versionado** — state em JSON commitado, audit trail total.
7. **Failure-safe** — se token expira, refresh tenta antes; se imagem falha, fallback chain; se PAT falta, graceful degradation.

---

**Última atualização**: 2026-06-05
**Mantenedor**: Claude (Anthropic) via sessão Claude Code
**Próxima revisão sugerida**: quando batch_002 esgotar OU quando Meta Ads for ativado.
