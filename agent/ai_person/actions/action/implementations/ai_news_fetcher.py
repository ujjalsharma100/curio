import feedparser
import requests
from bs4 import BeautifulSoup
import json
import time
import os
import logging
from datetime import datetime

# Setup logging for ai_news_fetcher
def setup_news_fetcher_logging():
    """Setup logging for the ai_news_fetcher module."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"ai_news_fetcher_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    logger = logging.getLogger("ai_person.actions.ai_news_fetcher")
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_news_fetcher_logging()

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

def contains_ai_keywords(text):
    text_lower = text.lower()
    matches = [kw for kw in AI_KEYWORDS if kw.lower() in text_lower]
    if matches:
        logger.debug(f"Found AI keywords in text: {matches}")
    return len(matches) > 0


def extract_full_content(url, selector):
    logger.debug(f"Extracting content from URL: {url} with selector: {selector}")
    try:
        logger.debug(f"Making HTTP request to: {url}")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        logger.debug(f"HTTP response status: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.warning(f"HTTP request failed with status {resp.status_code} for URL: {url}")
            return ""
            
        soup = BeautifulSoup(resp.content, "html.parser")
        content_div = soup.select_one(selector)
        
        if not content_div:
            logger.warning(f"No content div found with selector '{selector}' for URL: {url}")
            return ""
            
        paragraphs = content_div.find_all(['p', 'h2'])
        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        logger.debug(f"Extracted {len(content)} characters of content from URL: {url}")
        return content
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while fetching content from URL: {url}")
        return ""
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching content from URL {url}: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error while extracting content from URL {url}: {str(e)}")
        return ""


def fetch_article_content(article):
    """Fetch full content for a given article item.
    
    Args:
        article (dict): Article item containing source name and link
        
    Returns:
        str: Full article content
    """
    logger.debug(f"Fetching article content for: {article.get('title', 'No title')}")
    source = next((s for s in SOURCES if s["name"] == article["source"]), None)
    if not source:
        logger.warning(f"No source configuration found for: {article.get('source', 'Unknown source')}")
        return ""
    return extract_full_content(article["link"], source["article_selector"])


def fetch_all_sources():
    logger.info("Starting to fetch from all RSS sources")
    new_articles = []
    
    for source in SOURCES:
        logger.info(f"Fetching from {source['name']} ...")
        print(f"🔍 Fetching from {source['name']} ...")
        
        try:
            logger.debug(f"Parsing RSS feed: {source['rss_url']}")
            feed = feedparser.parse(source["rss_url"])
            logger.debug(f"RSS feed parsed successfully, found {len(feed.entries)} entries")
            
            articles_from_source = 0
            for i, entry in enumerate(feed.entries[:5]):
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                
                logger.debug(f"Processing entry {i+1}: {title}")

                if not contains_ai_keywords(title + summary):
                    logger.debug(f"Skipping entry {i+1}: No AI keywords found")
                    continue

                new_articles.append({
                    "source": source["name"],
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "content": "",
                    "published": entry.get("published", "")
                })
                articles_from_source += 1
                logger.debug(f"Added article from {source['name']}: {title}")
                
            logger.info(f"Found {articles_from_source} AI-related articles from {source['name']}")
            
        except Exception as e:
            logger.error(f"Error fetching from {source['name']}: {str(e)}", exc_info=True)
            print(f"⚠️ Error with {source['name']}: {e}")
            
        time.sleep(1)
    
    logger.info(f"Total AI-related articles found across all sources: {len(new_articles)}")
    return new_articles


def get_ai_updates():
    logger.info("Starting AI updates retrieval process")
    new_articles = fetch_all_sources()
    
    if new_articles:
        logger.info(f"Successfully retrieved {len(new_articles)} AI updates")
        return new_articles
    else:
        logger.info("No new articles found")
        print("\nℹ️ No new articles found.")
        return []
