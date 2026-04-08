#!/usr/bin/env python3
"""
VCtv AInews — Gerador automático de notícias
Rodado pelo GitHub Actions diariamente.
"""

import json
import os
import sys
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# ─── CONFIG ───────────────────────────────────────────────────────────────────

RSS_FEEDS = [
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml",               "source": "BBC World",     "category": "Mundo"},
    {"url": "https://feeds.bbci.co.uk/news/technology/rss.xml",          "source": "BBC Tech",      "category": "Tecnologia"},
    {"url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "source": "BBC Ciência", "category": "Ciência"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",    "source": "NY Times",      "category": "Mundo"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml","source": "NY Times Tech","category": "Tecnologia"},
    {"url": "https://g1.globo.com/rss/g1/rss.xml",                       "source": "G1",            "category": "Brasil"},
    {"url": "https://g1.globo.com/rss/g1/economia/rss.xml",              "source": "G1 Economia",   "category": "Economia"},
]

POLLINATIONS_URL = "https://text.pollinations.ai/"

# ─── SPECIAL EVENTS CALENDAR ──────────────────────────────────────────────────
# Formato: "MM-DD": "Nome do evento"
SPECIAL_EVENTS = {
    "01-01": "Ano Novo",
    "02-14": "Dia dos Namorados",
    "04-21": "Tiradentes",
    "05-01": "Dia do Trabalho",
    "07-04": "Independência dos EUA",
    "09-07": "Independência do Brasil",
    "10-31": "Halloween",
    "11-15": "Proclamação da República",
    "12-25": "Natal",
    "12-31": "Véspera de Ano Novo",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fetch_url(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VCtv-AInews/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠ Erro ao buscar {url}: {e}")
        return None


def parse_rss(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"media": "http://search.yahoo.com/mrss/"}
        channel = root.find("channel")
        if channel is None:
            return items
        for item in channel.findall("item")[:8]:
            title = (item.findtext("title") or "").strip()
            desc  = (item.findtext("description") or "").strip()
            link  = (item.findtext("link") or "").strip()
            pub   = (item.findtext("pubDate") or datetime.datetime.utcnow().isoformat())
            # Remove HTML tags
            import re
            desc = re.sub(r"<[^>]+>", "", desc)
            if title:
                items.append({"title": title, "summary": desc[:400], "link": link, "pub": pub})
    except Exception as e:
        print(f"  ⚠ Erro ao parsear RSS: {e}")
    return items


def pollinations_generate(prompt, model="openai"):
    payload = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "seed": 42,
    }).encode()
    try:
        req = urllib.request.Request(
            POLLINATIONS_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠ Pollinations error: {e}")
        return None


def enhance_article(raw_item, source, category, edition_type):
    """Use Pollinations to expand the raw RSS summary into a full article."""
    detail = "Seja conciso (3-4 parágrafos)." if edition_type == "daily" else \
             "Seja detalhado (5-7 parágrafos) com contexto e análise." if edition_type == "weekend" else \
             "Escreva uma matéria especial de alto impacto (6-8 parágrafos)."

    prompt = f"""Você é jornalista da VCtv AInews. Com base no seguinte título e resumo de notícia real, 
escreva uma matéria jornalística completa em português brasileiro.

TÍTULO ORIGINAL: {raw_item['title']}
RESUMO: {raw_item['summary']}
FONTE: {source}

INSTRUÇÕES: {detail}
Use linguagem jornalística formal. Expanda o conteúdo sem inventar fatos.
Retorne APENAS o corpo da matéria, sem repetir o título.
Não use markdown, use apenas texto plano."""

    body = pollinations_generate(prompt)
    return body.strip() if body else raw_item["summary"]


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    now = datetime.datetime.utcnow()
    today_key = now.strftime("%m-%d")
    weekday = now.weekday()  # 0=Mon, 5=Sat, 6=Sun

    # Determine edition type
    if today_key in SPECIAL_EVENTS:
        edition_type = "special"
        event_name = SPECIAL_EVENTS[today_key]
        edition_label = f"Edição Especial — {event_name}"
        articles_per_feed = 6
        model = "openai"
    elif weekday >= 5:
        edition_type = "weekend"
        edition_label = "Edição de Fim de Semana"
        articles_per_feed = 5
        model = "openai"
    else:
        edition_type = "daily"
        edition_label = "Edição Diária"
        articles_per_feed = 3
        model = "mistral"

    print(f"🗞  VCtv AInews — {edition_label}")
    print(f"📅 {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"📰 Tipo: {edition_type} | Modelo: {model}")
    print()

    articles = []

    for feed in RSS_FEEDS:
        print(f"📡 Buscando: {feed['source']}...")
        xml = fetch_url(feed["url"])
        if not xml:
            continue
        items = parse_rss(xml)
        print(f"   {len(items)} itens encontrados, processando {min(articles_per_feed, len(items))}...")

        for item in items[:articles_per_feed]:
            print(f"   ✍  {item['title'][:60]}...")
            full_body = enhance_article(item, feed["source"], feed["category"], edition_type)
            articles.append({
                "title": item["title"],
                "summary": item["summary"],
                "full_body": full_body,
                "source": feed["source"],
                "source_url": item["link"],
                "category": feed["category"],
                "generated_at": item["pub"],
                "ai_enhanced": True,
            })

    # Generate special editorial for weekend/special editions
    if edition_type in ("weekend", "special") and articles:
        print("\n✨ Gerando editorial especial...")
        event_context = f" em homenagem a {event_name}" if edition_type == "special" else ""
        editorial_prompt = f"""Escreva um editorial jornalístico de abertura{event_context} para a VCtv AInews. 
Data: {now.strftime('%d/%m/%Y')}.
Edição: {edition_label}.
Temas em destaque hoje: {', '.join([a['title'][:50] for a in articles[:5]])}

Escreva um editorial reflexivo e relevante de 4-5 parágrafos sobre o panorama atual das notícias.
Apenas o texto, sem título."""

        editorial_body = pollinations_generate(editorial_prompt, model=model)
        if editorial_body:
            articles.insert(0, {
                "title": f"Editorial VCtv AInews — {edition_label}",
                "summary": "Editorial de abertura da edição especial da VCtv AInews.",
                "full_body": editorial_body.strip(),
                "source": "VCtv AInews",
                "source_url": "",
                "category": "Editorial",
                "generated_at": now.isoformat(),
                "ai_enhanced": True,
                "is_editorial": True,
            })

    # Build output
    output = {
        "edition_type": edition_type,
        "edition_label": edition_label,
        "generated_at": now.isoformat(),
        "article_count": len(articles),
        "articles": articles,
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(articles)} artigos salvos em news.json")


if __name__ == "__main__":
    main()
