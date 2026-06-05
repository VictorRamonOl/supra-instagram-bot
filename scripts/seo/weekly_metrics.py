"""
weekly_metrics.py — Gera relatório SEO semanal consolidado.

Toda domingo 20h BR, o cron roda este script. Ele:
  1. Consulta Search Console API (se GSC_CREDENTIALS_JSON estiver no env)
     - Top 10 queries que geraram impressoes/cliques na semana
     - URLs mais clicadas
     - Posição média
     - Comparacao com semana anterior
  2. Consulta Bing Webmaster API (fallback) se BING_API_KEY estiver no env
  3. Se nenhuma API configurada, gera template manual com instrucoes
  4. Escreve content/seo_report/YYYY-WW.md
  5. Commit no GitHub (user recebe notificacao)

User abre o arquivo no domingo, vê tendências e age na semana seguinte.

V1 (hoje): modo template com instrucoes pra pegar metricas manualmente.
V2 (quando configurar OAuth): pull automático via Search Console API.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORT_DIR = PROJECT_ROOT / "content" / "seo_report"

SITE = "supraam.com.br"
GSC_PROPERTY = f"https://{SITE}/"


def try_gsc_api() -> dict | None:
    """
    Tenta puxar dados do Google Search Console via API.
    Requer GSC_CREDENTIALS_JSON no env (service account JSON encoded).
    Retorna None se nao configurado/falhar.
    """
    creds_json = os.getenv("GSC_CREDENTIALS_JSON")
    if not creds_json:
        return None

    try:
        from google.oauth2 import service_account  # noqa
        from googleapiclient.discovery import build  # noqa
    except ImportError:
        print("[gsc] biblioteca google-api-python-client nao instalada; modo template.")
        return None

    try:
        creds_data = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_data,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        service = build("searchconsole", "v1", credentials=credentials)

        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=7)

        # Top queries
        queries_resp = service.searchanalytics().query(
            siteUrl=GSC_PROPERTY,
            body={
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["query"],
                "rowLimit": 10,
            },
        ).execute()

        # Top pages
        pages_resp = service.searchanalytics().query(
            siteUrl=GSC_PROPERTY,
            body={
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["page"],
                "rowLimit": 10,
            },
        ).execute()

        # Totais
        totals_resp = service.searchanalytics().query(
            siteUrl=GSC_PROPERTY,
            body={
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": [],
            },
        ).execute()

        return {
            "queries": queries_resp.get("rows", []),
            "pages": pages_resp.get("rows", []),
            "totals": totals_resp.get("rows", [{}])[0],
            "period": f"{start} → {end}",
        }
    except Exception as e:
        print(f"[gsc] erro chamando API: {e}")
        return None


def render_template_md(week_id: str, today: str, gsc_data: dict | None) -> str:
    """Renderiza o relatorio em markdown."""
    md = f"""# Relatório SEO — Semana {week_id}

> Gerado em **{today}** · Site: `{SITE}`

---

## 1. Resumo executivo

"""

    if gsc_data:
        totals = gsc_data["totals"]
        clicks = totals.get("clicks", 0)
        impressions = totals.get("impressions", 0)
        ctr = totals.get("ctr", 0) * 100 if totals.get("ctr") else 0
        position = totals.get("position", 0)
        md += f"""**Período**: {gsc_data['period']}

| Métrica | Valor |
|---------|-------|
| Impressões | {int(impressions):,} |
| Cliques | {int(clicks):,} |
| CTR | {ctr:.2f}% |
| Posição média | {position:.1f} |

---

## 2. Top 10 queries que geraram cliques

| # | Query | Cliques | Impressões | CTR | Posição |
|---|-------|---------|------------|-----|---------|
"""
        for i, row in enumerate(gsc_data["queries"], 1):
            q = row.get("keys", ["?"])[0]
            c = int(row.get("clicks", 0))
            imp = int(row.get("impressions", 0))
            ctr_val = row.get("ctr", 0) * 100 if row.get("ctr") else 0
            pos = row.get("position", 0)
            md += f"| {i} | `{q}` | {c} | {imp} | {ctr_val:.1f}% | {pos:.1f} |\n"

        md += "\n---\n\n## 3. Top 10 páginas mais clicadas\n\n"
        md += "| # | Página | Cliques | Impressões |\n|---|--------|---------|------------|\n"
        for i, row in enumerate(gsc_data["pages"], 1):
            page = row.get("keys", ["?"])[0].replace(f"https://{SITE}", "")
            c = int(row.get("clicks", 0))
            imp = int(row.get("impressions", 0))
            md += f"| {i} | `{page or '/'}` | {c} | {imp} |\n"
    else:
        md += """> ℹ️ **Modo template** — Search Console API ainda não foi configurada.
>
> Pra ativar pull automático:
> 1. Cria projeto no Google Cloud Console
> 2. Habilita Search Console API
> 3. Cria Service Account → baixa JSON
> 4. Adiciona email do Service Account como usuário do GSC (Configurações → Usuários)
> 5. `gh secret set GSC_CREDENTIALS_JSON --body "$(cat service-account.json)"`
> 6. Próximo domingo, o relatório vem com dados reais

### Enquanto isso — checklist manual de 5 minutos

| Tarefa | Onde | Tempo |
|--------|------|-------|
| Anota impressões/cliques da semana | GSC → Desempenho (últimos 7 dias) | 1 min |
| Anota top 5 queries | GSC → Desempenho → Consultas | 2 min |
| Anota top 5 URLs | GSC → Desempenho → Páginas | 1 min |
| Verifica novas URLs indexadas | GSC → Indexação → Páginas | 1 min |

---

## 2. Métricas pra preencher manualmente

### Tráfego total
- Impressões semana: ____
- Cliques semana: ____
- CTR médio: ____ %
- Posição média: ____

### Top queries (cole as 5 maiores)
1. `___________` → __ cliques
2. `___________` → __ cliques
3. `___________` → __ cliques
4. `___________` → __ cliques
5. `___________` → __ cliques

### Top URLs (cole as 5 maiores)
1. `___________` → __ cliques
2. `___________` → __ cliques
3. `___________` → __ cliques
4. `___________` → __ cliques
5. `___________` → __ cliques
"""

    md += """

---

## 4. Bing Webmaster — checar também

Acessa `bing.com/webmasters` → Desempenho da Pesquisa. Anota:
- Impressões semana: ____
- Cliques semana: ____
- Top 3 queries: ____, ____, ____

---

## 5. Google Business Profile — métricas do perfil

Acessa `business.google.com` → Desempenho. Anota:
- Visualizações do perfil: ____
- Cliques no site: ____
- Cliques em "Ligar": ____
- Cliques em "Direções": ____
- Mensagens recebidas: ____
- Reviews recebidas: ____

---

## 6. Sinais de ALERTA — agir nessa semana

Marca conforme aparecer:

- [ ] Queda > 30% em impressões vs semana anterior → checar pages com noindex acidental
- [ ] Nova query com 50+ impressões mas 0 cliques → reescrever title/description dessa página
- [ ] URL no top 10 sem botão "Solicitar orçamento" → adicionar CTA
- [ ] Página com posição > 20 mas alto volume de impressão → otimizar conteúdo (mais palavras, mais headings, mais links internos)
- [ ] Review negativa não respondida → responder em < 24h
- [ ] Mensagem GBP não respondida > 24h → responder agora

---

## 7. Ações pra próxima semana

Baseado nos dados acima:

### Conteúdo
- [ ] Escrever 1 post no blog focado na query top do GSC
- [ ] Postar 2x no GBP (ver `content/gbp_digest/{week}.md`)
- [ ] Pedir 2 reviews adicionais

### Técnico
- [ ] Verificar status indexação no GSC (10 URLs novas)
- [ ] Submeter URLs novas no IndexNow (auto via news monitor)
- [ ] Conferir Core Web Vitals do GSC (carregamento das páginas)

### Backlinks
- [ ] Comentar em 2 posts de blog de educação (com link discreto)
- [ ] Pedir 1 backlink em rede de parceiros

---

**Próximo relatório**: domingo que vem às 20h BR (automático).
"""
    return md


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    iso = datetime.now(timezone.utc).isocalendar()
    week_id = f"{iso.year}-W{iso.week:02d}"

    gsc_data = try_gsc_api()
    if gsc_data:
        print("[seo-metrics] Pull do GSC OK — usando dados reais.")
    else:
        print("[seo-metrics] GSC nao configurado — gerando template manual.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md = render_template_md(week_id, today, gsc_data)
    out = REPORT_DIR / f"{week_id}.md"
    out.write_text(md, encoding="utf-8")
    print(f"[seo-metrics] Gerado: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
