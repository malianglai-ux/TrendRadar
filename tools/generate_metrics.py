# -*- coding: utf-8 -*-
"""
TrendRadar metrics.json 自动生成模块
----------------------------------
功能：
  - 从 api/trends.json 读取今日热点关键词与时间分布
  - 统计每个关键词在时间刻度内的出现次数
  - 生成前端可直接绘制的 metrics.json 文件

输出路径：
  output/{YYYYMMDD}/metrics.json
"""

import os
import re
import json
import datetime as dt
from collections import defaultdict

# ========== 配置部分 ==========
# 时间刻度（前端会直接按这些横轴标签绘制）
SLOTS = ["09:30","10:00","10:30","11:00","13:00","14:00","14:30","15:00"]

# 默认关键词（若 trends.json 中没有数据则兜底）
DEFAULT_KEYWORDS = ["人工智能", "光伏", "台积电"]

# ========== 工具函数 ==========
def hm_to_min(hm: str) -> int:
    """把 'HH:MM' 转为分钟"""
    h, m = hm.split(":")
    return int(h)*60 + int(m)

SLOT_MINUTES = [hm_to_min(x) for x in SLOTS]

TIME_RE = re.compile(r"\[(\d{2})时(\d{2})分\s*~\s*(\d{2})时(\d{2})分\]")

def parse_time_info_span(time_info: str):
    """解析 time_info，例如 '[00时33分 ~ 14时11分]' -> (33, 851)"""
    if not time_info:
        return None
    m = TIME_RE.search(time_info)
    if not m:
        return None
    sh, sm, eh, em = map(int, m.groups())
    start = sh*60 + sm
    end = eh*60 + em
    if end < start:
        end = start
    return start, end

def put_to_slot_index(minute_val: int) -> int:
    """将分钟值归入最近的时间刻度"""
    idx = 0
    for i, base in enumerate(SLOT_MINUTES):
        if minute_val >= base:
            idx = i
        else:
            break
    return idx

# ========== 主函数 ==========
def build_metrics_from_trends(trends_json_path: str,
                              out_dir: str,
                              date_str: str,
                              top_keywords=None):
    """根据 trends.json 生成 metrics.json"""
    # 读取 trends.json
    with open(trends_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    trends = data.get("trends", [])
    kw_list = top_keywords or DEFAULT_KEYWORDS
    buckets = {kw: [0]*len(SLOTS) for kw in kw_list}

    for item in trends:
        kw = item.get("keyword_group", "")
        if kw not in buckets:
            continue
        titles = item.get("titles", [])
        for t in titles:
            span = parse_time_info_span(t.get("time_info", ""))
            if not span:
                continue
            _, end_min = span
            slot_idx = put_to_slot_index(end_min)
            buckets[kw][slot_idx] += 1

    # 累计求和，使曲线更平滑（可选）
    for kw in buckets:
        acc = 0
        for i,v in enumerate(buckets[kw]):
            acc += v
            buckets[kw][i] = acc

    metrics = {
        "labels": SLOTS,
        "series": [{"name": kw, "data": buckets[kw]} for kw in kw_list]
    }

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "metrics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"[metrics] 输出完成: {out_path}")
    return out_path

# ========== 独立运行入口 ==========
if __name__ == "__main__":
    today = dt.datetime.now().strftime("%Y%m%d")
    trends_path = os.path.join("api", "trends.json")
    out_dir = os.path.join("output", today)

    # 自动取当天热点前三个关键词
    try:
        with open(trends_path, "r", encoding="utf-8") as f:
            jj = json.load(f)
        auto_kw = [x["keyword_group"] for x in jj.get("trends", [])[:3]]
        auto_kw = auto_kw or DEFAULT_KEYWORDS
    except Exception:
        auto_kw = DEFAULT_KEYWORDS

    build_metrics_from_trends(trends_path, out_dir, today, top_keywords=auto_kw)
