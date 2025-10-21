import json, requests, re, jieba
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# ------------------------
# 导入已有英文源
# ------------------------
from sources_rss import fetch_google_news  # 这是你原有英文RSS抓取逻辑文件

# ------------------------
# 导入中文源
# ------------------------
from zh_sources import (
    fetch_zhihu_hot,
    fetch_weibo_hot,
    fetch_baidu_hot,
    fetch_toutiao_hot
)

# ------------------------
# 文本清洗与聚类逻辑
# ------------------------
def clean_text(t):
    return re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]+", " ", t)

def cluster_topics(titles, n_clusters=6):
    if not titles:
        return []
    texts = [clean_text(t) for t in titles]
    vectorizer = TfidfVectorizer(
        tokenizer=lambda x: jieba.lcut(x),
        max_features=500
    )
    X = vectorizer.fit_transform(texts)
    km = KMeans(
        n_clusters=min(n_clusters, len(texts)),
        random_state=42
    )
    km.fit(X)
    clusters = {}
    for i, label in enumerate(km.labels_):
        clusters.setdefault(label, []).append(titles[i])
    return [
        {"cluster": i, "samples": v[:5]} for i, v in clusters.items()
    ]

# ------------------------
# 主程序入口
# ------------------------
def main():
    # 中文趋势
    zh = (
        fetch_zhihu_hot()
        + fetch_weibo_hot()
        + fetch_baidu_hot()
        + fetch_toutiao_hot()
    )

    # 英文趋势
    en = fetch_google_news()

    # 合并
    combined = zh + en

    # 聚类
    clusters = cluster_topics([t["title"] for t in combined])

    # 汇总输出
    result = {
        "generated_at": datetime.now().isoformat(),
        "source_count": len(set(t["source"] for t in combined)),
        "topic_count": len(combined),
        "topics": combined,
        "clusters": clusters,
    }

    with open("../api/trends.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ trends.json 已生成，共 %d 条记录。" % len(combined))

# ------------------------
# 程序执行
# ------------------------
if __name__ == "__main__":
    main()
