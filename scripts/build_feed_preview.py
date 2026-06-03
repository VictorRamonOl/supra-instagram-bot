"""
build_feed_preview.py - Gera mockup do feed do Instagram com os covers dos 12 posts.

Mostra como o grid 3x4 vai aparecer pra quem visitar @grupo.supraam.
Posts mais novos no topo (ordem cronologica reversa, como o IG mostra).
"""
import html
import json
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PENDING_DIR = PROJECT_ROOT / "content" / "pending"
APPROVED_DIR = PROJECT_ROOT / "content" / "approved"
PREVIEW_FILE = PROJECT_ROOT / "content" / "_feed_preview.html"


def collect_posts():
    """Coleta covers de pending + approved, ordenados por scheduled_for desc."""
    posts = []
    for src_dir in (APPROVED_DIR, PENDING_DIR):
        if not src_dir.exists():
            continue
        for d in src_dir.iterdir():
            if d.is_dir():
                meta_file = d / "post.json"
                cover = d / "slide_01.png"
                if meta_file.exists() and cover.exists():
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    posts.append({
                        "id": meta["id"],
                        "slug": meta["slug"],
                        "pillar": meta["pillar"],
                        "scheduled_for": meta["scheduled_for"],
                        "format": meta["format"],
                        "slides_count": meta["slides_count"],
                        "cover_path": str(cover.relative_to(PREVIEW_FILE.parent)).replace("\\", "/"),
                        "source": src_dir.name,
                    })
    # IG mostra mais novo primeiro
    return sorted(posts, key=lambda p: p["scheduled_for"], reverse=True)


HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Feed Preview - @grupo.supraam</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, "Segoe UI", sans-serif; background: #fafafa; color: #262626; }

  .ig-header { background: white; border-bottom: 1px solid #dbdbdb; padding: 24px 0; }
  .ig-profile { max-width: 935px; margin: 0 auto; display: flex; gap: 60px; align-items: center; padding: 0 24px; }
  .ig-avatar { width: 150px; height: 150px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #14315a, #0d2645); display: flex; align-items: center; justify-content: center; font-family: 'Playfair Display', Georgia, serif; font-size: 56px; font-weight: 700; color: #d4af5a; border: 3px solid #d4af5a; }
  .ig-info h1 { font-size: 28px; font-weight: 300; margin-bottom: 4px; }
  .ig-info .sub { font-size: 14px; color: #737373; margin-bottom: 16px; }
  .ig-stats { display: flex; gap: 32px; font-size: 16px; margin-bottom: 16px; }
  .ig-stats span b { font-weight: 600; }
  .ig-bio { max-width: 500px; font-size: 14px; line-height: 1.4; }
  .ig-bio strong { font-weight: 600; }

  .feed-tabs { max-width: 935px; margin: 32px auto 0; border-top: 1px solid #dbdbdb; padding: 16px; text-align: center; font-size: 12px; letter-spacing: 1px; color: #737373; }
  .feed-tabs span { padding: 0 24px; }
  .feed-tabs .active { color: #262626; border-top: 2px solid #262626; padding-top: 16px; margin-top: -17px; font-weight: 600; }

  .feed { max-width: 935px; margin: 0 auto; padding: 28px 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; }
  .tile { aspect-ratio: 1; position: relative; overflow: hidden; cursor: pointer; background: #000; }
  .tile img { width: 100%; height: 100%; object-fit: cover; transition: transform .2s; }
  .tile:hover img { transform: scale(1.03); }
  .tile-badge { position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.6); color: white; font-size: 11px; padding: 4px 8px; border-radius: 4px; font-weight: 500; }
  .tile-carousel-icon { position: absolute; top: 8px; right: 8px; color: white; font-size: 18px; filter: drop-shadow(0 0 2px rgba(0,0,0,0.5)); }
  .tile-info { position: absolute; bottom: 0; left: 0; right: 0; padding: 6px 8px; background: linear-gradient(to top, rgba(0,0,0,0.7), transparent); color: white; font-size: 10px; }
  .tile.future { opacity: 0.85; }
  .tile.future::after { content: "AGENDADO"; position: absolute; top: 8px; left: 8px; background: #d4af5a; color: #0d2645; font-size: 10px; padding: 2px 6px; border-radius: 3px; font-weight: 700; }

  .legend { max-width: 935px; margin: 0 auto 40px; padding: 0 24px; }
  .legend h3 { font-size: 14px; font-weight: 600; margin-bottom: 8px; }
  .legend-items { display: flex; gap: 24px; font-size: 13px; color: #737373; }
  .legend-pill { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 6px; vertical-align: middle; }
  .pill-tecnico { background: #003d99; }
  .pill-catalogo { background: #b35900; }
  .pill-regional { background: #006600; }
</style>
</head>
<body>

<div class="ig-header">
  <div class="ig-profile">
    <div class="ig-avatar">SA</div>
    <div class="ig-info">
      <h1>grupo.supraam</h1>
      <div class="sub">Supra AM | Soluções Integradas</div>
      <div class="ig-stats">
        <span><b>%TOTAL%</b> posts</span>
        <span><b>16</b> seguidores</span>
        <span><b>0</b> seguindo</span>
      </div>
      <div class="ig-bio">
        <strong>Soluções educacionais para o Norte</strong><br>
        PDDE • FNDE • Mobiliário • Tecnologia • Inclusão<br>
        Atendemos AM, PA, RO, RR, AC, AP, TO<br>
        🌐 supraam.com.br
      </div>
    </div>
  </div>
</div>

<div class="feed-tabs">
  <span class="active">▦ POSTS</span>
  <span>⏵ REELS</span>
  <span>👤 MARCADAS</span>
</div>

<div class="feed">
%TILES%
</div>

<div class="legend">
  <h3>Legenda dos pilares:</h3>
  <div class="legend-items">
    <span><span class="legend-pill pill-tecnico"></span>Técnico-regulatório (Segunda)</span>
    <span><span class="legend-pill pill-catalogo"></span>Catálogo/produto (Quarta)</span>
    <span><span class="legend-pill pill-regional"></span>Mercado/regional (Sexta)</span>
  </div>
</div>

</body>
</html>
"""


def build_tile(post: dict) -> str:
    carousel_icon = '<div class="tile-carousel-icon">⊟</div>' if post["format"] == "carousel" else ""
    return f"""
    <div class="tile future" title="#{post['id']} — {post['slug']} — {post['scheduled_for']}">
      <img src="{post['cover_path']}" alt="{html.escape(post['slug'])}">
      {carousel_icon}
      <div class="tile-info">
        <span class="legend-pill pill-{post['pillar']}"></span>
        #{post['id']} · {post['scheduled_for']}
      </div>
    </div>
    """


def main():
    posts = collect_posts()
    tiles_html = "\n".join(build_tile(p) for p in posts)
    final = HTML.replace("%TILES%", tiles_html).replace("%TOTAL%", str(len(posts)))
    PREVIEW_FILE.write_text(final, encoding="utf-8")
    print(f"Feed preview gerado: {PREVIEW_FILE}")
    webbrowser.open(PREVIEW_FILE.as_uri())


if __name__ == "__main__":
    main()
