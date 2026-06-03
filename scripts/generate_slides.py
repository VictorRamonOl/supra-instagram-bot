"""
generate_slides.py - Le um batch JSON e gera todas as pastas + PNGs em content/pending/.

Uso:
  python generate_slides.py --batch content/_specs/batch_001.json
  python generate_slides.py --batch content/_specs/batch_001.json --only 01,02
"""
import argparse
import html
import json
import shutil
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATE_FILE = Path(__file__).parent / "templates" / "slide_template.html"
PENDING_DIR = PROJECT_ROOT / "content" / "pending"


def render_hook(slide: dict) -> str:
    return f"""
    <div class="label">SUPRA AM</div>
    <h1>{html.escape(slide.get('headline', ''))}</h1>
    <div class="subhead">{html.escape(slide.get('subheadline', ''))}</div>
    """


def render_content(slide: dict) -> str:
    kicker = slide.get("kicker", "")
    return f"""
    {'<div class="kicker">' + html.escape(kicker) + '</div>' if kicker else ''}
    <h2>{html.escape(slide.get('headline', ''))}</h2>
    <div class="body">{html.escape(slide.get('body', ''))}</div>
    """


def render_data_list(slide: dict) -> str:
    kicker = slide.get("kicker", "")
    items_html = "\n".join(f"<li>{html.escape(item)}</li>" for item in slide.get("items", []))
    body = slide.get("body", "")
    body_html = f'<div class="body" style="margin-bottom:32px">{html.escape(body)}</div>' if body else ""
    return f"""
    {'<div class="kicker">' + html.escape(kicker) + '</div>' if kicker else ''}
    <h2>{html.escape(slide.get('headline', ''))}</h2>
    {body_html}
    <ul>{items_html}</ul>
    """


def render_comparison(slide: dict) -> str:
    kicker = slide.get("kicker", "")
    columns_html = ""
    for col in slide.get("columns", []):
        rows_html = "\n".join(f'<div class="col-row">{html.escape(r)}</div>' for r in col.get("rows", []))
        columns_html += f'<div class="col"><div class="col-name">{html.escape(col["name"])}</div>{rows_html}</div>'
    return f"""
    {'<div class="kicker">' + html.escape(kicker) + '</div>' if kicker else ''}
    <h2>{html.escape(slide.get('headline', ''))}</h2>
    <div class="columns">{columns_html}</div>
    """


def render_cta(slide: dict) -> str:
    handle = slide.get("footer", "@grupo.supraam")
    return f"""
    <h2>{html.escape(slide.get('headline', ''))}</h2>
    <div class="body">{html.escape(slide.get('body', ''))}</div>
    <div class="handle">{html.escape(handle)}</div>
    """


RENDERERS = {
    "hook": render_hook,
    "content": render_content,
    "data": render_data_list,
    "list": render_data_list,
    "comparison": render_comparison,
    "cta": render_cta,
}


def build_slide_html(slide: dict, page_label: str, template: str) -> str:
    slide_type = slide.get("type", "content")
    renderer = RENDERERS.get(slide_type, render_content)
    content_html = renderer(slide)
    return (
        template
        .replace("{{TYPE}}", slide_type)
        .replace("{{CONTENT_HTML}}", content_html)
        .replace("{{PAGE_LABEL}}", page_label)
    )


def render_slide_to_png(html_string: str, output_png: Path, browser):
    page = browser.new_page(viewport={"width": 1080, "height": 1080})
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
        f.write(html_string)
        temp_html = Path(f.name)
    try:
        page.goto(f"file:///{temp_html.as_posix()}", wait_until="networkidle")
        page.wait_for_timeout(400)  # da tempo para fontes do Google
        page.screenshot(path=str(output_png), full_page=False, omit_background=False)
    finally:
        page.close()
        temp_html.unlink(missing_ok=True)


def process_post(post: dict, template: str, browser):
    post_id = post["id"]
    slug = post["slug"]
    folder_name = f"{post_id}_{post['scheduled_for']}_{slug}"
    post_dir = PENDING_DIR / folder_name

    if post_dir.exists():
        print(f"  [skip] {folder_name} ja existe — apagando para regenerar")
        shutil.rmtree(post_dir)
    post_dir.mkdir(parents=True, exist_ok=True)

    slides = post["slides"]
    total = len(slides)
    for i, slide in enumerate(slides, start=1):
        page_label = f"{i:02d} / {total:02d}"
        html_string = build_slide_html(slide, page_label, template)
        out_png = post_dir / f"slide_{i:02d}.png"
        print(f"    -> slide {i}/{total}")
        render_slide_to_png(html_string, out_png, browser)

    post_meta = {
        "id": post_id,
        "slug": slug,
        "scheduled_for": post["scheduled_for"],
        "pillar": post["pillar"],
        "format": post["format"],
        "caption": post["caption"] + "\n\n" + post.get("hashtags", ""),
        "slides_count": total,
        "status": "pending_review",
    }
    (post_dir / "post.json").write_text(
        json.dumps(post_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [ok] {folder_name} ({total} slides)")


def main(batch_file: Path, only: set | None):
    batch = json.loads(batch_file.read_text(encoding="utf-8"))
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    posts = batch["posts"]
    if only:
        posts = [p for p in posts if p["id"] in only]

    print(f"\nGerando {len(posts)} posts...\n")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for post in posts:
                print(f"\n[{post['id']}] {post['slug']}")
                process_post(post, template, browser)
        finally:
            browser.close()

    print(f"\n>>> Pronto! Arquivos em: {PENDING_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True, help="Caminho do arquivo batch JSON")
    parser.add_argument("--only", default="", help="IDs de posts a processar, separados por virgula")
    args = parser.parse_args()
    only = set(x.strip() for x in args.only.split(",") if x.strip()) or None
    main(Path(args.batch), only)
