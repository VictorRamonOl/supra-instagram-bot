"""
build_review.py - Gera HTML unico mostrando todos os posts em /pending/ pra revisao em lote.

Uso:
  python build_review.py
  python build_review.py --open    (abre automaticamente no navegador)
"""
import argparse
import html
import json
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PENDING_DIR = PROJECT_ROOT / "content" / "pending"
REVIEW_FILE = PROJECT_ROOT / "content" / "_review_pending.html"


HTML_HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Revisao em Lote - Posts Pendentes</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', -apple-system, sans-serif; background: #f5f5f7; color: #1c1c1e; padding: 32px; }
  .header { max-width: 1400px; margin: 0 auto 32px; }
  .header h1 { font-size: 28px; margin-bottom: 8px; }
  .header p { color: #6e6e73; font-size: 14px; }
  .instructions { background: #fffbe6; border: 1px solid #ffd666; padding: 16px 24px; border-radius: 8px; margin: 24px 0; max-width: 1400px; margin-left: auto; margin-right: auto; }
  .instructions code { background: #1c1c1e; color: #fff; padding: 2px 8px; border-radius: 4px; font-family: 'SF Mono', Monaco, monospace; font-size: 13px; }
  .post { background: white; border-radius: 12px; padding: 28px; margin: 0 auto 24px; max-width: 1400px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .post-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 16px; border-bottom: 1px solid #e5e5e7; margin-bottom: 24px; }
  .post-meta { display: flex; align-items: center; gap: 16px; }
  .post-id { font-size: 24px; font-weight: 700; color: #0d2645; }
  .post-slug { font-size: 16px; color: #1c1c1e; font-weight: 500; }
  .post-tags { display: flex; gap: 8px; }
  .tag { background: #e5e5e7; padding: 4px 10px; border-radius: 6px; font-size: 12px; color: #424247; font-weight: 500; }
  .tag.pillar-tecnico { background: #e6f0ff; color: #003d99; }
  .tag.pillar-catalogo { background: #fff4e6; color: #b35900; }
  .tag.pillar-regional { background: #e6ffe6; color: #006600; }
  .post-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
  .slides-wrap { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .slides-wrap img { width: 100%; border-radius: 6px; cursor: pointer; transition: transform 0.15s; border: 1px solid #e5e5e7; }
  .slides-wrap img:hover { transform: scale(1.02); }
  .caption { background: #f5f5f7; padding: 20px; border-radius: 8px; white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #1c1c1e; font-family: 'SF Mono', Monaco, monospace; max-height: 460px; overflow-y: auto; }
  .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 1000; align-items: center; justify-content: center; cursor: zoom-out; }
  .modal.open { display: flex; }
  .modal img { max-width: 90vw; max-height: 90vh; border-radius: 8px; }
  .actions { display: flex; gap: 8px; }
  .btn { padding: 8px 16px; border-radius: 6px; border: 1px solid #d2d2d7; background: white; color: #1c1c1e; font-size: 13px; cursor: pointer; font-weight: 500; }
  .btn:hover { background: #f5f5f7; }
  .btn.approve { background: #34c759; color: white; border-color: #34c759; }
  .btn.reject { background: #ff3b30; color: white; border-color: #ff3b30; }
  .post.approved { background: #f0fff4; }
  .post.rejected { background: #fff5f5; opacity: 0.6; }
  .summary { position: fixed; bottom: 24px; right: 24px; background: #1c1c1e; color: white; padding: 16px 24px; border-radius: 12px; font-size: 14px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); z-index: 100; min-width: 280px; }
  .summary .cmd { background: #2c2c2e; padding: 8px 12px; border-radius: 6px; margin-top: 8px; font-family: 'SF Mono', Monaco, monospace; font-size: 12px; word-break: break-all; }
  .summary .cmd-row { display: flex; gap: 8px; margin-top: 6px; }
  .summary button { background: #34c759; color: white; border: 0; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; }
</style>
</head>
<body>
<div class="modal" onclick="this.classList.remove('open')"><img id="modalImg"></div>

<div class="header">
  <h1>Revisao em Lote - %COUNT% posts pendentes</h1>
  <p>Veja cada post, marque o que aprova (✓) ou rejeita (✗). Quando terminar, copie o comando no canto e cole no terminal.</p>
</div>

<div class="instructions">
  <strong>Como funciona:</strong> Voce clica em <code>Aprovar</code> ou <code>Rejeitar</code> em cada post. No fim, o painel embaixo a direita te da o comando exato pra rodar no PowerShell. <br>
  Posts aprovados sao movidos pra <code>content/approved/</code> e o agendador publica conforme cronograma. Posts rejeitados sao deletados.
</div>
"""

HTML_FOOT = """
<div class="summary" id="summary">
  <div><strong>Resumo:</strong> <span id="counts">0 aprovados, 0 rejeitados, %COUNT% pendentes</span></div>
  <div class="cmd" id="cmd-approve">python scripts/approve_batch.py --ids</div>
  <div class="cmd" id="cmd-reject">python scripts/approve_batch.py --reject</div>
  <div class="cmd-row">
    <button onclick="copyCmd('cmd-approve')">Copiar aprovar</button>
    <button onclick="copyCmd('cmd-reject')" style="background:#ff3b30">Copiar rejeitar</button>
  </div>
</div>

<script>
const state = {};
function setStatus(postId, status) {
  state[postId] = status;
  document.querySelectorAll('.post').forEach(el => {
    if (el.dataset.id === postId) {
      el.classList.remove('approved', 'rejected');
      if (status === 'approved') el.classList.add('approved');
      if (status === 'rejected') el.classList.add('rejected');
    }
  });
  updateSummary();
}
function updateSummary() {
  const approved = Object.entries(state).filter(([,v]) => v === 'approved').map(([k]) => k).sort();
  const rejected = Object.entries(state).filter(([,v]) => v === 'rejected').map(([k]) => k).sort();
  const total = document.querySelectorAll('.post').length;
  document.getElementById('counts').textContent =
    `${approved.length} aprovados, ${rejected.length} rejeitados, ${total - approved.length - rejected.length} pendentes`;
  document.getElementById('cmd-approve').textContent =
    `python scripts/approve_batch.py --ids ${approved.join(',') || '<nenhum>'}`;
  document.getElementById('cmd-reject').textContent =
    `python scripts/approve_batch.py --reject ${rejected.join(',') || '<nenhum>'}`;
}
function openImg(src) {
  document.getElementById('modalImg').src = src;
  document.querySelector('.modal').classList.add('open');
}
function copyCmd(id) {
  navigator.clipboard.writeText(document.getElementById(id).textContent);
  alert('Comando copiado!');
}
</script>
</body>
</html>
"""


def build_post_html(post_dir: Path) -> str:
    meta = json.loads((post_dir / "post.json").read_text(encoding="utf-8"))
    slides = sorted([f for f in post_dir.glob("slide_*.png")])
    if not slides:
        return ""

    slides_html = "\n".join(
        f'<img src="{html.escape(str(s.relative_to(REVIEW_FILE.parent)).replace(chr(92), "/"))}" '
        f'onclick="openImg(this.src)" alt="slide {i+1}">'
        for i, s in enumerate(slides)
    )

    return f"""
    <div class="post" data-id="{meta['id']}">
      <div class="post-header">
        <div class="post-meta">
          <div class="post-id">#{meta['id']}</div>
          <div class="post-slug">{html.escape(meta['slug'])}</div>
          <div class="post-tags">
            <span class="tag pillar-{meta['pillar']}">{meta['pillar']}</span>
            <span class="tag">{meta['format']}</span>
            <span class="tag">{meta['scheduled_for']}</span>
            <span class="tag">{meta['slides_count']} slides</span>
          </div>
        </div>
        <div class="actions">
          <button class="btn approve" onclick="setStatus('{meta['id']}', 'approved')">✓ Aprovar</button>
          <button class="btn reject" onclick="setStatus('{meta['id']}', 'rejected')">✗ Rejeitar</button>
        </div>
      </div>
      <div class="post-grid">
        <div>
          <div class="slides-wrap">{slides_html}</div>
        </div>
        <div>
          <div class="caption">{html.escape(meta['caption'])}</div>
        </div>
      </div>
    </div>
    """


def main(auto_open: bool):
    posts = sorted(d for d in PENDING_DIR.iterdir() if d.is_dir() and (d / "post.json").exists())
    if not posts:
        print("Sem posts em content/pending/.")
        return

    posts_html = "\n".join(build_post_html(p) for p in posts)
    count = str(len(posts))
    final_html = (HTML_HEAD.replace("%COUNT%", count)
                  + posts_html
                  + HTML_FOOT.replace("%COUNT%", count))
    REVIEW_FILE.write_text(final_html, encoding="utf-8")
    print(f"Revisao gerada: {REVIEW_FILE}")
    print(f"Total de posts: {count}")

    if auto_open:
        webbrowser.open(REVIEW_FILE.as_uri())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--open", action="store_true", help="Abrir no navegador")
    args = parser.parse_args()
    main(args.open)
