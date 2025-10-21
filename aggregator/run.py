import json, requests, re, jieba
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# ------------------------
# 数据源：英文
# ------------------------
def fetch_google_news():
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    import feedparser
    feed = feedparser.parse(url)
    return [{
        "title": e.title,
        "source": "google-news",
        "url": e.link,
        "ts": int(datetime.now().timestamp())
    } for e in feed.entries[:30]]

# ------------------------
# 数据源：中文
# ------------------------
def fetch_zhihu_hot():
    try:
        r = requests.get("https://www.zhihu.com/api/v4/hotlist/sections/total", timeout=10).json()
        return [{"title": i["target"]["title_area"]["text"], "source": "zhihu",
                 "url": i["target"]["link"]["url"], "ts": int(datetime.now().timestamp())}
                for i in r["data"]]
    except: return []

def fetch_weibo_hot():
    try:
        r = requests.get("https://weibo.com/ajax/side/hotSearch", timeout=10).json()
        return [{"title": i["word"], "source": "weibo",
                 "url": "https://s.weibo.com/weibo?q=" + i["word"],
                 "ts": int(datetime.now().timestamp())}
                for i in r["data"]["realtime"]]
    except: return []

def fetch_baidu_hot():
    try:
        r = requests.get("https://top.baidu.com/api/board?platform=pc&tab=realtime", timeout=10).json()
        return [{"title": i["word"], "source": "baidu",
                 "url": i["url"], "ts": int(datetime.now().timestamp())}
                for i in r["data"]["cards"][0]["content"]]
    except: return []

def fetch_toutiao_hot():
    try:
        r = requests.get("https://www.toutiao.com/hot-event/hot-board/", timeout=10).json()
        return [{"title": i["Title"], "source": "toutiao",
                 "url": "https://www.toutiao.com" + i["Url"],
                 "ts": int(datetime.now().timestamp())}
                for i in r["data"]]
    except: return []

# ------------------------
# 聚类逻辑
# ------------------------
def clean_text(t): return re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]+", " ", t)

def cluster_topics(titles, n_clusters=6):
    if not titles: return []
    texts = [clean_text(t) for t in titles]
    vectorizer = TfidfVectorizer(tokenizer=lambda x: jieba.lcut(x), max_features=500)
    X = vectorizer.fit_transform(texts)
    km = KMeans(n_clusters=min(n_clusters, len(texts)), random_state=42)
    km.fit(X)
    clusters = {}
    for i, label in enumerate(km.labels_):
        clusters.setdefault(label, []).append(titles[i])
    return [{"cluster": i, "samples": v[:5]} for i, v in clusters.items()]

# ------------------------
# 主执行逻辑
# ------------------------
def main():
    zh = fetch_zhihu_hot() + fetch_weibo_hot() + fetch_baidu_hot() + fetch_toutiao_hot()
    en = fetch_google_news()
    combined = zh + en
    clusters = cluster_topics([t["title"] for t in combined])

    result = {
        "generated_at": datetime.now().isoformat(),
        "source_count": len(set(t["source"] for t in combined)),
        "topic_count": len(combined),
        "topics": combined,
        "clusters": clusters
    }
    with open("../api/trends.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("✅ trends.json 已更新")

if __name__ == "__main__":
    main()
