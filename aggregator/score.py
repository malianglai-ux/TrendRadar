# -*- coding: utf-8 -*-
import math
from typing import Dict

PLATFORM_WEIGHT = {
    "reuters": 1.0,
    "google-news": 0.7,
    # 未来新增中文站点时继续补：wallstreetcn、zhihu、weibo、bilibili、baidu、toutiao ...
}

def score_topic(tp: Dict, now_ts: int) -> float:
    # 简版评分： coverage + authority + freshness
    coverage = tp.get("cover", 1)
    authority = 0.0
    for it in tp["items"]:
        authority += PLATFORM_WEIGHT.get(it.source, 0.5)
    # 取均值
    authority = authority / max(1, tp["size"])
    # 时间衰减（最近越高）
    dt = max(1, now_ts - tp["max_ts"])
    freshness = math.exp(-dt / (6 * 3600.0))  # 6 小时半衰

    return 0.45 * coverage + 0.35 * authority + 0.20 * freshness
