import feedparser
from datetime import datetime

def fetch_google_news():
    """Google News（英文）"""
    feed = feedparser.parse("https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en")
    items = []
    for entry in feed.entries[:50]:
        items.append({
            "title": entry.title,
            "url": entry.link,
            "source": "google-news",
            "ts": int(datetime.now().timestamp())
        })
    return items

def collect_english_trends():
    """汇总英文来源（后续可扩展更多）"""
    return fetch_google_news()
