"""
indexnow.py — Notifica IndexNow (Bing / Yandex / Seznam / Naver) de URLs novas/atualizadas.

A chave do IndexNow é apenas um identificador hexadecimal. Bing valida buscando
o arquivo em https://supraam.com.br/<KEY>.txt (que ja esta hospedado no Site_FNDE).

Fluxo:
  1. Quando o news monitor gera uma entrada nova de blog, chama add_pending(url)
  2. state/pending_indexnow.json acumula URLs novas
  3. Apos o push pro Site_FNDE (Vercel deploy ~60s), workflow chama flush_pending()
  4. Bing/Yandex sao notificados em lote
  5. URLs sao indexadas em <1h (vs dias do crawl tradicional)

Uso:
  - CLI direto:  python -m scripts.news.indexnow https://supraam.com.br/blog/slug
  - Sem args:    le state/pending_indexnow.json e flush
  - Programatico: notify_indexnow(["https://..."])
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Iterable

import requests

PROJECT_ROOT = Path(__file__).parent.parent.parent
PENDING_FILE = PROJECT_ROOT / "state" / "pending_indexnow.json"

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
HOST = "supraam.com.br"
# Chave IndexNow do Site_FNDE. Esta hospedada em <HOST>/<KEY>.txt (Bing valida buscando isso).
# Como a chave fica em URL publica, nao tem sentido manter "secreta" — hardcode esta OK.
# Override via INDEXNOW_KEY se quiser rotacionar.
DEFAULT_KEY = "284142c04864c67111610badd2ccd911ff94b411a3c3dd9759d2bc99d0ae7bd8"
KEY_LOCATION = f"https://{HOST}/{DEFAULT_KEY}.txt"


def _read_pending() -> list[str]:
    if not PENDING_FILE.exists():
        return []
    try:
        data = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(u) for u in data]
    except Exception:
        pass
    return []


def _write_pending(urls: list[str]) -> None:
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_FILE.write_text(
        json.dumps(urls, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_pending(url: str) -> None:
    """Adiciona uma URL na fila local pra envio batch posterior."""
    if not url:
        return
    pending = _read_pending()
    if url in pending:
        return
    pending.append(url)
    _write_pending(pending)
    print(f"  [indexnow] pending +{url}")


def notify_indexnow(urls: Iterable[str], key: str | None = None) -> bool:
    """
    Envia POST pro IndexNow com 1 ou mais URLs.
    Retorna True se aceito (status 200 ou 202).
    """
    url_list = [u for u in urls if u]
    if not url_list:
        print("[indexnow] sem URLs pra notificar.")
        return False

    key = key or os.getenv("INDEXNOW_KEY") or DEFAULT_KEY
    if not key:
        print("[indexnow] sem chave; pulando.")
        return False

    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": KEY_LOCATION,
        "urlList": url_list,
    }

    try:
        resp = requests.post(
            INDEXNOW_ENDPOINT,
            json=payload,
            timeout=20,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
    except Exception as e:
        print(f"[indexnow] erro de rede: {e}")
        return False

    if resp.status_code in (200, 202):
        print(f"[indexnow] OK ({resp.status_code}) — {len(url_list)} URL(s) notificada(s)")
        for u in url_list:
            print(f"           -> {u}")
        return True

    # 400 = bad request | 403 = chave invalida | 422 = URLs invalidas | 429 = rate limit
    print(f"[indexnow] HTTP {resp.status_code}: {resp.text[:300]}")
    return False


def flush_pending() -> int:
    """Le pending file, notifica IndexNow, limpa file. Retorna contagem enviada."""
    urls = _read_pending()
    if not urls:
        print("[indexnow] pending file vazio; nada a fazer.")
        return 0

    if notify_indexnow(urls):
        # Limpa o pending file (mantem arquivo vazio pra ficar visivel)
        _write_pending([])
        return len(urls)

    print("[indexnow] falha — mantendo pending pra proxima tentativa.")
    return 0


def main():
    args = sys.argv[1:]
    if args:
        # Modo CLI: usa URLs dos args
        ok = notify_indexnow(args)
        sys.exit(0 if ok else 1)

    # Modo flush: pega do pending file
    n = flush_pending()
    print(f"[indexnow] {n} URL(s) processada(s).")


if __name__ == "__main__":
    main()
