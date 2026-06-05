"""
monitor.py - Busca Google News RSS por keywords do nicho Supra AM.
Filtra por fontes confiaveis (gov.br + midia top). Salva state em /state/seen_articles.json.

Uso:
  python -m scripts.news.monitor              # acha + gera + queue
  python -m scripts.news.monitor --dry-run    # so acha, nao gera
  python -m scripts.news.monitor --limit 1    # processa max N articles novos
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import requests

PROJECT_ROOT = Path(__file__).parent.parent.parent
STATE_FILE = PROJECT_ROOT / "state" / "seen_articles.json"

# Queries combinadas (uma busca Google News por linha)
QUERIES = [
    "FNDE PDDE repasse escolas",
    "FNDE PDDE Equidade Qualidade Resolução",
    "Ministério Educação recurso transferência escola",
    "MEC repassa bilhões Fundeb educação básica",
    "Fundeb repasse estados municípios",
    "Educação Conectada PDDE Conectividade",
    "Sala Recursos Multifuncionais SRM AEE inclusão",
    "Censo escolar Amazonas educação básica",
    "PDDE Amazonas escolas ribeirinhas",
    "Cantinho da Leitura PDDE FNDE",
    "Compras públicas educação licitação",
    "Mais Educação Tempo Integral FNDE",
    "Salário-educação repasse municípios",
]

# Domains confiaveis (whitelist forte)
TRUSTED_DOMAINS = (
    # Oficiais
    ".gov.br",
    "fnde.gov.br",
    "mec.gov.br",
    "in.gov.br",
    # Agencias publicas
    "agenciabrasil.ebc.com.br",
    "agenciagov.ebc.com.br",
    # Grandes midias
    "g1.globo.com",
    "valor.globo.com",
    "globo.com",
    "folha.uol.com.br",
    "estadao.com.br",
    "oglobo.globo.com",
    "uol.com.br",
    "cnnbrasil.com.br",
    "exame.com",
    "veja.abril.com.br",
    "metropoles.com",
    "noticias.r7.com",
    "r7.com",
    "jovempan.com.br",
    "brasil61.com",
    # Pacotes/agregadores B2G educacao (medias mas com cobertura forte)
    "radardigitalbrasilia",
    "conexao",
    "diariodopoder",
    "revistaoeste",
)

# Notícias mais antigas que isso são ignoradas (mantém o feed sempre fresco)
MAX_AGE_DAYS = 7

# Palavras de impacto que dão "boost" pra noticia (sao publicadas mesmo se source for menos famoso)
IMPACT_KEYWORDS = (
    "repasse", "repassa", "libera", "anuncia", "anunciou",
    "bilhão", "bilhões", "milhão", "milhões",
    "r$", "fundeb", "salário-educação", "transferência",
)

# Palavras-chave que indicam noticia relevante (precisa ter pelo menos 1)
RELEVANCE_KEYWORDS = (
    "fnde",
    "pdde",
    "mec",
    "educa",
    "escolas",
    "escolar",
    "repasse",
    "verba",
    "recurso",
    "censo",
    "inclus",
    "aee",
    "srm",
    "bncc",
    "ideb",
    "ribeirinha",
    "amazonas",
)

# Palavras-chave que DESQUALIFICAM (excluem)
BLOCKLIST = (
    "universidade",
    "ensino superior",
    "fuvest",
    "enem",
    "vestibular",
    "particular",
    "privada",
)


def fetch_google_news_rss(query: str) -> list[dict]:
    url = (
        "https://news.google.com/rss/search?q="
        + quote_plus(query)
        + "&hl=pt-BR&gl=BR&ceid=BR:pt"
    )
    try:
        resp = requests.get(
            url, timeout=20, headers={"User-Agent": "Mozilla/5.0 SupraNews/1.0"}
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"  [erro] {query}: {e}", file=sys.stderr)
        return []

    items = []
    try:
        root = ET.fromstring(resp.content)
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            desc = (item.findtext("description") or "").strip()
            source_elem = item.find("source")
            source_name = source_elem.text if source_elem is not None else ""
            source_url = (
                source_elem.get("url") if source_elem is not None else ""
            )
            if not title or not link:
                continue
            items.append(
                {
                    "title": title,
                    "link": link,
                    "pub_date": pub_date,
                    "description": desc,
                    "source_name": source_name or _domain(source_url or link),
                    "source_url": source_url,
                    "query": query,
                }
            )
    except ET.ParseError as e:
        print(f"  [parse] {query}: {e}", file=sys.stderr)
    return items


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url


def _signature(title: str, desc: str) -> str | None:
    """Gera assinatura unica para deduplicar a mesma noticia em fontes diferentes.

    Usa o primeiro valor R$ + tipo (bilh/milh) + tema (fundeb/pdde/etc).
    Ex: 'r$4,8bilh/fundeb' identifica essa noticia independente da fonte.
    """
    text = (title + " " + desc).lower()
    # extrai R$ X,Y bilhao/milhao
    m = re.search(
        r"r\$\s*([\d,\.]+)\s*(bilh\w+|milh\w+)",
        text,
    )
    if not m:
        return None
    valor = m.group(1).replace(".", "").replace(",", ".")
    unidade = "bilh" if "bilh" in m.group(2) else "milh"
    # detecta o tema (fundeb, pdde, salario-educacao, etc.)
    temas = ("fundeb", "pdde", "fnde", "salário-educação", "salario-educacao",
             "educacao conectada", "educacao basica", "merenda")
    tema = next((t for t in temas if t.replace("-", " ") in text or t in text), "geral")
    return f"r${valor}{unidade}/{tema}"


def _resolve_redirect(link: str) -> str:
    """Google News usa link redirect com JS. Best-effort fallback."""
    try:
        resp = requests.head(
            link, allow_redirects=True, timeout=8, headers={"User-Agent": "Mozilla/5.0"}
        )
        if "google" not in resp.url:
            return resp.url
    except Exception:
        pass
    return link


def is_trusted(item: dict) -> bool:
    """Confia no source_url do RSS (Google News injeta o dominio real)."""
    candidates = [
        item.get("source_url", ""),
        item.get("resolved_link", ""),
        item.get("source_name", "").lower().replace(".", "").replace(" ", ""),
    ]
    # Extrai sufixo "- GOV.BR" / "- G1" do titulo
    title = item.get("title", "")
    m = re.search(r"\s-\s([^-]+)$", title)
    if m:
        candidates.append(m.group(1).strip().lower())
    blob = " ".join(c for c in candidates if c).lower()
    return any(d.lower() in blob for d in TRUSTED_DOMAINS)


def is_relevant(title: str, description: str) -> bool:
    text = (title + " " + description).lower()
    if any(b in text for b in BLOCKLIST):
        return False
    return any(k in text for k in RELEVANCE_KEYWORDS)


def has_impact(title: str, description: str) -> bool:
    text = (title + " " + description).lower()
    return any(k in text for k in IMPACT_KEYWORDS)


def is_recent(pub_date_str: str) -> bool:
    """True se noticia foi publicada nos ultimos MAX_AGE_DAYS dias."""
    if not pub_date_str:
        return False
    from datetime import datetime, timezone, timedelta
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            dt = datetime.strptime(pub_date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
            return dt >= cutoff
        except ValueError:
            continue
    return False


def load_seen() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_seen(seen: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def find_new_articles(limit: int = None) -> list[dict]:
    seen = load_seen()

    # HARD CAP: max 1 noticia publicada por dia (anti-spam algoritmico)
    from datetime import datetime, timezone, timedelta
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    published_today = sum(
        1 for v in seen.values()
        if isinstance(v, dict)
        and not v.get("skipped_duplicate_of_signature")
        and v.get("found_at", "").startswith(today_utc)
    )
    if published_today >= 1:
        print(f"[hard-cap] Ja foi publicada 1 noticia hoje ({today_utc}). Pulando.")
        return []

    new = []
    seen_keys = set(seen.keys())
    seen_signatures = {
        v.get("signature") for v in seen.values() if isinstance(v, dict) and v.get("signature")
    }
    new_signatures_this_run = set()  # evita duplicar dentro da mesma execucao
    all_items = []
    for q in QUERIES:
        all_items.extend(fetch_google_news_rss(q))

    # Dedupe por titulo (Google News retorna mesma noticia em queries diferentes)
    by_title = {}
    for item in all_items:
        key = re.sub(r"\s+", " ", item["title"].lower())[:120]
        if key not in by_title:
            by_title[key] = item

    # Score + filtro
    scored = []
    for item in by_title.values():
        title = item["title"]
        desc = item.get("description", "")
        pub = item.get("pub_date", "")

        if not is_recent(pub):
            continue
        if not is_relevant(title, desc):
            continue

        impact = has_impact(title, desc)
        trusted = is_trusted(item)

        # Regras de admissão:
        # - se fonte confiável: aceita sempre
        # - se fonte secundária mas com impacto (R$, repasse, bilhões): aceita
        # - caso contrário: descarta
        if not (trusted or impact):
            continue

        # Score: impact (+2) + trusted (+1) — usado pra ordenar
        score = (2 if impact else 0) + (1 if trusted else 0)
        # Sort secundário: data mais nova primeiro
        scored.append((score, pub, item))

    # Ordena por score desc, depois data desc
    scored.sort(key=lambda x: (-x[0], x[1]), reverse=False)
    scored.sort(key=lambda x: x[0], reverse=True)

    for _, _, item in scored:
        article_key = item["link"]
        if article_key in seen_keys:
            continue

        # Dedup semantico: mesma noticia em fontes diferentes
        sig = _signature(item["title"], item.get("description", ""))
        if sig and (sig in seen_signatures or sig in new_signatures_this_run):
            # Marca como visto pra nao reaparecer, mas nao gera post
            seen[article_key] = {
                "title": item["title"],
                "found_at": datetime.now(timezone.utc).isoformat(),
                "source": item.get("source_name", ""),
                "skipped_duplicate_of_signature": sig,
            }
            continue

        item["resolved_link"] = _resolve_redirect(item["link"])
        new.append(item)
        seen[article_key] = {
            "title": item["title"],
            "found_at": datetime.now(timezone.utc).isoformat(),
            "source": item.get("source_name") or _domain(item["resolved_link"]),
            "signature": sig,
        }
        if sig:
            new_signatures_this_run.add(sig)
        if limit and len(new) >= limit:
            break

    save_seen(seen)
    return new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Apenas lista")
    parser.add_argument("--limit", type=int, default=1, help="Max novos por exec")
    args = parser.parse_args()

    print("Buscando novidades governamentais...")
    new = find_new_articles(limit=args.limit)
    if not new:
        print("Sem novidades.")
        return

    print(f"\n>> {len(new)} noticia(s) nova(s):")
    for n in new:
        print(f"  - {n['title']}")
        print(f"    {_domain(n['resolved_link'])} | {n['pub_date']}")

    if args.dry_run:
        return

    # Importa e chama o gerador
    from scripts.news.generate_post import generate_for
    for n in new:
        try:
            generate_for(n)
        except Exception as e:
            print(f"  [erro gerando post] {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
