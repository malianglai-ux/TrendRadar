from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import jieba
import re

def clean_text(t):
    return re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]+", " ", t)

def cluster_topics(titles, n_clusters=6):
    texts = [clean_text(t) for t in titles]
    if not texts: return []
    vectorizer = TfidfVectorizer(
        tokenizer=lambda x: jieba.lcut(x),
        max_features=500
    )
    X = vectorizer.fit_transform(texts)
    km = KMeans(n_clusters=min(n_clusters, len(texts)), random_state=42)
    km.fit(X)
    labels = km.labels_
    clusters = {}
    for i, label in enumerate(labels):
        clusters.setdefault(label, []).append(titles[i])
    # 取每个聚类的代表词
    return [
        {"cluster": i, "samples": v[:5]} for i, v in clusters.items()
    ]
