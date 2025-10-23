from collections import Counter
import re
from difflib import SequenceMatcher

def normalize_title(title: str) -> str:
    """去除符号与空格用于比对"""
    return re.sub(r"[\W_]+", "", title.lower())

def calc_similarity(a: str, b: str) -> float:
    """标题相似度（0~1）"""
    return SequenceMatcher(None, a, b).ratio()

def compute_heat_score(items, sim_threshold=0.6):
    """
    基于相似标题与多源出现频率计算热度分数
    - 出现次数越多、跨源越多 → 热度越高
    """
    if not items:
        return []

    scores = []
    normalized = [normalize_title(i["title"]) for i in items]
    source_counter = Counter([i["source"] for i in items])

    for idx, item in enumerate(items):
        score = 1.0  # 基础分
        this = normalized[idx]

        # 同类标题重复加权
        for j, other in enumerate(normalized):
            if idx != j and calc_similarity(this, other) > sim_threshold:
                score += 0.5

        # 来源权重（来源越热门加权越低）
        score += source_counter[item["source"]] * 0.1
        scores.append(score)

    # 标准化到 0~100
    max_score = max(scores)
    for i, s in enumerate(scores):
        items[i]["heat"] = round(100 * s / max_score, 2)

    return sorted(items, key=lambda x: x["heat"], reverse=True)
