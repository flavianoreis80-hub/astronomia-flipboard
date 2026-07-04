#!/bin/zsh
# Rode este script no Terminal quando estiver no computador:
#   ~/Documents/Astro/login-github.sh
# Ele abre o login do GitHub no navegador; depois disso a publicação do feed
# passa a funcionar sozinha (o publicar.sh cria o repositório na próxima execução).
export PATH="/opt/homebrew/bin:$PATH"
gh auth login --hostname github.com --git-protocol https --web
echo ""
echo "Login concluído! Publicando o feed agora..."
"$(dirname "$0")/publicar.sh"
