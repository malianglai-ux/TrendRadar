# -*- coding: utf-8 -*-
import json
import os
import time
from typing import List
from .schema import Item
from .sources_rss import reuters_top, google_news_world
from .dedup_cluster import cluster_items
from .score import score_topic

OUT_API = "api/trends.json"   # 统一输出
os.makedirs("api", exist_ok=True)

def collect_all() -> List[Item]:
    items: List[Item] = []
    # 目前先接两路稳定源；后续逐步加中文站点
    for fetch in (reuters_top, google_news_world):
        try:
            items.extend(fetch())
        except Exception as e:
            print("[warn] source fetch failed:", fetch.__name__, e)
    return items

def run():
    now_ts = int(time.time())
    items = collect_all()
    # 去重聚合
    topics = cluster_items(items, threshold=0.85)
    # 打分
    for tp in topics:
        tp["score"] = round(score_topic(tp, now_ts), 4)
        # 输出最简代表字段，方便前端使用
        tp["title"] = tp["rep_title"]
        tp["links"] = [{"title": it.title, "url": it.url, "source": it.source, "ts": it.ts} for it in tp["items"]]
        # 清理内部字段
        del tp["rep_title"]
        del tp["items"]
    # 排序并截断（防止过长）
    topics.sort(key=lambda x: x["score"], reverse=True)
    topics = topics[:120]

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now_ts)),
        "source_count": len(set([l["source"] for t in topics for l in t["links"]])),
        "topic_count": len(topics),
        "topics": topics,
    }
    with open(OUT_API, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[ok] write {OUT_API}, topics={len(topics)}")

if __name__ == "__main__":
    run()
