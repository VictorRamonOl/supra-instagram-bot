# Setup GitHub Actions — Publicação 100% automática

Após esse setup, **nada precisa de intervenção** por 4 semanas. O GitHub publica sozinho 3x/semana e renova o token a cada 25 dias.

**Tempo total: ~5 minutos. Executa uma vez só.**

---

## 📋 Pré-requisitos verificados

✅ Git instalado (versão 2.53)
✅ GitHub CLI instalado (versão 2.93) em `C:\Program Files\GitHub CLI\gh.exe`
✅ Token Instagram long-lived válido até ~02/08/2026
✅ 12 posts aprovados em `content/approved/`
✅ Workflow `.github/workflows/publish.yml` pronto
✅ Conta GitHub: **VictorRamonOl**

---

## Passo 1 — Autenticar no GitHub CLI

Cola no PowerShell:

```powershell
cd "D:\Documents\0. Automações\Insta_Supra"
& "C:\Program Files\GitHub CLI\gh.exe" auth login
```

Responde nas perguntas:

| Pergunta | Resposta |
|----------|----------|
| Where do you use GitHub? | `GitHub.com` (Enter) |
| Preferred protocol | `HTTPS` (Enter) |
| Authenticate Git with your GitHub credentials? | `Y` + Enter |
| How would you like to authenticate? | `Login with a web browser` (Enter) |

Vai aparecer um **código de 8 dígitos** (ex: `ABCD-1234`).
1. Aperta Enter pra abrir o navegador
2. Cola o código
3. Autoriza tudo
4. Volta no terminal — deve aparecer `✓ Logged in as VictorRamonOl`

---

## Passo 2 — Criar repo + subir código + configurar segredos

**Cola TUDO de uma vez no PowerShell.** Esse bloco faz:
- Cria repositório privado `supra-instagram-bot`
- Sobe o código atual
- Configura os 3 segredos (token, ID, app_secret)

```powershell
cd "D:\Documents\0. Automações\Insta_Supra"
$env:Path += ";C:\Program Files\GitHub CLI"

# Cria repo privado e faz push
gh repo create supra-instagram-bot --private --source=. --remote=origin --push

# Le o token do .env local
$token = (Get-Content .env | Select-String "^INSTAGRAM_ACCESS_TOKEN=" | ForEach-Object { ($_ -split "=", 2)[1] }).Trim()

# Configura os 3 segredos no GitHub
gh secret set INSTAGRAM_USER_ID --body "17841437968295675"
gh secret set INSTAGRAM_APP_SECRET --body "781bfe34f29fa3c18a3a0a728c23de32"
gh secret set INSTAGRAM_ACCESS_TOKEN --body $token

Write-Host "`n>>> Repo criado e segredos configurados!" -ForegroundColor Green
Write-Host ">>> URL: https://github.com/VictorRamonOl/supra-instagram-bot" -ForegroundColor Cyan
```

---

## Passo 3 — Testar manualmente antes do agendamento

```powershell
gh workflow run publish.yml
```

Espera 30 segundos. Depois ve o status:

```powershell
gh run list --workflow=publish.yml --limit 1
```

Pra acompanhar em tempo real:

```powershell
gh run watch
```

**Se ficar verde ✅** → Já publicou o primeiro post (Mobiliário 5 erros) no @grupo.supraam. Confere o perfil. 🎉

**Se ficar vermelho ❌** → Cola o output do `gh run view` aqui no Claude que eu corrijo na hora.

---

## ⏰ Cronograma automático a partir de agora

Após o setup, os 12 posts saem nesta ordem **sem você precisar mexer em nada**:

| # | Data | Horário (BR) | Post |
|---|------|--------------|------|
| 01 | Qua 03/06 | 13h | Mobiliário 5 erros (catálogo) |
| 02 | Sex 05/06 | 18h | Logística interior AM (regional) |
| 03 | Seg 08/06 | 9h | PDDE Guia (técnico) |
| 04 | Qua 10/06 | 13h | Brinquedo 3 perguntas (catálogo) |
| 05 | Sex 12/06 | 18h | Censo escolar AM (regional) |
| 06 | Seg 15/06 | 9h | SRM Resolução FNDE (técnico) |
| 07 | Qua 17/06 | 13h | Lousa Projetor TV (catálogo) |
| 08 | Sex 19/06 | 18h | SRM subutilizada (regional) |
| 09 | Seg 22/06 | 9h | Educação Conectada (técnico) |
| 10 | Qua 24/06 | 13h | Compras públicas 2026 (catálogo) |
| 11 | Sex 26/06 | 18h | 5 perguntas fornecedor (regional) |
| 12 | Seg 29/06 | 9h | Cantinho Leitura 70/30 (técnico) |

---

## 🔁 Quando a fila esvaziar (depois de 29/06)

Você abre o Claude Code e diz:

> "Produz batch 002 com mais 12 posts seguindo o BRAND_PATTERN.md"

Eu produzo, você revisa (mesmo formato do batch 001), aprova, e o cron continua publicando.

---

## 🛡 Sobre segurança e privacidade

- Repo é **privado** (só você vê)
- Token guardado nos **GitHub Secrets** (criptografado, não visível em logs)
- Workflow nunca printa o token em texto puro
- O `.env` local fica **fora do repo** (protegido pelo `.gitignore`)

---

## ⚠ O que pode pedir intervenção (raro)

| Cenário | Quando | Solução |
|---------|--------|---------|
| Token expira (depois de 60 dias) | ~01/08/2026 | Auto-refresh é feito em todo publish. Se falhar, eu gero novo |
| Fila acaba | Depois de 29/06 | Me chama no Claude pra produzir batch 002 |
| Erro no GitHub Actions | Raro | Vai te mandar email automaticamente. Manda print do erro |

---

## 📚 Comandos úteis (guarda essa lista)

```powershell
# Adiciona o PATH (necessario em terminal novo)
$env:Path += ";C:\Program Files\GitHub CLI"

# Ver historico de execucoes do workflow
gh run list --workflow=publish.yml

# Disparar manualmente (fora do agendamento)
gh workflow run publish.yml

# Ver logs de uma execucao especifica
gh run view <ID>

# Pausar publicacoes (ex: feriado, recesso)
gh workflow disable publish.yml

# Voltar publicacoes
gh workflow enable publish.yml

# Atualizar token Instagram quando precisar
gh secret set INSTAGRAM_ACCESS_TOKEN --body "NOVO_TOKEN"
```

---

> **Última coisa:** depois do Passo 3 dar verde, você pode fechar o computador. O resto roda na nuvem.
