"""
publish_story.py - Publica 1 Story no @grupo.supraam via Instagram Graph API.

Logica:
  1. Gera o proximo story pendente (chama generate_story)
  2. Publica como Story usando media_type=STORIES
  3. Marca como publicado em state/published_stories.json
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

IG_USER_ID = os.getenv("INSTAGRAM_USER_ID")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
API_VERSION = os.getenv("META_API_VERSION", "v23.0")
BASE_URL = f"https://graph.instagram.com/{API_VERSION}"

sys.path.insert(0, str(Path(__file__).parent))
from generate_story import main as generate_story_main, mark_published


def github_raw_url(image_path: Path) -> str:
    """Constroi raw URL do GitHub. Usa branch master (nao SHA) pra refletir commit recem-feito."""
    repo = os.getenv("GITHUB_REPOSITORY")
    if not repo:
        raise RuntimeError(
            "GITHUB_REPOSITORY nao setado. Story publishing precisa rodar em GH Actions."
        )
    rel = image_path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    return f"https://raw.githubusercontent.com/{repo}/master/{rel}"


def commit_and_push_story(image_path: Path):
    """Commita e empurra a imagem do story pra master, pra raw URL ficar acessivel."""
    import subprocess
    rel = image_path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    print(f"  Commitando {rel} pro master...")
    subprocess.run(["git", "config", "user.name", "supra-story-bot"], check=True, cwd=PROJECT_ROOT)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True, cwd=PROJECT_ROOT)
    subprocess.run(["git", "add", rel], check=True, cwd=PROJECT_ROOT)
    subprocess.run(
        ["git", "commit", "-m", f"story: img {Path(rel).parent.name}"],
        check=True, cwd=PROJECT_ROOT,
    )
    subprocess.run(["git", "push", "origin", "HEAD:master"], check=True, cwd=PROJECT_ROOT)
    # Espera CDN do GitHub atualizar
    time.sleep(8)


def create_story_container(image_url: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/{IG_USER_ID}/media",
        data={
            "access_token": ACCESS_TOKEN,
            "image_url": image_url,
            "media_type": "STORIES",
        },
        timeout=60,
    )
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar story container: {result}")
    return result["id"]


def wait_ready(container_id: str, max_attempts: int = 24) -> bool:
    for i in range(max_attempts):
        resp = requests.get(
            f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN},
            timeout=15,
        )
        status = resp.json().get("status_code", "")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"Container com erro: {resp.json()}")
        print(f"  Processando... {i*5}s ({status or 'IN_PROGRESS'})")
        time.sleep(5)
    return False


def publish_container(container_id: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/{IG_USER_ID}/media_publish",
        data={"access_token": ACCESS_TOKEN, "creation_id": container_id},
        timeout=30,
    )
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao publicar story: {result}")
    return result["id"]


def main():
    print("[1/4] Gerando proximo story pendente...")
    out_dir = generate_story_main()
    image = out_dir / "story.png"
    if not image.exists():
        raise RuntimeError(f"Imagem nao gerada: {image}")

    print("\n[2/4] Commitando + hospedando imagem (GitHub raw)...")
    if os.getenv("GITHUB_ACTIONS"):
        commit_and_push_story(image)
    url = github_raw_url(image)
    print(f"  URL: {url}")

    print("\n[3/4] Criando container Story...")
    container_id = create_story_container(url)
    print(f"  Container: {container_id}")

    if not wait_ready(container_id):
        raise RuntimeError("Timeout processamento.")

    print("\n[4/4] Publicando...")
    media_id = publish_container(container_id)
    print(f"\n>>> STORY PUBLICADO! ID: {media_id}")

    # Marca como publicado
    meta = json.loads((out_dir / "story.json").read_text(encoding="utf-8"))
    mark_published(meta["id"])
    print(f"  Marcado como publicado: {meta['id']}")


if __name__ == "__main__":
    main()
