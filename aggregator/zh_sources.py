import requests
from datetime import datetime

def fetch_zhihu_hot():
    """知乎热榜"""
    try:
        resp = requests.get("https://www.zhihu.com/api/v4/hotlist/sections/total", timeout=10).json()
        return [
            {
                "title": item["target"]["title_area"]["text"],
                "url": item["target"]["link"]["url"],
                "source": "zhihu",
                "ts": int(datetime.now().timestamp())
            }
            for item in resp["data"]
        ]
    except Exception:
        return []

def fetch_weibo_hot():
    """微博热搜"""
    try:
        resp = requests.get("https://weibo.com/ajax/side/hotSearch", timeout=10).json()
        return [
            {
                "title": item["word"],
                "url": f"https://s.weibo.com/weibo?q={item['word']}",
                "source": "weibo",
                "ts": int(datetime.now().timestamp())
            }
            for item in resp["data"]["realtime"]
        ]
    except Exception:
        return []

def fetch_baidu_hot():
    """百度热榜"""
    try:
        resp = requests.get("https://top.baidu.com/api/board?platform=pc&tab=realtime", timeout=10).json()
        return [
            {
                "title": item["word"],
                "url": item["url"],
                "source": "baidu",
                "ts": int(datetime.now().timestamp())
            }
            for item in resp["data"]["cards"][0]["content"]
        ]
    except Exception:
        return []

def fetch_toutiao_hot():
    """今日头条热榜"""
    try:
        resp = requests.get("https://www.toutiao.com/hot-event/hot-board/", timeout=10).json()
        return [
            {
                "title": item["Title"],
                "url": "https://www.toutiao.com" + item["Url"],
                "source": "toutiao",
                "ts": int(datetime.now().timestamp())
            }
            for item in resp["data"]
        ]
    except Exception:
        return []

def collect_chinese_trends():
    """汇总中文来源"""
    return (
        fetch_zhihu_hot()
        + fetch_weibo_hot()
        + fetch_baidu_hot()
        + fetch_toutiao_hot()
    )
