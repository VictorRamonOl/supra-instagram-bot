"""
publish_next_approved.py - Publica o proximo post aprovado.

Logica:
  1. Olha em content/approved/ por subpastas com post.json
  2. Pega a mais antiga (alfabetica)
  3. Chama publish_instagram.run() nela
  4. Se nao houver nada aprovado, registra em content/_logs/ e sai

Esse script eh ideal para ser chamado por agendador (Windows Task Scheduler
ou cron) a cada 3 dias.
"""
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
APPROVED_DIR = PROJECT_ROOT / "content" / "approved"
NEWS_QUEUE_DIR = PROJECT_ROOT / "content" / "news_queue"
LOG_DIR = PROJECT_ROOT / "content" / "_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).parent))
import publish_instagram
import refresh_token


def log(msg: str):
    print(msg)
    log_file = LOG_DIR / f"auto_publish_{time.strftime('%Y-%m')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def find_next_approved() -> Path | None:
    # 1. Prioridade: news_queue (notícias fura fila)
    if NEWS_QUEUE_DIR.exists():
        news = sorted(
            [
                d
                for d in NEWS_QUEUE_DIR.iterdir()
                if d.is_dir() and (d / "post.json").exists()
            ]
        )
        if news:
            return news[0]

    # 2. Fila regular de aprovados
    if not APPROVED_DIR.exists():
        return None
    candidates = sorted(
        [
            d
            for d in APPROVED_DIR.iterdir()
            if d.is_dir() and (d / "post.json").exists()
        ]
    )
    return candidates[0] if candidates else None


def main():
    log("Renovando token se necessario...")
    try:
        refresh_token.main(force=False)
    except Exception as e:
        log(f"AVISO ao tentar renovar token: {e}")

    log("Verificando posts aprovados...")
    next_post = find_next_approved()

    if next_post is None:
        log("AVISO: Nenhum post aprovado disponivel. Gere conteudo novo no Claude Code.")
        flag_file = LOG_DIR / "needs_content.flag"
        flag_file.write_text(
            json.dumps(
                {
                    "flagged_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "message": "Fila de aprovados vazia. Abra o Claude Code e peca para gerar novos posts.",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        sys.exit(2)

    log(f"Publicando: {next_post.name}")
    try:
        publish_instagram.run(next_post, dry_run=False)
        log(f"Sucesso: {next_post.name}")
    except Exception as e:
        log(f"ERRO ao publicar {next_post.name}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
