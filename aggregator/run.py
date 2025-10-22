import json, requests, re, jieba
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# ===== 数据源导入 =====
# 英文 RSS 抓取模块
from .sources_rss import fetch_google_news

# 中文热搜抓取模块
from .zh_sources import (
    fetch_zhihu_hot,
    fetch_weibo_hot,
    fetch_baidu_hot,
    fetch_toutiao_hot
)

# ===== 工具函数 =====
def clean_text(text: str) -> str:
    """清洗标题文本"""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9\s]", "", text)
    return text.strip()

def segment_texts(texts):
    """根据语言分词"""
    segs = []
    for t in texts:
        if re.search(r'[\u4e00-\u9fa5]', t):
            segs.append(" ".join(jieba.cut(t)))
        else:
            segs.append(t)
    return segs

def cluster_topics(titles, num_clusters=10):
    """基于 TF-IDF 的文本聚类"""
    if len(titles) <= 2:
        return [{"cluster": idx, "samples": [t]} for idx, t in enumerate(titles)]

    seg_titles = segment_texts(titles)
    vectorizer = TfidfVectorizer(max_features=300)
    X = vectorizer.fit_transform(seg_titles)

    k = min(num_clusters, len(titles))
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(X)

    clusters = {}
    for title, label in zip(titles, labels):
        clusters.setdefault(label, []).append(title)

    results = []
    for label, items in clusters.items():
        results.append({
            "cluster": int(label),
            "samples": items
        })
    return results

# ===== 主程序 =====
def main():
    print("正在抓取中英文热点...")

    # 抓取英文源
    en_news = fetch_google_news()
    # 将英文数据转换为统一格式
    en_items = []
    for item in en_news:
        title = item.get("title", "")
        link = item.get("link") or item.get("url")
        en_items.append({
            "title": title,
            "source": "google",
            "score": 1,
            "links": [{"url": link, "title": title}] if link else []
        })

    # 抓取中文源
    zh_items = []
    for func in [fetch_zhihu_hot, fetch_weibo_hot, fetch_baidu_hot, fetch_toutiao_hot]:
        for item in func():
            title = item.get("title", "")
            link = item.get("url") or item.get("link")
            zh_items.append({
                "title": title,
                "source": item.get("source"),
                "score": 1,
                "links": [{"url": link, "title": title}] if link else []
            })

    all_items = en_items + zh_items
    all_titles = [clean_text(it["title"]) for it in all_items]

    # 聚类
    clusters = cluster_topics(all_titles, num_clusters=12)

    # 输出结果
    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_count": len(all_items),
        "topic_count": len(all_items),
        "topics": all_items,
        "clusters": clusters
    }

    out_path = "./api/trends.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已生成聚合文件: {out_path} ({len(all_items)} 条)")

if __name__ == "__main__":
    main()
