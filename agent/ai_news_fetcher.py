import feedparser
import requests
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

AI_KEYWORDS = [
    "artificial intelligence", "AI", "machine learning", "neural network", "deep learning",
    "LLM", "GPT", "Claude", "Anthropic", "OpenAI", "transformer", "AGI"
]

SOURCES = [
    {
        "name": "VentureBeat",
        "rss_url": "https://venturebeat.com/feed/",
        "article_selector": "div.article-content"
    },
    {
        "name": "TechCrunch",
        "rss_url": "https://techcrunch.com/feed/",
        "article_selector": "div.entry-content"
    }
]


def load_existing_articles(filename="ai_news_curated.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def extract_links(articles):
    return set(article["link"] for article in articles)


def contains_ai_keywords(text):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in AI_KEYWORDS)


def extract_full_content(url, selector):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")
        content_div = soup.select_one(selector)
        if not content_div:
            return ""
        paragraphs = content_div.find_all(['p', 'h2'])
        return "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    except Exception as e:
        return ""


def fetch_all_sources(existing_links):
    new_articles = []
    for source in SOURCES:
        print(f"🔍 Fetching from {source['name']} ...")
        try:
            feed = feedparser.parse(source["rss_url"])
            for entry in feed.entries[:5]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                if link in existing_links or not contains_ai_keywords(title + summary):
                    continue

                content = extract_full_content(link, source["article_selector"])
                if content:
                    new_articles.append({
                        "source": source["name"],
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "content": content,
                        "published": entry.get("published", "")
                    })
                    existing_links.add(link)
        except Exception as e:
            print(f"⚠️ Error with {source['name']}: {e}")
        time.sleep(1)
    return new_articles


def save_to_json(all_articles, filename="ai_news_curated.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)


def get_ai_updates():
    existing_articles = load_existing_articles()
    existing_links = extract_links(existing_articles)

    new_articles = fetch_all_sources(existing_links)

    if new_articles:
        updated_articles = existing_articles + new_articles
        save_to_json(updated_articles)
        print(f"\n✅ Saved {len(new_articles)} new AI-related articles.")
        return new_articles
    else:
        print("\nℹ️ No new articles found.")
        return []


if __name__ == "__main__":
    get_ai_updates()