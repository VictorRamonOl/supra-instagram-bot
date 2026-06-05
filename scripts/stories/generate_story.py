"""
generate_story.py - Renderiza Stories PNG (1080x1920) usando Playwright.
Le specs de content/_specs/stories.json e gera PNGs em content/stories_queue/.
"""
import argparse
import html as html_mod
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATE_FILE = Path(__file__).parent.parent / "templates" / "story_template.html"
QUEUE_DIR = PROJECT_ROOT / "content" / "stories_queue"
SPECS_FILE = PROJECT_ROOT / "content" / "_specs" / "stories.json"


def render_dica(s: dict) -> str:
    kicker = s.get("kicker", "Dica rápida")
    return f"""
    <div class="kicker">{html_mod.escape(kicker)}</div>
    <h1>{html_mod.escape(s.get('headline', ''))}</h1>
    <div class="body">{html_mod.escape(s.get('body', ''))}</div>
    """


def render_dado(s: dict) -> str:
    return f"""
    <div class="label">{html_mod.escape(s.get('label', 'Sabia disso?'))}</div>
    <div class="numero">{html_mod.escape(s.get('numero', ''))}</div>
    <div class="descricao">{html_mod.escape(s.get('descricao', ''))}</div>
    <div class="fonte">{html_mod.escape(s.get('fonte', ''))}</div>
    """


def render_quote(s: dict) -> str:
    return f"""
    <div class="marks">"</div>
    <div class="frase">{html_mod.escape(s.get('frase', ''))}</div>
    <div class="autor">— {html_mod.escape(s.get('autor', ''))}</div>
    """


def render_pergunta(s: dict) -> str:
    opcoes_html = "\n".join(
        f'<div class="opcao">{html_mod.escape(o)}</div>'
        for o in s.get("opcoes", [])
    )
    return f"""
    <div class="label">Pergunta do dia</div>
    <h1>{html_mod.escape(s.get('pergunta', ''))}</h1>
    <div class="opcoes">{opcoes_html}</div>
    <div class="responde">Responde no direct ou nos comentarios</div>
    """


RENDERERS = {
    "dica": render_dica,
    "dado": render_dado,
    "quote": render_quote,
    "pergunta": render_pergunta,
}


def build_html(spec: dict, template: str) -> str:
    stype = spec.get("type", "dica")
    renderer = RENDERERS.get(stype, render_dica)
    return (
        template
        .replace("{{TYPE}}", stype)
        .replace("{{CONTENT_HTML}}", renderer(spec))
    )


def render_to_png(html_string: str, out_png: Path, browser):
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
        f.write(html_string)
        temp_html = Path(f.name)
    try:
        page.goto(f"file:///{temp_html.as_posix()}", wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=str(out_png), full_page=False)
    finally:
        page.close()
        temp_html.unlink(missing_ok=True)


def find_next_pending() -> dict | None:
    """Retorna o proximo story do specs file que ainda nao foi publicado."""
    if not SPECS_FILE.exists():
        return None
    specs = json.loads(SPECS_FILE.read_text(encoding="utf-8"))

    # Marca quais ja foram publicados (controle por arquivo de state)
    published = set()
    state_file = PROJECT_ROOT / "state" / "published_stories.json"
    if state_file.exists():
        published = set(json.loads(state_file.read_text(encoding="utf-8")))

    for s in specs.get("stories", []):
        if s["id"] not in published:
            return s
    return None


def mark_published(story_id: str):
    state_file = PROJECT_ROOT / "state" / "published_stories.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    published = []
    if state_file.exists():
        published = json.loads(state_file.read_text(encoding="utf-8"))
    if story_id not in published:
        published.append(story_id)
    state_file.write_text(
        json.dumps(published, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main(spec_id: str | None = None):
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    if spec_id:
        all_specs = json.loads(SPECS_FILE.read_text(encoding="utf-8"))
        spec = next(
            (s for s in all_specs["stories"] if s["id"] == spec_id), None
        )
        if not spec:
            print(f"[erro] Story {spec_id} nao encontrado em specs.")
            sys.exit(1)
    else:
        spec = find_next_pending()
        if not spec:
            print("[info] Sem stories pendentes na fila.")
            sys.exit(2)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    folder_name = f"{timestamp}_{spec['id']}"
    out_dir = QUEUE_DIR / folder_name
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            html_str = build_html(spec, template)
            out_png = out_dir / "story.png"
            print(f"Gerando story {spec['id']}...")
            render_to_png(html_str, out_png, browser)
        finally:
            browser.close()

    # Meta do story (pra publisher usar)
    meta = {
        "id": spec["id"],
        "type": spec.get("type"),
        "spec": spec,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "story.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[ok] Story gerado em {out_dir}")
    return out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", help="ID do story especifico (senao pega o proximo)")
    args = parser.parse_args()
    main(args.id)
