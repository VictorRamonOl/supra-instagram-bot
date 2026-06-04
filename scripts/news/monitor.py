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
    "Educação Conectada PDDE Conectividade",
    "Sala Recursos Multifuncionais SRM AEE inclusão",
    "Censo escolar Amazonas educação básica",
    "PDDE Amazonas escolas ribeirinhas",
    "Cantinho da Leitura PDDE FNDE",
    "Compras públicas educação licitação",
    "Mais Educação Tempo Integral FNDE",
]

# Domains confiaveis (whitelist forte)
TRUSTED_DOMAINS = (
    ".gov.br",
    "fnde.gov.br",
    "mec.gov.br",
    "in.gov.br",
    "agenciabrasil.ebc.com.br",
    "agenciagov.ebc.com.br",
    "g1.globo.com",
    "valor.globo.com",
    "globo.com/educacao",
    "folha.uol.com.br",
    "estadao.com.br",
    "oglobo.globo.com",
    "uol.com.br/educacao",
    "cnnbrasil.com.br/educacao",
    "exame.com",
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
    new = []
    seen_keys = set(seen.keys())
    all_items = []
    for q in QUERIES:
        all_items.extend(fetch_google_news_rss(q))

    # Dedupe por titulo (Google News retorna mesma noticia em queries diferentes)
    by_title = {}
    for item in all_items:
        key = re.sub(r"\s+", " ", item["title"].lower())[:120]
        if key not in by_title:
            by_title[key] = item

    for item in by_title.values():
        # Filtra antes de resolver (mais rapido)
        if not is_trusted(item):
            continue
        if not is_relevant(item["title"], item.get("description", "")):
            continue

        # Dedup pela URL do Google News (estavel)
        article_key = item["link"]
        if article_key in seen_keys:
            continue

        # Resolve apenas dos que vamos processar
        item["resolved_link"] = _resolve_redirect(item["link"])

        new.append(item)
        seen[article_key] = {
            "title": item["title"],
            "found_at": datetime.now(timezone.utc).isoformat(),
            "source": item.get("source_name") or _domain(item["resolved_link"]),
        }

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
