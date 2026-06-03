# Padrão Editorial e Visual — @grupo.supraam
> Documento de referência para futuras produções (batch 002, 003, ...)
> Usado pelo Claude pra manter consistência sem você ter que reexplicar.

---

## 1. Identidade Visual

### Paleta de cores (atualizado 2026-06-02 para casar com supraam.com.br)
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
- Círculos decorativos transparentes (5% opacidade) — um no canto inferior direito (700x700), um no superior esquerdo (500x500)
- Marca **SA** no canto inferior direito: quadrado 56x56 com borda dourada, "SUPRA AM / SOLUÇÕES INTEGRADAS" ao lado
- Paginador `01 / 07` no canto inferior esquerdo, cor creme, opacidade 50%

---

## 2. Estrutura Editorial

### Pilares (3x/semana)
| Dia | Pilar | Função |
|-----|-------|--------|
| **Segunda** | Técnico-regulatório | Autoridade. PDDE/FNDE, Resolução, Portaria 448, vedações, prestação de contas |
| **Quarta** | Catálogo/produto | Conversão suave. "Como escolher", checklists, comparativos. SEM expor inventário |
| **Sexta** | Mercado/regional | Posicionamento. Censo escolar AM, logística, inclusão no Norte |

### Frequência
**3x/semana** (não diário, não a cada 3 dias). Dias fixos > intervalo fixo.

### Horários (em Brasília)
- Seg 9h, Qua 13h, Sex 18h
- Em UTC: Seg 12h, Qua 16h, Sex 21h

---

## 3. Tipos de Slide

### `hook` (Capa)
Primeiro slide do carrossel. Layout vertical de impacto.
- Label "SUPRA AM" com linha dourada
- Headline grande Playfair (110px)
- Subhead em creme (32px, 35% width)
- Footer pequeno: "Carrossel — Supra AM"

### `content` (Conteúdo)
Slide intermediário com kicker + título + corpo.
- Kicker numerado em quadro com borda dourada: "1 / Subtema"
- Headline Playfair 68px
- Corpo Inter 30px, line-height 1.55, máx 880px de largura
- Suporta `\n` pra quebra de linha

### `data` ou `list` (Lista numerada)
Para destacar 3-5 itens importantes.
- Kicker + headline (56px)
- Lista com numeração em Playfair dourado (01, 02, 03)
- Divisor dourado fino entre itens

### `comparison` (Comparativo 3 colunas)
Para comparar opções (ex: Lousa vs Projetor vs TV).
- 3 colunas com fundo translúcido e borda dourada
- Nome de cada coluna em Playfair dourado
- Linhas de comparação em creme

### `program` (Programa Supra AM) ⭐ NOVO
Slide de oferta institucional — penúltimo do carrossel (antes do CTA).
- Kicker "PROGRAMA SUPRA AM" com linha dourada nas pontas
- Headline 60px Playfair (nome do kit/programa)
- Descrição curta (26px, creme, 300 weight)
- 4 bullets com checkmark dourado
- Link `supraam.com.br` em badge com borda dourada

### `cta` (Chamada pra ação)
Último slide do carrossel.
- Centralizado verticalmente
- Headline pergunta direta
- Body com instrução **+ sempre menção a `supraam.com.br`** ("Visite supraam.com.br pra ver todos os kits.")
- Botão dourado com `@grupo.supraam`

---

## 4. Estrutura de Conteúdo

### Carrossel padrão (6-8 slides)
```
1. Hook (capa)
2-5. Content / Data / List (corpo educativo)
6. Program (kit/programa específico)
7. CTA (DM ou comentário)
```

### Card único
1 slide só, tipo `list` (5 itens em geral). Direto, sem build-up.

---

## 5. Caption (Legenda)

### Estrutura
```
[Linha 1 — hook curto, máx 80 caracteres]

[Parágrafo 1 — contexto do problema/tema]

[Parágrafo 2 — o que o post entrega]

[Linha de CTA — "Salve" / "Comenta" / "Chama no direct"]

Conheça todos os nossos kits em supraam.com.br

[Hashtags — 5 a 8, sempre quebra de linha antes]
```

> **Site CTA é padrão fixo em toda caption** — drives traffic pro supraam.com.br. Nunca remover.

### Tom de voz
- Formal-acessível (como o site)
- Decisor B2G — sem gírias, sem emoji em excesso (máx 0-1 por caption)
- Linguagem técnica explicada (Resolução X = "a regra que diz que...")
- CTAs orientados a **DM** (direct message) ou **salvar post**

---

## 6. Hashtags

### Base (sempre presentes em todo post)
`#PDDE #FNDE #GestaoEscolar #EducacaoAmazonas`

### Por pilar (adicionar 2-4 do pilar do post)
**Técnico**: `#ComprasPublicas #Portaria448 #ResolucaoFNDE #UnidadeExecutora`
**Catálogo**: `#MobiliarioEscolar #TecnologiaNaEducacao #SRM #InclusaoEscolar #BrinquedoPedagogico #EducacaoInfantil`
**Regional**: `#EducacaoNoNorte #CensoEscolar #EscolaRibeirinha #AmazonasEducacao #LogisticaEducacional`

---

## 7. Restrições editoriais (importante)

❌ **NÃO postar:**
- Fotos de equipe, escritório, processos internos
- Números internos (qtd de clientes, faturamento, equipe)
- "Vendemos pra escola X" / nomes de clientes
- Memes, GIFs, gírias
- Conteúdo de "promoção / desconto"

✅ **PODE postar:**
- Conteúdo técnico autoral
- Comparativos
- Dados públicos (Censo INEP, IBGE, FNDE)
- Referências a kits/programas do supraam.com.br via slide `program`
- Opiniões técnicas com responsabilidade

---

## 8. Sequência de produção (passo a passo Claude)

Pra produzir um novo batch (ex: batch 002):

1. **Identificar gaps** no calendário (próximos 30 dias)
2. **Mapear pilares** por dia (Seg/Qua/Sex)
3. **Escrever specs** no formato `content/_specs/batch_NNN.json`
4. **Adicionar slide `program`** em todos os carrosseis (mapear kit relevante)
5. **Rodar generate_slides.py** pra produzir os PNGs
6. **Rodar build_review.py** pra gerar página de revisão
7. **Rodar build_feed_preview.py** pra mostrar como ficará o grid
8. **Usuário revisa e aprova** via `approve_batch.py`
9. **GitHub Actions** publica conforme cron

---

## 9. Comandos de referência

```powershell
# Gerar slides de um batch
python scripts/generate_slides.py --batch content/_specs/batch_001.json

# Gerar so alguns (--only)
python scripts/generate_slides.py --batch content/_specs/batch_001.json --only 03,06

# Pagina de revisao
python scripts/build_review.py --open

# Feed preview
python scripts/build_feed_preview.py

# Aprovar (move pending -> approved)
python scripts/approve_batch.py --ids 01,02,03
python scripts/approve_batch.py --all
python scripts/approve_batch.py --reject 05

# Publicar manualmente (ou GitHub Actions faz)
python scripts/publish_next_approved.py

# Renovar token (auto, mas pode forçar)
python scripts/refresh_token.py --force
```

---

## 10. Métricas de sucesso (90 dias)

- Crescimento: 16 → 300 seguidores
- Engajamento médio: >4% (alto pra B2B)
- Salvos: >20% das curtidas
- DMs qualificadas: >2/mês de gestores reais

---

> Última atualização: 2026-06-02
> Batch atual: 001 (12 posts cobrindo Junho 2026)
