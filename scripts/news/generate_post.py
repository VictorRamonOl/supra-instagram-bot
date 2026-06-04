"""
generate_post.py - Gera post Instagram (slides + post.json) + entrada no blog Site_FNDE.

Recebe artigo com {title, link, resolved_link, source_name, pub_date, description}
e cria:
  1. content/news_queue/YYYYMMDD_HHMM_slug/  com 5 slides PNG + post.json
  2. Anexa entrada em Site_FNDE/src/data/news.ts (se path existir)

Template (sem IA): hook + manchete + resumo + impacto + CTA blog.
"""
import html as html_mod
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests


def clean_text(s: str) -> str:
    """Decodifica entidades HTML e normaliza espacos."""
    if not s:
        return ""
    s = html_mod.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s)
    # Remove ruido de busca/Google News
    s = re.sub(r"\s*-\s*[^-]+$", "", s)  # remove " - SourceName" no final
    return s.strip()

PROJECT_ROOT = Path(__file__).parent.parent.parent
NEWS_QUEUE = PROJECT_ROOT / "content" / "news_queue"
TEMPLATE_FILE = PROJECT_ROOT / "scripts" / "templates" / "slide_template.html"
# SITE_FNDE_PATH pode ser sobrescrito via env var (usado no GitHub Actions)
_site_override = os.environ.get("SITE_FNDE_PATH")
SITE_FNDE_ROOT = (
    Path(_site_override) if _site_override else PROJECT_ROOT.parent / "Site_FNDE"
)
SITE_NEWS_FILE = SITE_FNDE_ROOT / "src" / "data" / "news.ts"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from generate_slides import build_slide_html, render_slide_to_png  # noqa


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9\s-]", "", s).strip().lower()
    s = re.sub(r"[\s-]+", "-", s)
    return s[:60]


def fetch_article_summary(url: str) -> dict:
    """Busca title + description meta + first paragraph do article. Best-effort."""
    try:
        resp = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 SupraNewsBot/1.0"},
        )
        html = resp.text
    except Exception:
        return {}

    out = {}
    # OG title / description (mais consistente em sites de noticia)
    og_title = re.search(
        r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    og_desc = re.search(
        r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    if og_title:
        out["title"] = og_title.group(1)
    if og_desc:
        out["description"] = og_desc.group(1)
    if "description" not in out:
        m = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if m:
            out["description"] = m.group(1)
    return out


def chunks_from_summary(text: str, max_chars: int = 280) -> list[str]:
    """Divide um resumo longo em 1-2 paragrafos."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return [text]
    # Quebra em frases e agrupa
    sentences = re.split(r"(?<=[\.\!\?])\s+", text)
    out, cur = [], ""
    for s in sentences:
        if len(cur) + len(s) + 1 <= max_chars:
            cur = (cur + " " + s).strip()
        else:
            if cur:
                out.append(cur)
            cur = s
    if cur:
        out.append(cur)
    return out[:2]


def fmt_date_br(rfc822: str) -> str:
    if not rfc822:
        return ""
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            dt = datetime.strptime(rfc822, fmt)
            return dt.strftime("%d %b %Y").lower().replace(".", "")
        except ValueError:
            continue
    return ""


def best_title(article: dict, summary: dict) -> str:
    rss_title = clean_text(article["title"])
    og_title = clean_text(summary.get("title", ""))
    if og_title and "google news" not in og_title.lower() and len(og_title) > 20:
        return og_title
    return rss_title


def best_description(article: dict, summary: dict, title: str) -> str:
    title_norm = title.lower().strip()
    title_prefix = title_norm[:80]
    for c in (
        clean_text(summary.get("description", "")),
        clean_text(article.get("description", "")),
    ):
        if not c or len(c) < 40:
            continue
        if "google news" in c.lower():
            continue
        c_norm = c.lower().strip()
        # Pula se for so o titulo repetido (Google News RSS = titulo + sufixo)
        if title_norm in c_norm or c_norm in title_norm:
            continue
        if c_norm[:60] == title_prefix[:60]:
            continue
        return c
    return ""


def build_slides(article: dict, summary: dict) -> list[dict]:
    title = best_title(article, summary)
    description = best_description(article, summary, title)
    source_name = article.get("source_name") or "Fonte oficial"
    date_str = fmt_date_br(article.get("pub_date", ""))
    paragraphs = chunks_from_summary(description, 260) if description else []

    slides = [
        {
            "type": "news",
            "label": "Novidade FNDE/MEC",
            "headline": title[:140],
            "summary": paragraphs[0] if paragraphs else "Acesse o artigo completo no nosso blog.",
            "source": source_name,
            "date": date_str,
        }
    ]

    # Slide 2: contexto/impacto (se ha 2o paragrafo)
    if len(paragraphs) >= 2:
        slides.append(
            {
                "type": "content",
                "kicker": "Contexto",
                "headline": "O que diz a publicação",
                "body": paragraphs[1],
            }
        )

    # Slide 3: o que muda para gestores (gen�rico mas certeiro)
    slides.append(
        {
            "type": "content",
            "kicker": "Impacto",
            "headline": "O que isso significa pra sua escola",
            "body": (
                "Toda nova publicação no FNDE/MEC pode afetar prazos, regras "
                "de aplicação ou rubricas elegíveis no PDDE.\n\n"
                "Vale revisar seu plano de aplicação à luz da novidade antes "
                "de seguir com compras."
            ),
        }
    )

    # Slide 4: programa Supra
    slides.append(
        {
            "type": "program",
            "headline": "Conte com a Supra AM",
            "desc": "Estamos antenados a cada atualização normativa do FNDE/MEC.",
            "items": [
                "Orçamentos já enquadrados na regra vigente",
                "Suporte na prestação de contas",
                "Análise técnica do impacto pra sua escola",
                "Atendimento direto pra gestores do Norte",
            ],
            "link": "supraam.com.br",
        }
    )

    # Slide 5: CTA blog + newsletter
    slides.append(
        {
            "type": "cta",
            "headline": "Quer receber novidades em primeira mão?",
            "body": (
                "Análise completa no blog: supraam.com.br/blog\n"
                "Cadastre-se na nossa newsletter pra receber novidades do FNDE/MEC direto no e-mail."
            ),
            "footer": "@grupo.supraam · supraam.com.br",
        }
    )

    return slides


def build_caption(article: dict, summary: dict, blog_slug: str) -> str:
    title = best_title(article, summary)
    description = best_description(article, summary, title)[:280]
    source = article.get("source_name") or "Fonte oficial"
    desc_block = f"{description}\n\n" if description else ""

    caption = (
        f"Novidade FNDE/MEC: {title}\n\n"
        f"{desc_block}"
        f"Fonte: {source}\n"
        f"Análise completa no blog: supraam.com.br/blog/{blog_slug}\n"
        f"Cadastre-se na newsletter em supraam.com.br pra receber novidades como essa no e-mail.\n\n"
        f"Conheça nossos kits em supraam.com.br\n\n"
        f"#FNDE #PDDE #GestaoEscolar #EducacaoAmazonas #NovidadeFNDE #EducacaoNoNorte"
    )
    return caption


def render_post_dir(article: dict, summary: dict) -> Path:
    from playwright.sync_api import sync_playwright

    title = best_title(article, summary)
    slug = slugify(title)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    folder_name = f"{timestamp}_{slug}"
    post_dir = NEWS_QUEUE / folder_name
    post_dir.mkdir(parents=True, exist_ok=True)

    slides = build_slides(article, summary)
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    total = len(slides)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for i, slide in enumerate(slides, start=1):
                page_label = f"{i:02d} / {total:02d}"
                html_str = build_slide_html(slide, page_label, template)
                out = post_dir / f"slide_{i:02d}.png"
                print(f"  -> slide {i}/{total}")
                render_slide_to_png(html_str, out, browser)
        finally:
            browser.close()

    caption = build_caption(article, summary, slug)
    post_meta = {
        "id": "NEWS",
        "slug": slug,
        "scheduled_for": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "pillar": "news",
        "format": "carousel" if total > 1 else "single",
        "caption": caption,
        "slides_count": total,
        "source": {
            "url": article.get("resolved_link") or article["link"],
            "name": article.get("source_name", ""),
            "pub_date": article.get("pub_date", ""),
            "query": article.get("query", ""),
        },
        "status": "queued_for_publish",
    }
    (post_dir / "post.json").write_text(
        json.dumps(post_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return post_dir


def detect_theme(title: str, description: str) -> dict:
    """Identifica o tema da noticia pra contextualizar o conteudo."""
    text = (title + " " + description).lower()
    themes = {
        "fundeb": {
            "label": "Fundeb",
            "what_is": (
                "O Fundeb é o fundo nacional que financia a educação básica pública no Brasil. "
                "Os recursos são repassados a estados e municípios com base no número de alunos "
                "matriculados na rede e na complementação da União."
            ),
            "impact": (
                "Para escolas e secretarias, esse repasse significa fôlego orçamentário para "
                "manter e melhorar a estrutura: pagamento de pessoal, manutenção do prédio, "
                "transporte escolar, alimentação e aquisição de materiais didáticos e mobiliário."
            ),
            "action": [
                "Consulte o portal do FNDE para confirmar o valor que sua escola/município recebe",
                "Revise o plano de aplicação à luz do novo repasse",
                "Atualize o inventário de bens permanentes",
                "Planeje aquisições já com descrição técnica padronizada pra prestação de contas",
            ],
        },
        "pdde": {
            "label": "PDDE",
            "what_is": (
                "O Programa Dinheiro Direto na Escola (PDDE) é o recurso federal repassado "
                "diretamente à Unidade Executora (UEx) de cada escola pública. Ele cobre "
                "manutenção, conservação e pequenos investimentos. Existem 3 modalidades: "
                "Básico, Equidade e Qualidade — cada uma com regras próprias na Resolução vigente do FNDE."
            ),
            "impact": (
                "Toda escola que recebe PDDE precisa aplicar respeitando a divisão entre "
                "custeio e capital (Portaria 448/2002) e as vedações da Resolução. Errar a "
                "classificação ou comprar item vedado pode resultar em glosa e devolução do recurso."
            ),
            "action": [
                "Revise o saldo do PDDE no PDDE Web antes de planejar compras",
                "Consulte a Resolução CD/FNDE em vigor para ver o que pode/não pode comprar",
                "Antes de fechar orçamento, confirme se cada item está na rubrica correta",
                "Documente NF, recibo e termo de doação por exercício",
            ],
        },
        "srm": {
            "label": "Sala de Recursos / Inclusão",
            "what_is": (
                "A Sala de Recursos Multifuncionais (SRM) é o espaço de Atendimento Educacional "
                "Especializado (AEE) obrigatório em escolas com matrículas elegíveis. Recebe "
                "equipamentos de informática, tecnologia assistiva e mobiliário ergonômico."
            ),
            "impact": (
                "Implantar SRM exige checklist obrigatório de equipamentos e mobiliário, com "
                "laudos técnicos por item. Sem cumprir a Resolução, a prestação de contas é glosada."
            ),
            "action": [
                "Confirme se a SRM tem todos os itens previstos no Tipo 1 ou Tipo 2",
                "Verifique manutenção dos equipamentos e adequação do mobiliário",
                "Documente o uso pedagógico com plano de AEE assinado pelo conselho",
                "Capacite a equipe para o atendimento especializado",
            ],
        },
        "default": {
            "label": "FNDE/MEC",
            "what_is": (
                "O Ministério da Educação e o FNDE publicam regularmente normativas, repasses "
                "e programas que impactam a rotina das escolas e Unidades Executoras. Estar "
                "atento a essas publicações é parte essencial da gestão escolar."
            ),
            "impact": (
                "Cada nova publicação pode alterar prazos, regras de aplicação ou rubricas "
                "elegíveis. Vale revisar seu plano à luz da novidade antes de seguir com compras "
                "ou prestação de contas."
            ),
            "action": [
                "Acompanhe o portal oficial do FNDE para confirmar a publicação",
                "Verifique se sua escola está enquadrada no que mudou",
                "Atualize procedimentos internos se necessário",
                "Procure orientação técnica se tiver dúvidas",
            ],
        },
    }
    if "fundeb" in text:
        return themes["fundeb"]
    if "pdde" in text:
        return themes["pdde"]
    if "srm" in text or "sala de recursos" in text or "inclusão" in text or "aee" in text:
        return themes["srm"]
    return themes["default"]


def build_blog_content(title: str, description: str, theme: dict, quote_block: dict) -> list:
    """Monta o array de blocos do blog post — conteudo substancial + CTA."""
    blocks = []

    # Resumo (callout no topo)
    blocks.append({
        "kind": "callout",
        "tone": "info",
        "title": "Resumo",
        "text": description or f"Publicação oficial referente a {theme['label']}. Confira a análise abaixo.",
    })

    # Seção 1: contexto
    blocks.append({"kind": "h2", "text": f"O que é {theme['label']} e por que essa notícia importa"})
    blocks.append({"kind": "p", "text": theme["what_is"]})
    blocks.append({"kind": "p", "text": theme["impact"]})

    # Citação da notícia
    blocks.append(quote_block)

    # Seção 2: como agir (checklist)
    blocks.append({"kind": "h2", "text": "Como agir agora"})
    blocks.append({
        "kind": "p",
        "text": "Esses são os passos práticos que sugerimos pra gestores escolares e UEx diante desse tipo de publicação:",
    })
    blocks.append({
        "kind": "checklist",
        "items": [{"ok": False, "text": item} for item in theme["action"]],
    })

    # Seção 3: como a Supra ajuda
    blocks.append({"kind": "h2", "text": "Como a Supra AM pode te apoiar"})
    blocks.append({
        "kind": "p",
        "text": (
            "Trabalhamos há anos com escolas e Unidades Executoras do Norte do Brasil. Cada "
            "orçamento que entregamos vem com enquadramento FNDE já correto, descrição técnica "
            "padronizada na nota fiscal e logística calculada pra realidade do interior. "
            "Você ganha tempo e elimina o risco de glosa na prestação de contas."
        ),
    })

    # CTA final — botão pra orçamento
    blocks.append({
        "kind": "cta",
        "title": "Quer apoio técnico pra aplicar bem esse recurso?",
        "text": (
            "Solicite um orçamento técnico com a Supra AM. Avaliamos sua demanda, sugerimos os "
            "kits adequados pra sua escola e entregamos com documentação pronta pra prestação de contas."
        ),
        "buttonLabel": "Solicitar orçamento",
        "buttonHref": "/orcamento",
    })

    return blocks


def append_blog_entry(article: dict, summary: dict, post_dir: Path):
    """Anexa entrada em Site_FNDE/src/data/news.ts (se Site_FNDE existir)."""
    if not SITE_FNDE_ROOT.exists():
        print("  [info] Site_FNDE nao acessivel, pulando blog entry.")
        return

    title = best_title(article, summary)
    description = best_description(article, summary, title)[:280]
    source_url = article.get("resolved_link") or article["link"]
    source_name = article.get("source_name", "Fonte oficial")
    slug = slugify(title)
    today_br = datetime.now(timezone.utc).strftime("%d %b %Y").lower()
    has_real_url = source_url and "news.google.com" not in source_url

    quote_block = {"kind": "quote", "text": title, "source": source_name}
    if has_real_url:
        quote_block["sourceLink"] = source_url

    theme = detect_theme(title, description)
    content_blocks = build_blog_content(title, description, theme, quote_block)

    entry = {
        "slug": slug,
        "tag": "Novidade FNDE",
        "date": today_br,
        "title": title,
        "excerpt": description or f"Novidade {theme['label']}: acompanhamento institucional pela equipe Supra AM.",
        "readingTime": "4 min",
        "authorName": "Equipe Supra AM",
        "authorRole": "Monitoramento FNDE/MEC",
        "heroImage": "/blog/como-funciona-pdde-2026.jpg",
        "content": content_blocks,
    }
    _gen_at = datetime.now(timezone.utc).isoformat()

    SITE_NEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SITE_NEWS_FILE.exists():
        content = SITE_NEWS_FILE.read_text(encoding="utf-8")
        marker = "// AUTO-GEN BLOG ENTRIES BELOW"
        if marker in content:
            new_block = f"\n  /* {_gen_at} */\n  {json.dumps(entry, ensure_ascii=False, indent=2)},\n"
            content = content.replace(marker, marker + new_block, 1)
            SITE_NEWS_FILE.write_text(content, encoding="utf-8")
        else:
            print(f"  [aviso] {SITE_NEWS_FILE.name} sem marker, recriando")
            _create_news_file(entry, _gen_at)
    else:
        _create_news_file(entry, _gen_at)
    print(f"  [blog] {slug} adicionado em {SITE_NEWS_FILE.name}")


def _create_news_file(entry: dict, gen_at: str):
    content = f'''import type {{ BlogPost }} from "./blog";

// Entradas auto-geradas pelo monitor de noticias.
// NAO EDITAR manualmente abaixo do marker.
export const newsPosts: BlogPost[] = [
  // AUTO-GEN BLOG ENTRIES BELOW
  /* {gen_at} */
  {json.dumps(entry, ensure_ascii=False, indent=2)},
];
'''
    SITE_NEWS_FILE.write_text(content, encoding="utf-8")


def generate_for(article: dict):
    """Pipeline completo pra 1 artigo."""
    print(f"\nProcessando: {article['title'][:80]}...")
    summary = fetch_article_summary(
        article.get("resolved_link") or article["link"]
    )
    post_dir = render_post_dir(article, summary)
    print(f"  [post] queued em {post_dir.name}")
    append_blog_entry(article, summary, post_dir)
    return post_dir


if __name__ == "__main__":
    print("Use via monitor.py — esse script nao tem CLI direto.")
