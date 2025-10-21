# -*- coding: utf-8 -*-
from typing import List, Dict, Tuple
from .schema import Item, norm_text, stable_id

def title_sim(a: str, b: str) -> float:
    """极简相似度：基于 token 的 Jaccard，相似>0.85 判同题"""
    ta = set(norm_text(a).split())
    tb = set(norm_text(b).split())
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union

def cluster_items(items: List[Item], threshold: float = 0.85) -> List[Dict]:
    topics: List[Dict] = []
    for it in items:
        placed = False
        for tp in topics:
            # 用簇代表标题做快速判断
            if title_sim(tp["rep_title"], it.title) >= threshold:
                tp["items"].append(it)
                # 更新时间范围
                tp["min_ts"] = min(tp["min_ts"], it.ts)
                tp["max_ts"] = max(tp["max_ts"], it.ts)
                placed = True
                break
        if not placed:
            topics.append({
                "topic": stable_id(it.title[:64]),   # 代表标题 hash
                "rep_title": it.title,
                "items": [it],
                "min_ts": it.ts,
                "max_ts": it.ts,
            })
    # 附加统计
    for tp in topics:
        srcs = {i.source for i in tp["items"]}
        tp["sources"] = sorted(list(srcs))
        tp["cover"] = len(srcs)
        tp["size"] = len(tp["items"])
    # 简单排序：先按覆盖平台数，再按最新时间
    topics.sort(key=lambda x: (x["cover"], x["max_ts"]), reverse=True)
    return topics
