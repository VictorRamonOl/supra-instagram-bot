"""
weekly_digest.py — Gera digest semanal de posts pro Google Business Profile.

Toda segunda 9h BR, o cron roda este script. Ele:
  1. Lê o conteúdo publicado/agendado da semana (batch_002 + stories + news)
  2. Escolhe 2 ângulos diferentes pra postar no GBP
  3. Adapta a copy pro formato GBP (curto, CTA forte, link)
  4. Escreve em content/gbp_digest/YYYY-WW.md
  5. Commit no GitHub (você recebe notificação)

Resultado: você abre o arquivo de domingo, copia/cola 2 posts no GBP, leva 4 minutos.

Sem GBP API (foi restringida em 2022), automação 100% headless requer Selenium
ou serviço pago. Esse digest é o middle-ground: 95% automatizado, 5% manual.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DIGEST_DIR = PROJECT_ROOT / "content" / "gbp_digest"
BATCH_FILE = PROJECT_ROOT / "content" / "_specs" / "batch_002.json"
STORIES_FILE = PROJECT_ROOT / "content" / "_specs" / "stories.json"
PUBLISHED_FILE = PROJECT_ROOT / "state" / "published.json"
PUBLISHED_STORIES_FILE = PROJECT_ROOT / "state" / "published_stories.json"

SITE_URL = "https://supraam.com.br"
WHATSAPP_URL = "https://wa.me/5592981411712"


# Templates de copy adaptados pro GBP (mais curto, CTA direto)
# Cada template usa o tema do post original e adapta pro GBP.
GBP_TEMPLATES = {
    "tutorial": {
        "title_pattern": "Tutorial: {topic}",
        "text_pattern": (
            "Equipe Supra AM publicou hoje um tutorial completo: {topic}. "
            "Conteúdo gratuito pra UEx, diretores e secretarias. Confira no "
            "nosso blog — e se precisar de apoio técnico pra aplicar, "
            "fala com a gente."
        ),
        "cta_label": "Ler tutorial",
        "cta_url": f"{SITE_URL}/blog",
    },
    "kit": {
        "title_pattern": "Kit pronto: {topic}",
        "text_pattern": (
            "{topic} — kit completo com itens elegíveis, descrição técnica "
            "alinhada ao FNDE e logística pra todo o Norte. Orçamento "
            "técnico em até 3 dias úteis."
        ),
        "cta_label": "Pedir orçamento",
        "cta_url": f"{SITE_URL}/orcamento",
    },
    "evergreen": {
        "title_pattern": "{topic}",
        "text_pattern": (
            "{topic} — material de referência pra gestores escolares do "
            "Norte. Conteúdo técnico baseado na legislação FNDE vigente. "
            "Acesse e compartilhe com sua equipe."
        ),
        "cta_label": "Ver no blog",
        "cta_url": f"{SITE_URL}/blog",
    },
    "news": {
        "title_pattern": "Novidade FNDE: {topic}",
        "text_pattern": (
            "Acompanhamos a publicação: {topic}. Veja análise completa no "
            "nosso blog — com impacto pra escolas e orientação técnica de "
            "como agir. Apoio gratuito pra UEx do Norte."
        ),
        "cta_label": "Ler análise",
        "cta_url": f"{SITE_URL}/blog",
    },
    "checklist": {
        "title_pattern": "Checklist: {topic}",
        "text_pattern": (
            "{topic} — checklist prático elaborado pela equipe técnica. "
            "Use pra revisar antes de publicar/empenhar/prestar contas. "
            "Material gratuito."
        ),
        "cta_label": "Ver checklist",
        "cta_url": f"{SITE_URL}/blog",
    },
    "default": {
        "title_pattern": "{topic}",
        "text_pattern": (
            "{topic}. Conteúdo elaborado pela equipe Supra AM pra escolas "
            "e secretarias do Norte. Veja mais no blog e fale com a gente "
            "se precisar de apoio."
        ),
        "cta_label": "Saiba mais",
        "cta_url": SITE_URL,
    },
}


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_published_slugs() -> set[str]:
    """Slugs ja publicados (pra nao repetir no digest)."""
    data = load_json(PUBLISHED_FILE, {})
    if isinstance(data, dict) and "posts" in data:
        return {p.get("slug") for p in data["posts"] if p.get("slug")}
    if isinstance(data, list):
        return {p.get("slug") for p in data if isinstance(p, dict) and p.get("slug")}
    return set()


def detect_category(post: dict) -> str:
    """Detecta tipo do post pra escolher template. Usa pillar primeiro, fallback heuristico."""
    # Mapeamento direto do pillar (batch_002.json usa esse campo)
    pillar = (post.get("pillar") or "").lower().strip()
    if pillar:
        return {
            "tutorial": "tutorial",
            "kit": "kit",
            "vitrine": "kit",
            "evergreen": "evergreen",
            "checklist": "checklist",
            "news": "news",
            "noticia": "news",
        }.get(pillar, "default")

    # Fallback heuristico
    slug = (post.get("slug") or "").lower()
    title = _post_title(post).lower()
    blob = f"{title} {slug}"

    if any(k in blob for k in ["kit-", "kit ", "completo"]):
        return "kit"
    if any(k in blob for k in ["tutorial", "passo-a-passo", "como-"]):
        return "tutorial"
    if any(k in blob for k in ["checklist", "lista de", "vedacoes", "sinais"]):
        return "checklist"
    if any(k in blob for k in ["news", "noticia", "novidade", "publicou", "mec-", "fnde-"]):
        return "news"
    if any(k in blob for k in ["calendario", "regra", "portaria", "saldo", "vs"]):
        return "evergreen"
    return "default"


def _post_title(post: dict) -> str:
    """Extrai um titulo legivel do post (do slide hook, caption ou slug)."""
    # 1. Tenta slide hook (slides[0].headline + subheadline)
    slides = post.get("slides") or []
    if slides:
        s0 = slides[0]
        head = (s0.get("headline") or "").strip()
        sub = (s0.get("subheadline") or "").strip()
        if head and sub:
            return f"{head} {sub}"
        if head:
            return head
    # 2. Tenta title direto
    if post.get("title"):
        return str(post["title"]).strip()
    # 3. Tenta primeira frase do caption
    cap = (post.get("caption") or "").strip()
    if cap:
        first = cap.split("\n")[0].strip()
        if first:
            return first[:120]
    # 4. Fallback: slug humanizado
    return (post.get("slug", "")
            .replace("-", " ")
            .replace("_", " ")
            .strip()
            .capitalize() or "Post Supra AM")


def pick_topic_phrase(post: dict) -> str:
    """Extrai frase-tópico curta (max 80 chars)."""
    title = _post_title(post)
    title = title.rstrip(".:!?,;")
    return title[:80]


def render_gbp_post(post: dict) -> dict:
    """Aplica template de GBP a 1 post."""
    cat = detect_category(post)
    tpl = GBP_TEMPLATES[cat]
    topic = pick_topic_phrase(post)
    return {
        "category": cat,
        "source_slug": post.get("slug", "?"),
        "source_title": _post_title(post),
        "gbp_title": tpl["title_pattern"].format(topic=topic),
        "gbp_text": tpl["text_pattern"].format(topic=topic),
        "cta_label": tpl["cta_label"],
        "cta_url": tpl["cta_url"],
    }


def pick_two_posts(batch: list[dict], stories: list[dict], published: set[str]) -> list[dict]:
    """
    Escolhe 2 posts complementares pra digest da semana.
    Prioriza diversidade (1 kit + 1 tutorial, ou 1 evergreen + 1 news, etc).
    """
    candidates = []

    # Pega posts ja publicados (mais relevante pro algoritmo do GBP)
    for p in batch:
        if p.get("slug") in published:
            candidates.append({**p, "_source": "batch_published"})

    # Adiciona kits e evergreens nao publicados ainda (sao bons pra GBP)
    for p in batch:
        if p.get("slug") not in published:
            cat = detect_category(p)
            if cat in ("kit", "evergreen", "checklist"):
                candidates.append({**p, "_source": "batch_pending"})

    if not candidates:
        # Fallback: pega os 2 primeiros do batch
        candidates = [{**p, "_source": "batch_fallback"} for p in batch[:2]]

    # Tenta pegar 2 categorias diferentes
    selected = []
    seen_cats = set()
    for c in candidates:
        cat = detect_category(c)
        if cat not in seen_cats:
            selected.append(c)
            seen_cats.add(cat)
        if len(selected) == 2:
            break

    # Se nao deu 2 com categorias diferentes, completa com qualquer
    if len(selected) < 2:
        for c in candidates:
            if c not in selected:
                selected.append(c)
            if len(selected) == 2:
                break

    return selected[:2]


def build_digest_md(week_id: str, posts: list[dict], today: str) -> str:
    """Renderiza o markdown final do digest."""
    rendered = [render_gbp_post(p) for p in posts]

    md = f"""# GBP Digest — Semana {week_id}

> Gerado automaticamente em **{today}**. 2 minutos pra fazer:
> 1. Copia o **Título** + **Texto** + **CTA** de cada post abaixo
> 2. Cola no painel GBP → **Postagens → Adicionar atualização**
> 3. Faz upload da imagem sugerida (ou usa o equivalente do Instagram)
> 4. Publica
>
> **Cadência ideal**: posta o Post 1 na **segunda ou terça**, o Post 2 na **quinta ou sexta**.

---

## Post 1 — {rendered[0]['category']} · `{rendered[0]['source_slug']}`

### Título
```
{rendered[0]['gbp_title']}
```

### Texto
```
{rendered[0]['gbp_text']}
```

### Botão
- **Label**: {rendered[0]['cta_label']}
- **URL**: {rendered[0]['cta_url']}

### Imagem sugerida
- Pega a capa do post `{rendered[0]['source_slug']}` em `content/images/{rendered[0]['source_slug']}/` (slide 1 ou o `program.png`)
- Ou reaproveita a mesma capa do Instagram

---

"""
    if len(rendered) > 1:
        md += f"""## Post 2 — {rendered[1]['category']} · `{rendered[1]['source_slug']}`

### Título
```
{rendered[1]['gbp_title']}
```

### Texto
```
{rendered[1]['gbp_text']}
```

### Botão
- **Label**: {rendered[1]['cta_label']}
- **URL**: {rendered[1]['cta_url']}

### Imagem sugerida
- Pega a capa do post `{rendered[1]['source_slug']}` em `content/images/{rendered[1]['source_slug']}/`
- Ou reaproveita a mesma capa do Instagram

---

"""

    md += f"""## Por que esses 2 posts foram escolhidos

| Post | Categoria | Razão |
|------|-----------|-------|
| 1 | {rendered[0]['category']} | {_explain_category(rendered[0]['category'])} |
"""
    if len(rendered) > 1:
        md += f"| 2 | {rendered[1]['category']} | {_explain_category(rendered[1]['category'])} |\n"

    md += f"""
---

## Próximos passos

- [ ] Postar Post 1 (segunda/terça)
- [ ] Postar Post 2 (quinta/sexta)
- [ ] Adicionar 1 review pedido se possível
- [ ] Responder mensagens recebidas em < 2h

## Quando você terminou, marca aqui

> Quando você postar os 2, **deleta esse arquivo** (`rm content/gbp_digest/{week_id}.md`)
> ou marca uma seção "✅ POSTADOS" no topo. Assim eu sei que avançou.

---

**Próximo digest**: segunda que vem às 9h BR (automático).
"""
    return md


def _explain_category(cat: str) -> str:
    return {
        "tutorial": "Posts educativos rankeiam bem em buscas '_como_, _o que é_, _passo a passo_'",
        "kit": "Posts de produto convertem direto — botão 'Pedir orçamento' = lead",
        "evergreen": "Conteúdo perene gera tráfego constante por meses",
        "news": "Atualizações sinalizam ao algoritmo que o negócio está ativo",
        "checklist": "Posts utilitários ganham salvos/compartilhamentos",
        "default": "Diversificação de tipos pra manter o feed dinâmico",
    }.get(cat, "Variedade no feed melhora ranqueamento")


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # ISO week — formato YYYY-WW
    iso = datetime.now(timezone.utc).isocalendar()
    week_id = f"{iso.year}-W{iso.week:02d}"

    batch = load_json(BATCH_FILE, {})
    batch_posts = batch.get("posts", []) if isinstance(batch, dict) else []
    stories = load_json(STORIES_FILE, {})
    stories_list = stories.get("stories", []) if isinstance(stories, dict) else []
    published = load_published_slugs()

    if not batch_posts:
        print("[gbp-digest] batch_002.json vazio — abortando")
        return 1

    selected = pick_two_posts(batch_posts, stories_list, published)
    if not selected:
        print("[gbp-digest] nenhum post selecionado")
        return 1

    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    md = build_digest_md(week_id, selected, today)
    out = DIGEST_DIR / f"{week_id}.md"
    out.write_text(md, encoding="utf-8")
    print(f"[gbp-digest] Gerado: {out}")
    print(f"[gbp-digest] Posts: {[p.get('slug') for p in selected]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
