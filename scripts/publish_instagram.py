"""
publish_instagram.py - Publica posts/carrosseis no @grupo.supraam via Instagram Graph API.

Usa a API NOVA do Instagram (instagram_business_*) que roda em graph.instagram.com.

Uso:
  python publish_instagram.py --post-dir content/approved/2026-06-05_post1
  python publish_instagram.py --post-dir content/approved/2026-06-05_post1 --dry-run

Espera dentro do --post-dir:
  - post.json   (com chave "caption")
  - 1+ imagens .png/.jpg (ordenadas por nome)
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

IG_USER_ID = os.getenv("INSTAGRAM_USER_ID")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
API_VERSION = os.getenv("META_API_VERSION", "v23.0")
BASE_URL = f"https://graph.instagram.com/{API_VERSION}"


UPLOAD_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 SupraBot/1.0"


def _upload_0x0(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://0x0.st",
            files={"file": (image_path.name, f, "image/png")},
            headers={"User-Agent": UPLOAD_UA},
            timeout=60,
        )
    url = resp.text.strip()
    if not url.startswith("https://"):
        raise RuntimeError(f"0x0.st rejeitou: {url[:200]}")
    return url


def _upload_catbox(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": (image_path.name, f, "image/png")},
            headers={"User-Agent": UPLOAD_UA},
            timeout=60,
        )
    url = resp.text.strip()
    if not url.startswith("https://"):
        raise RuntimeError(f"catbox.moe rejeitou: {url[:200]}")
    return url


def _raw_github_url(image_path: Path) -> str | None:
    """Se rodando no GitHub Actions (repo publico), monta a URL raw direto."""
    repo = os.getenv("GITHUB_REPOSITORY")
    sha = os.getenv("GITHUB_SHA")
    if not repo or not sha:
        return None
    rel = image_path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    return f"https://raw.githubusercontent.com/{repo}/{sha}/{rel}"


def host_image(image_path: Path) -> str:
    """Hospeda imagem em URL publica. Em GH Actions usa raw URL (repo publico).
    Localmente, tenta 0x0.st -> catbox.moe."""
    print(f"  Hospedando {image_path.name}...")

    gh_url = _raw_github_url(image_path)
    if gh_url:
        print(f"    URL (GH raw): {gh_url}")
        return gh_url

    errors = []
    for fn in (_upload_0x0, _upload_catbox):
        try:
            url = fn(image_path)
            print(f"    URL: {url}")
            return url
        except Exception as e:
            errors.append(f"{fn.__name__}: {e}")
    raise RuntimeError("Todos os hosts falharam: " + " | ".join(errors))


def create_single_container(image_url: str, caption: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/{IG_USER_ID}/media",
        data={"access_token": ACCESS_TOKEN, "image_url": image_url, "caption": caption},
        timeout=60,
    )
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar container: {result}")
    return result["id"]


def create_carousel_item(image_url: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/{IG_USER_ID}/media",
        data={
            "access_token": ACCESS_TOKEN,
            "image_url": image_url,
            "is_carousel_item": "true",
        },
        timeout=60,
    )
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar item de carrossel: {result}")
    return result["id"]


def create_carousel(media_ids: list, caption: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/{IG_USER_ID}/media",
        data={
            "access_token": ACCESS_TOKEN,
            "media_type": "CAROUSEL",
            "children": ",".join(media_ids),
            "caption": caption,
        },
        timeout=30,
    )
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao montar carrossel: {result}")
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
        print(f"  Processando... {i * 5}s ({status or 'IN_PROGRESS'})")
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
        raise RuntimeError(f"Erro ao publicar: {result}")
    return result["id"]


def load_post(post_dir: Path) -> tuple[str, list[Path]]:
    meta_file = post_dir / "post.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"Nao achei post.json em {post_dir}")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    caption = meta.get("caption", "").strip()
    if not caption:
        raise ValueError("post.json sem 'caption'")

    images = sorted(
        [p for p in post_dir.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")]
    )
    if not images:
        raise FileNotFoundError(f"Nenhuma imagem em {post_dir}")
    if len(images) > 10:
        raise ValueError("Instagram permite no maximo 10 imagens por carrossel")
    return caption, images


def archive_post(post_dir: Path, post_id: str):
    """Move post de /approved/ para /published/ apos publicacao."""
    published_dir = PROJECT_ROOT / "content" / "published"
    published_dir.mkdir(parents=True, exist_ok=True)
    target = published_dir / post_dir.name
    if target.exists():
        target = published_dir / f"{post_dir.name}_{post_id}"
    post_dir.rename(target)

    receipt = target / "publish_receipt.json"
    receipt.write_text(
        json.dumps(
            {
                "post_id": post_id,
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "instagram_handle": os.getenv("INSTAGRAM_HANDLE", ""),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  Arquivado em: {target}")


def run(post_dir: Path, dry_run: bool = False):
    if not IG_USER_ID or not ACCESS_TOKEN:
        print("ERRO: credenciais nao configuradas. Preencha o .env.")
        sys.exit(1)

    caption, images = load_post(post_dir)
    print(f"\nPost: {post_dir.name}")
    print(f"Imagens: {len(images)}")
    print(f"Caption ({len(caption)} chars):\n  {caption[:120]}...")

    if dry_run:
        print("\n[DRY RUN] Tudo OK. Remova --dry-run para publicar de verdade.")
        return

    print("\n[1/4] Hospedando imagens...")
    image_urls = [host_image(img) for img in images]

    print("\n[2/4] Criando containers de midia...")
    if len(images) == 1:
        container_id = create_single_container(image_urls[0], caption)
    else:
        item_ids = [create_carousel_item(url) for url in image_urls]
        container_id = create_carousel(item_ids, caption)
    print(f"  Container final: {container_id}")

    print("\n[3/4] Aguardando processamento do Instagram...")
    if not wait_ready(container_id):
        print("ERRO: Timeout no processamento.")
        sys.exit(1)

    print("\n[4/4] Publicando...")
    post_id = publish_container(container_id)
    print(f"\n>>> PUBLICADO! Post ID: {post_id}")

    archive_post(post_dir, post_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--post-dir", required=True, help="Pasta com post.json e imagens"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(Path(args.post_dir), args.dry_run)
