import requests
import json
from datetime import datetime

def fetch_zhihu_hot():
    url = "https://www.zhihu.com/api/v4/hotlist/sections/total"
    try:
        data = requests.get(url, timeout=8).json()
        return [
            {
                "title": i["target"]["title_area"]["text"],
                "source": "zhihu",
                "url": i["target"]["link"]["url"],
                "ts": int(datetime.now().timestamp())
            } for i in data["data"]
        ]
    except:
        return []

def fetch_weibo_hot():
    url = "https://weibo.com/ajax/side/hotSearch"
    try:
        data = requests.get(url, timeout=8).json()
        return [
            {
                "title": i["word"],
                "source": "weibo",
                "url": "https://s.weibo.com/weibo?q=" + i["word"],
                "ts": int(datetime.now().timestamp())
            } for i in data["data"]["realtime"]
        ]
    except:
        return []

def fetch_baidu_hot():
    url = "https://top.baidu.com/api/board?platform=pc&tab=realtime"
    try:
        data = requests.get(url, timeout=8).json()
        return [
            {
                "title": i["word"],
                "source": "baidu",
                "url": i["url"],
                "ts": int(datetime.now().timestamp())
            } for i in data["data"]["cards"][0]["content"]
        ]
    except:
        return []

def fetch_toutiao_hot():
    url = "https://www.toutiao.com/hot-event/hot-board/"
    try:
        data = requests.get(url, timeout=8).json()
        return [
            {
                "title": i["Title"],
                "source": "toutiao",
                "url": "https://www.toutiao.com" + i["Url"],
                "ts": int(datetime.now().timestamp())
            } for i in data["data"]
        ]
    except:
        return []

def collect_chinese_trends():
    zh = fetch_zhihu_hot()
    wb = fetch_weibo_hot()
    bd = fetch_baidu_hot()
    tt = fetch_toutiao_hot()
    return zh + wb + bd + tt
