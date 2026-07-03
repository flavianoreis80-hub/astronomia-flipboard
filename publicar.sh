#!/bin/zsh
# Coleta as notícias e publica o feed no GitHub (rodado 1x ao dia pelo LaunchAgent)
cd "$(dirname "$0")" || exit 1

.venv/bin/python main.py || exit 1

# Só publica se o remote já estiver configurado
if git remote get-url origin >/dev/null 2>&1; then
    git add feed_astronomia.xml
    if ! git diff --cached --quiet; then
        git commit -m "Atualiza feed $(date '+%Y-%m-%d %H:%M')"
        git push origin main
    else
        echo "Feed sem mudanças, nada a publicar"
    fi
else
    echo "Remote 'origin' não configurado — feed gerado apenas localmente"
fi
