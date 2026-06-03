"""
refresh_token.py - Renova o long-lived token do Instagram (estende +60 dias).

Logica:
  - Le INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_TOKEN_REFRESHED_AT do .env
  - Se token foi renovado ha mais de 25 dias, chama o endpoint de refresh
  - Atualiza .env com token novo e nova data
  - Idempotente: se ainda esta fresco, nao faz nada

Pode ser chamado:
  python refresh_token.py            # so renova se precisa
  python refresh_token.py --force    # forca renovacao agora
"""
import argparse
import os
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

REFRESH_AFTER_DAYS = 25  # renova quando ja se passaram 25 dias do ultimo refresh


def get_token_age_days() -> int:
    refreshed_at = os.getenv("INSTAGRAM_TOKEN_REFRESHED_AT", "")
    if not refreshed_at:
        return 999  # forca refresh se nao tem registro
    try:
        last = datetime.strptime(refreshed_at, "%Y-%m-%d").date()
        return (date.today() - last).days
    except ValueError:
        return 999


def refresh() -> tuple[str, int]:
    """Chama o endpoint refresh_access_token. Retorna (novo_token, segundos_validade)."""
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN nao encontrado no .env")

    resp = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
        timeout=30,
    )
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"Refresh falhou: {data}")
    return data["access_token"], data.get("expires_in", 0)


def update_env(new_token: str):
    """Atualiza INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_TOKEN_REFRESHED_AT no .env."""
    today = date.today().strftime("%Y-%m-%d")
    content = ENV_FILE.read_text(encoding="utf-8")

    content = re.sub(
        r"^INSTAGRAM_ACCESS_TOKEN=.*$",
        f"INSTAGRAM_ACCESS_TOKEN={new_token}",
        content,
        flags=re.MULTILINE,
    )
    if "INSTAGRAM_TOKEN_REFRESHED_AT=" in content:
        content = re.sub(
            r"^INSTAGRAM_TOKEN_REFRESHED_AT=.*$",
            f"INSTAGRAM_TOKEN_REFRESHED_AT={today}",
            content,
            flags=re.MULTILINE,
        )
    else:
        content += f"\nINSTAGRAM_TOKEN_REFRESHED_AT={today}\n"

    ENV_FILE.write_text(content, encoding="utf-8")


def main(force: bool = False):
    age = get_token_age_days()
    print(f"Token tem {age} dias desde ultimo refresh.")

    if not force and age < REFRESH_AFTER_DAYS:
        print(f"Ainda fresco (limite: {REFRESH_AFTER_DAYS} dias). Nada a fazer.")
        return

    print("Renovando token...")
    new_token, expires_in = refresh()
    update_env(new_token)
    print(f"Token renovado! Validade: ~{expires_in // 86400} dias.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Forca renovacao")
    args = parser.parse_args()
    try:
        main(force=args.force)
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
