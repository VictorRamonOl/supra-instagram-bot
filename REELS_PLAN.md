# Plano de Reels Automatizados — @grupo.supraam
> Documento de design técnico + estratégia. A implementar nas próximas iterações.

---

## Por que Reels é prioridade #1

Em junho/2026 no Instagram:
- **Reach orgânico de Reel é 5-10x maior que carrossel** (algoritmo prioriza)
- Conta nova (sub-1k seguidores) ganha mais reach de Reel ainda
- Explore Tab é dominado por Reels
- Formato curto (15-30s) tem 70%+ completion rate quando bom

Pra um perfil B2B/B2G como o nosso, Reels é **a única alavanca orgânica que pode levar a 20k em <12 meses sem ads**.

---

## Estratégia de Reels — formatos que performam em B2B Educação

### 1. "Você sabia?" / Mito vs Verdade (15-20s)
**Hook**: "Você sabia que TODA escola pode receber PDDE Equidade?"
**Desenvolvimento**: 2-3 frames com regra ou esclarecimento
**CTA**: "Salva esse e marca um diretor"

### 2. Prazos críticos (10-15s)
**Hook**: "ATENÇÃO: prazo PDDE acaba em 7 dias"
**Desenvolvimento**: data exata + 3 passos
**CTA**: "Salva pra não esquecer"

### 3. Erros comuns (20-30s)
**Hook**: "5 erros que invalidam sua prestação de contas PDDE"
**Desenvolvimento**: 5 erros em sequência com X em vermelho
**CTA**: "Salva esse antes de comprar"

### 4. Comparativos visuais (15-20s)
**Hook**: "Lousa digital ou TV interativa? Veja a diferença"
**Desenvolvimento**: split-screen ou colunas
**CTA**: "Qual sua escola tem? Comenta"

### 5. Bastidores do FNDE/MEC (10-15s)
**Hook**: "FNDE acaba de liberar R$ 4,8 BI"
**Desenvolvimento**: dado-bomba com tipografia grande
**CTA**: "Saiba mais no blog"

---

## Arquitetura técnica (a construir)

### Stack
- **Renderização**: Playwright (já temos) — gera frames PNG
- **Animação**: keyframes via CSS animation
- **Vídeo**: ffmpeg pra combinar frames + áudio
- **Áudio**: biblioteca livre IG (selecionado manualmente) ou músicas free no Pixabay
- **Upload**: Meta Graph API endpoint `/media` com `media_type=REELS`

### Pipeline
```
1. specs/reels_001.json    ← spec do Reel (hook, frames, duração, audio)
2. generate_reel.py        ← Playwright captura sequência de frames
3. compose_reel.py         ← ffmpeg junta frames + audio → MP4 vertical 1080x1920
4. publish_reel.py         ← Meta API upload com media_type=REELS
```

### Template HTML do Reel
Diferente do carrossel (1080x1080), o Reel é **1080x1920** (9:16).
Cada frame tem 2-4s de duração. Texto grande, contraste forte.

```html
<body style="width:1080px; height:1920px; background: navy gradient;">
  <div class="hook" style="font-size:120px; text-align:center;">
    Você sabia?
  </div>
  <div class="punchline" style="font-size:90px;">
    Que TODA escola pode receber PDDE Equidade?
  </div>
</body>
```

### Audio strategy
- **Trending audio** do IG (manual — pegar o áudio do momento e usar)
- **Sound effects** sutis (whoosh, click) entre frames
- **Música institucional** (livre) pra Reels mais "anúncio"

Pra v1, sem audio (vídeo silencioso) já roda. Adicionar audio depois.

---

## Cadência sugerida (3x/semana de Reels)

| Dia | Tipo de Reel | Duração | Conteúdo |
|-----|-------------|---------|----------|
| Ter | Atualidade FNDE | 10-15s | "FNDE acaba de..." |
| Qui | Dica técnica | 20-30s | Mito/verdade ou checklist |
| Sáb | Polêmica/Pergunta | 15-20s | "Você compra X de jeito Y? Faz errado!" |

Combinado com carrossel Seg/Qua/Sex:
- Seg 9h: carrossel
- Ter 12h: Reel
- Qua 13h: carrossel
- Qui 12h: Reel
- Sex 18h: carrossel
- Sáb 11h: Reel
- Dom: descanso

**= 6 posts/semana** (3 Reels + 3 carrosseis). Sweet spot pra B2B em crescimento.

---

## Próximos passos pra implementar

- [ ] Criar template HTML vertical 1080x1920 com animações CSS
- [ ] Adaptar generate_slides.py pra modo "reel" (gerar 30 frames/sec)
- [ ] Adicionar ffmpeg ao requirements + install no GitHub Actions
- [ ] Endpoint Meta API: `POST /{ig-user-id}/media` com `media_type=REELS` e `video_url`
- [ ] Upload do MP4 pra raw.githubusercontent.com (já temos repo público)
- [ ] Cron separado: `reels.yml` Ter/Qui/Sáb

---

## Estimativa de impacto

**Sem Reels** (estratégia atual):
- 17 → 200 seguidores em 90 dias (organico carrossel apenas)

**Com Reels** (essa proposta):
- 17 → 1.500-3.000 seguidores em 90 dias
- 1 viral Reel (acontece) → +500-2k em poucos dias

Reels é a aposta. Carrossel sozinho não escala.
