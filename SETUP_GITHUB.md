# Setup GitHub Actions — versão simplificada (via gh CLI)

Tempo: ~5 min. Só faz uma vez.

---

## Passo 1 — Autenticar no GitHub

Cole no PowerShell:

```powershell
cd "D:\Documents\0. Automações\Insta_Supra"
& "C:\Program Files\GitHub CLI\gh.exe" auth login
```

Responda as perguntas no terminal:
- **Where do you use GitHub?** → `GitHub.com`
- **Preferred protocol** → `HTTPS`
- **Authenticate Git with your GitHub credentials?** → `Y`
- **How would you like to authenticate?** → `Login with a web browser`

Vai abrir o navegador, fazer login (cria conta se ainda não tem), confirmar o código de 8 dígitos que aparece no terminal, e pronto.

---

## Passo 2 — Criar repo, subir código e configurar segredos (1 comando só)

Cola tudo de uma vez no PowerShell:

```powershell
cd "D:\Documents\0. Automações\Insta_Supra"
$env:Path += ";C:\Program Files\GitHub CLI"

# Cria repo privado e sobe o codigo
gh repo create supra-instagram-bot --private --source=. --remote=origin --push

# Configura os 3 segredos
gh secret set INSTAGRAM_USER_ID --body "17841437968295675"
gh secret set INSTAGRAM_APP_SECRET --body "781bfe34f29fa3c18a3a0a728c23de32"
gh secret set INSTAGRAM_ACCESS_TOKEN --body (Get-Content .env | Select-String "INSTAGRAM_ACCESS_TOKEN=" | ForEach-Object { ($_ -split "=", 2)[1] })

Write-Host "`n>>> Pronto. Repo + segredos configurados." -ForegroundColor Green
```

---

## Passo 3 — Testar o workflow manualmente

```powershell
gh workflow run publish.yml
```

Espera ~30 segundos e ve o status:

```powershell
gh run list --workflow=publish.yml --limit 1
```

Pra ver detalhes da execução em andamento:

```powershell
gh run watch
```

Se ficar verde ✅ → publicou no @grupo.supraam. Confere o perfil.
Se ficar vermelho ❌ → me manda o output que eu ajusto.

---

## Próximos posts

A partir daqui, sem precisar fazer nada:

| Dia | Horário | Post |
|-----|---------|------|
| Quarta 03/06 | 13h BR | 01 Mobiliário 5 erros |
| Sexta 05/06 | 18h BR | 02 Logística interior AM |
| Segunda 08/06 | 9h BR | 03 PDDE Guia |
| ... | ... | (e por aí vai os 12) |

Quando a fila esvaziar (após 4 semanas), você me chama no Claude Code que eu produzo o próximo batch.

---

## Comandos úteis

```powershell
# Ver historico de execucoes
gh run list --workflow=publish.yml

# Disparar manualmente fora do agendamento
gh workflow run publish.yml

# Ver logs de uma execucao especifica
gh run view <ID>

# Cancelar workflow agendado por uma semana (ex: feriado)
gh workflow disable publish.yml
gh workflow enable publish.yml
```
