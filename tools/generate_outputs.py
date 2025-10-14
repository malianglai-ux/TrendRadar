# tools/generate_outputs.py
# 作用：
# 1) 生成 output/YYYYMMDD/metrics.json（供首页图表读取）
# 2) 若 output/YYYYMMDD/html/当日热点.html 不存在，则写入一个占位片段（不覆盖你已有日报）

import json
import os
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))  # 北京时间

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def today_dir() -> str:
    return datetime.now(TZ).strftime("%Y%m%d")

def write_metrics_json(base_dir: str):
    """
    这里给出一个稳定的示例格式。
    之后你有真实数据时，替换下面 metrics 的 labels/series 即可。
    """
    metrics = {
        "labels": ["09:30","10:00","10:30","11:00","13:00","14:00","14:30","15:00"],
        "series": [
            {"name": "人工智能", "data": [12, 18, 25, 27, 30, 28, 35, 40]},
            {"name": "光伏",     "data": [ 8, 12, 14, 18, 20, 22, 21, 24]},
            {"name": "台积电",   "data": [10, 11, 13, 15, 16, 18, 19, 22]}
        ]
    }
    ensure_dir(base_dir)
    out_file = os.path.join(base_dir, "metrics.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"✅ metrics.json 写入完成: {out_file}")

def write_daily_stub_if_absent(html_dir: str):
    """
    如果你已经有爬虫生成的当日热点，不做任何事。
    没有的话写入一个简单占位片段，首页就能正常展示。
    """
    ensure_dir(html_dir)
    target = os.path.join(html_dir, "当日热点.html")
    if os.path.exists(target):
        print(f"ℹ️ 检测到已有当日热点文件，跳过占位写入: {target}")
        return

    stub = """<h2>📈 今日重点趋势</h2>
<div class="trend-card">
  <h3>示例：新能源板块资金回流</h3>
  <p class="source">来源：示例源 · 10:15</p>
</div>
<div class="trend-card">
  <h3>示例：美债收益率回落，科技股反弹</h3>
  <p class="source">来源：示例源 · 09:45</p>
</div>"""
    with open(target, "w", encoding="utf-8") as f:
        f.write(stub)
    print(f"✅ 当日热点占位片段已写入: {target}")

def main():
    d = today_dir()
    day_root = os.path.join("output", d)
    write_metrics_json(day_root)
    write_daily_stub_if_absent(os.path.join(day_root, "html"))

if __name__ == "__main__":
    main()
