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
        return [{"topic": t, "size": 1, "score": 1.0, "titles": [t]} for t in titles]

    seg_titles = segment_texts(titles)
    vectorizer = TfidfVectorizer(max_features=300)
    X = vectorizer.fit_transform(seg_titles)

    k = min(num_clusters, len(titles))
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(X)

    clusters = {}
    for i, label in enumerate(labels):
        clusters.setdefault(label, []).append(titles[i])

    results = []
    for label, items in clusters.items():
        results.append({
            "topic": items[0][:40],
            "size": len(items),
            "score": round(float(len(items) / len(titles)), 3),
            "titles": items
        })
    return results


# ===== 主程序 =====
def main():
    print("正在抓取中英文热点...")

    # 抓取英文源
    en_news = fetch_google_news()
    en_titles = [clean_text(i["title"]) for i in en_news]

    # 抓取中文源
    zh_data = []
    zh_data += fetch_zhihu_hot()
    zh_data += fetch_weibo_hot()
    zh_data += fetch_baidu_hot()
    zh_data += fetch_toutiao_hot()
    zh_titles = [clean_text(i["title"]) for i in zh_data]

    # 聚类
    all_titles = en_titles + zh_titles
    topics = cluster_topics(all_titles, num_clusters=12)

    # 输出结果
    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_count": len(all_titles),
        "topic_count": len(topics),
        "topics": topics,
    }

    out_path = "./api/trends.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已生成聚合文件: {out_path} ({len(all_titles)} 条)")


if __name__ == "__main__":
    main()
