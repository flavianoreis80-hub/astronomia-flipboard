#!/bin/zsh
# Coleta as notícias e publica o feed no GitHub (rodado 1x ao dia pelo LaunchAgent)
cd "$(dirname "$0")" || exit 1
export PATH="/opt/homebrew/bin:$PATH"

.venv/bin/python main.py || exit 1

# Cria o repositório no GitHub na primeira execução após o login (gh auth login)
if ! git remote get-url origin >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
        gh repo create astronomia-flipboard --public --source=. --remote=origin --push \
            && echo "Repositório criado e feed publicado"
    else
        echo "Remote 'origin' não configurado e gh sem login — feed gerado apenas localmente"
        exit 0
    fi
fi

git add feed_astronomia.xml feeds
if ! git diff --cached --quiet; then
    git commit -m "Atualiza feed $(date '+%Y-%m-%d %H:%M')"
    git push origin main
else
    echo "Feed sem mudanças, nada a publicar"
fi
