# ⚡ Guia Rápido - Astronomia Flipboard

## 📥 Instalação (2 minutos)

```bash
cd astronomia-flipboard
pip install feedparser requests agendador --break-system-packages
```

## 🧪 Testar (1 minuto)

```bash
python3 main.py
```

✓ Pronto! Gerou `feed_astronomia.xml` com artigos.

## ⏰ Agendar 1x ao dia (escolha uma)

### Linux/Mac (RECOMENDADO)
```bash
crontab -e
# Adicione esta linha:
0 8 * * * cd ~/astronomia-flipboard && python3 main.py >> agendador.log 2>&1
```

### Windows
1. Abra **Agendador de Tarefas**
2. **Criar Tarefa** → Diariamente às 08:00
3. Programa: `python.exe`
4. Argumentos: `main.py`
5. **Criar**

### Python (simples)
```bash
python3 agendador.py
```

## 📤 Hospedar Feed (GitHub - GRÁTIS)

### Passo 1: Fazer upload para GitHub

```bash
git init
git add .
git commit -m "Agente de astronomia"
git remote add origin https://github.com/seu-usuario/astronomia-flipboard.git
git push -u origin principal
```

### Passo 2: Feed URL

```
https://raw.githubusercontent.com/seu-usuario/astronomia-flipboard/principal/feed_astronomia.xml
```

## 📥 Importar Flipboard

1. Abra **Flipboard**
2. Clique **"+"** → **"Adicionar Feed RSS"**
3. Cole a URL acima
4. ✓ **Adicionar**

## 🎯 Pronto!

✅ Seu feed será atualizado **todos os dias às 08:00**

---

## 📚 Documentação completa

- `README.md` - Visão geral e fontes
- `INSTALL.md` - Setup detalhado
- `main.py` - Código fonte (totalmente em português)

## 🔧 Dúvidas?

**Feed não atualiza?**
- Verifique cron: `crontab -l`
- Ver logs: `tail -f agendador.log`

**Flipboard não importa?**
- Teste URL: `curl https://url-do-feed`
- Aguarde 1-2 horas para cache atualizar

**Mudar horário?**
- Edite crontab ou `agendador.py`

---

**Aproveite!** 🚀🌌
