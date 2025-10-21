import feedparser

def fetch_google_news():
    """从 Google News RSS 抓取热点"""
    print("正在抓取 Google News...")
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)

    items = []
    for entry in feed.entries[:50]:
        items.append({
            "title": entry.title,
            "url": entry.link,
            "source": "google-news",
            "ts": int(getattr(entry, "published_parsed", (0,))[0]) if hasattr(entry, "published_parsed") else 0,
        })
    print(f"Google News 抓取完成，共 {len(items)} 条")
    return items
