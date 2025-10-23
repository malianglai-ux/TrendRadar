import json
from datetime import datetime
from .zh_sources import collect_chinese_trends
from .sources_rss import collect_english_trends
from .score import compute_heat_score

def main():
    zh_trends = collect_chinese_trends()
    en_trends = collect_english_trends()
    all_trends = zh_trends + en_trends

    # 计算热度
    all_trends = compute_heat_score(all_trends)

    out = {
        "generated_at": datetime.now().isoformat(),
        "source_count": len(set(t["source"] for t in all_trends)),
        "topic_count": len(all_trends),
        "topics": all_trends
    }

    with open("api/trends.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"[OK] Generated {len(all_trends)} topics from {out['source_count']} sources.")

if __name__ == "__main__":
    main()
