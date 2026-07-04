#!/usr/bin/env python3
"""
Agente de Astronomia - Flipboard
Coleta notícias de astronomia via APIs e gera RSS diário
Executa 1x ao dia via agendador ou cron
"""

import os
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Diretórios
DIRETORIO_BASE = Path(__file__).parent
SAIDA_RSS = DIRETORIO_BASE / "feed_astronomia.xml"

# Vault Obsidian: nota diária de notícias (defina OBSIDIAN_VAULT para usar outro vault)
VAULT_OBSIDIAN = Path(os.environ.get(
    "OBSIDIAN_VAULT",
    "/Users/flaviano/Library/Mobile Documents/iCloud~md~obsidian/Documents/Astronomia"
))
PASTA_NOTICIAS = VAULT_OBSIDIAN / "07 Notícias"

# Homepage de cada fonte (atributo url exigido pelo elemento <source> do RSS 2.0)
URLS_FONTES = {
    "NASA APOD": "https://apod.nasa.gov",
    "Space.com": "https://www.space.com",
    "ESO": "https://www.eso.org/public/news/",
    "CCVAlg": "https://www.ccvalg.pt/astronomia/",
    "arXiv": "https://arxiv.org",
    "NASA": "https://www.nasa.gov",
}


def data_rfc822(dt=None):
    """Formata uma data no padrão RFC-822 exigido pelo RSS (ex.: Fri, 03 Jul 2026 08:00:00 +0000)"""
    if dt is None:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def data_entrada_feed(entrada):
    """Extrai a data de uma entrada do feedparser em RFC-822 (fallback: agora)"""
    analisada = entrada.get("published_parsed") or entrada.get("updated_parsed")
    if analisada:
        return data_rfc822(datetime(*analisada[:6], tzinfo=timezone.utc))
    return data_rfc822()


class ColetorAstronomia:
    def __init__(self):
        self.artigos = []
        self.momento = datetime.now(timezone.utc)

    def buscar_nasa_apod(self):
        """Busca Imagem Astronômica do Dia (APOD) da NASA"""
        try:
            url = "https://api.nasa.gov/planetary/apod"
            parametros = {
                # Últimos 3 dias (count=N retornaria imagens ALEATÓRIAS do arquivo, não as recentes)
                "start_date": (self.momento - timedelta(days=2)).strftime("%Y-%m-%d"),
                # DEMO_KEY tem limite de 50 requisições/dia; defina NASA_API_KEY para usar chave própria
                "api_key": os.environ.get("NASA_API_KEY", "DEMO_KEY")
            }
            resposta = requests.get(url, params=parametros, timeout=5)
            if resposta.status_code == 200:
                for item in resposta.json():
                    try:
                        data = data_rfc822(datetime.strptime(item.get("date", ""), "%Y-%m-%d"))
                    except ValueError:
                        data = data_rfc822()
                    self.artigos.append({
                        "titulo": item.get("title", "NASA APOD"),
                        "descricao": item.get("explanation", "")[:300],
                        "link": item.get("url", "https://apod.nasa.gov"),
                        "fonte": "NASA APOD",
                        "data": data
                    })
                print("✓ NASA APOD coletado")
        except Exception as e:
            print(f"✗ Erro ao buscar NASA APOD: {e}")

    def buscar_space_com(self):
        """Busca notícias do Space.com via RSS"""
        try:
            url = "https://www.space.com/feeds.xml"
            feed = feedparser.parse(url)
            # Últimas 5 notícias
            if feed.entries:
                for entrada in feed.entries[:5]:
                    resumo = entrada.get("summary", "") or entrada.get("description", "")
                    self.artigos.append({
                        "titulo": entrada.get("title", "Notícia de Espaço"),
                        "descricao": resumo[:300] if resumo else "Notícia de espaço",
                        "link": entrada.get("link", "https://space.com"),
                        "fonte": "Space.com",
                        "data": data_entrada_feed(entrada)
                    })
                print(f"✓ Space.com coletado ({len(feed.entries)} artigos)")
            else:
                print("✗ Space.com: nenhum artigo encontrado")
        except Exception as e:
            print(f"✗ Erro ao buscar Space.com: {e}")

    def buscar_eso(self):
        """Busca notícias do ESO (Observatório Europeu Austral) via RSS"""
        try:
            url = "https://www.eso.org/public/news/feed/"
            feed = feedparser.parse(url)
            if feed.entries:
                for entrada in feed.entries[:3]:
                    resumo = entrada.get("summary", "") or entrada.get("description", "")
                    self.artigos.append({
                        "titulo": entrada.get("title", "Notícia do ESO"),
                        "descricao": resumo[:300] if resumo else "Descoberta do Observatório Europeu Austral",
                        "link": entrada.get("link", "https://www.eso.org/public/news/"),
                        "fonte": "ESO",
                        "data": data_entrada_feed(entrada)
                    })
                print(f"✓ ESO coletado ({len(feed.entries)} artigos)")
            else:
                print("✗ ESO: nenhum artigo encontrado")
        except Exception as e:
            print(f"✗ Erro ao buscar ESO: {e}")

    def buscar_ccvalg(self):
        """Busca notícias de astronomia em português do CCVAlg (Centro Ciência Viva do Algarve)"""
        try:
            url = "http://feeds.feedburner.com/astropt_ccvalg"
            feed = feedparser.parse(url)
            if feed.entries:
                for entrada in feed.entries[:5]:
                    resumo = entrada.get("summary", "") or entrada.get("description", "")
                    self.artigos.append({
                        "titulo": entrada.get("title", "Notícia de Astronomia"),
                        "descricao": resumo[:300] if resumo else "Notícia de astronomia em português",
                        "link": entrada.get("link", "https://www.ccvalg.pt/astronomia/"),
                        "fonte": "CCVAlg",
                        "data": data_entrada_feed(entrada)
                    })
                print(f"✓ CCVAlg coletado ({len(feed.entries)} artigos)")
            else:
                print("✗ CCVAlg: nenhum artigo encontrado")
        except Exception as e:
            print(f"✗ Erro ao buscar CCVAlg: {e}")

    def buscar_arxiv_astronomia(self):
        """Busca artigos científicos de astronomia do arXiv"""
        try:
            url = "http://export.arxiv.org/api/query"
            parametros = {
                "search_query": "cat:astro-ph.GA",  # Astrofísica - Galáxias
                "start": 0,
                "max_results": 3,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            resposta = requests.get(url, params=parametros, timeout=5)
            if resposta.status_code == 200:
                raiz = ET.fromstring(resposta.content)
                # Analisar XML do arXiv
                ns = "{http://www.w3.org/2005/Atom}"
                for entrada in raiz.findall(f"{ns}entry")[:3]:
                    elem_titulo = entrada.find(f"{ns}title")
                    elem_resumo = entrada.find(f"{ns}summary")
                    elem_id = entrada.find(f"{ns}id")
                    elem_data = entrada.find(f"{ns}published")

                    data = data_rfc822()
                    if elem_data is not None and elem_data.text:
                        try:
                            data = data_rfc822(datetime.fromisoformat(elem_data.text.replace("Z", "+00:00")))
                        except ValueError:
                            pass

                    if elem_titulo is not None:
                        self.artigos.append({
                            "titulo": elem_titulo.text.strip() if elem_titulo.text else "Artigo arXiv",
                            "descricao": (elem_resumo.text.strip() if elem_resumo.text else "")[:300],
                            "link": elem_id.text if elem_id is not None else "https://arxiv.org",
                            "fonte": "arXiv",
                            "data": data
                        })
                print("✓ arXiv coletado")
        except Exception as e:
            print(f"✗ Erro ao buscar arXiv: {e}")

    def gerar_rss(self):
        """Gera arquivo RSS com os artigos coletados"""
        rss = ET.Element("rss")
        rss.set("version", "2.0")

        canal = ET.SubElement(rss, "channel")

        # Metadados do canal
        ET.SubElement(canal, "title").text = "Astronomia Diária"
        ET.SubElement(canal, "link").text = "https://flipboard.com"
        ET.SubElement(canal, "description").text = "Notícias e descobertas de astronomia atualizadas diariamente"
        ET.SubElement(canal, "language").text = "pt-br"
        ET.SubElement(canal, "lastBuildDate").text = data_rfc822(self.momento)

        # Adicionar artigos
        for artigo in self.artigos:
            item = ET.SubElement(canal, "item")
            ET.SubElement(item, "title").text = artigo["titulo"]
            ET.SubElement(item, "description").text = artigo["descricao"]
            ET.SubElement(item, "link").text = artigo["link"]
            guid = ET.SubElement(item, "guid")
            guid.set("isPermaLink", "false")
            guid.text = artigo["link"]
            fonte = ET.SubElement(item, "source")
            fonte.set("url", URLS_FONTES.get(artigo["fonte"], "https://flipboard.com"))
            fonte.text = artigo["fonte"]
            ET.SubElement(item, "pubDate").text = artigo["data"]

        # Formatar com indentação
        texto_xml = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
        # Remover linhas vazias
        texto_xml = "\n".join([linha for linha in texto_xml.split("\n") if linha.strip()])

        with open(SAIDA_RSS, "w", encoding="utf-8") as f:
            f.write(texto_xml)

        print(f"\n✓ RSS gerado: {SAIDA_RSS}")
        print(f"  {len(self.artigos)} artigos inclusos")

    def gerar_nota_obsidian(self):
        """Gera a nota diária de notícias no vault Obsidian (sobrescreve a do mesmo dia)"""
        if not VAULT_OBSIDIAN.exists():
            print("✗ Vault Obsidian não encontrado, nota não gerada")
            return
        try:
            PASTA_NOTICIAS.mkdir(exist_ok=True)
            hoje = self.momento.strftime("%Y-%m-%d")
            nota = PASTA_NOTICIAS / f"{hoje} — Notícias de astronomia.md"

            linhas = [
                "---",
                "tags: [noticias]",
                f"data: {hoje}",
                "---",
                "",
                "# 📰 Notícias de astronomia",
                "",
            ]
            for fonte in dict.fromkeys(a["fonte"] for a in self.artigos):
                linhas.append(f"## {fonte}")
                linhas.append("")
                for artigo in self.artigos:
                    if artigo["fonte"] != fonte:
                        continue
                    linhas.append(f"### [{artigo['titulo']}]({artigo['link']})")
                    if artigo["descricao"]:
                        linhas.append(artigo["descricao"])
                    linhas.append("")

            linhas.append("*Gerado automaticamente pelo agente de astronomia*")
            nota.write_text("\n".join(linhas) + "\n", encoding="utf-8")
            print(f"✓ Nota Obsidian gerada: {nota.name}")
        except Exception as e:
            print(f"✗ Erro ao gerar nota Obsidian: {e}")

    def adicionar_artigos_demo(self):
        """Adiciona artigos de demonstração (fallback se APIs falham)"""
        demo = [
            {
                "titulo": "Descoberta de Exoplaneta Potencialmente Habitável",
                "descricao": "Astrônomos descobrem um novo exoplaneta na zona habitável de uma estrela próxima, com possibilidade de existência de água líquida e condições para vida.",
                "link": "https://space.com",
                "fonte": "Space.com",
                "data": data_rfc822(self.momento)
            },
            {
                "titulo": "Telescópio James Webb Revela Galáxia Distante",
                "descricao": "O JWST captura imagens de uma galáxia formada há apenas 300 milhões de anos após o Big Bang, fornecendo insights sobre os primeiros universos.",
                "link": "https://nasa.gov",
                "fonte": "NASA",
                "data": data_rfc822(self.momento)
            },
            {
                "titulo": "Anomalia em Órbita de Mercúrio Confirma Relatividade de Einstein",
                "descricao": "Novas medições confirmam a precessão da órbita de Mercúrio, validando as previsões da Teoria da Relatividade Geral de Einstein.",
                "link": "https://arxiv.org",
                "fonte": "arXiv",
                "data": data_rfc822(self.momento)
            }
        ]

        self.artigos.extend(demo)
        print(f"✓ {len(demo)} artigos de demonstração adicionados")

    def executar(self):
        """Executa coleta completa"""
        print(f"\n🌌 Coletando astronomia... ({self.momento.strftime('%d/%m/%Y %H:%M:%S')})\n")

        self.buscar_nasa_apod()
        self.buscar_space_com()
        self.buscar_eso()
        self.buscar_ccvalg()
        self.buscar_arxiv_astronomia()

        # Se nenhum artigo foi coletado, usar demonstração
        if not self.artigos:
            print("\n⚠️  Nenhum artigo coletado das APIs, usando demonstração...")
            self.adicionar_artigos_demo()

        self.gerar_rss()
        self.gerar_nota_obsidian()

        print(f"\n✓ Processo concluído!\n")


def main():
    coletor = ColetorAstronomia()
    coletor.executar()


if __name__ == "__main__":
    main()
