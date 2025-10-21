# -*- coding: utf-8 -*-
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from typing import List
from .schema import Item

def _fetch(url: str, timeout: int = 12) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (TrendAggregator/1.0; +https://github.com/)",
            "Accept": "application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def parse_rss(url: str, source: str, lang: str = "en") -> List[Item]:
    raw = _fetch(url)
    root = ET.fromstring(raw)
    items = []
    # 兼容 rss/channel/item 与 feed/entry 两种结构
    nodes = root.findall(".//item")
    if not nodes:
        nodes = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    def _text(node, path_options):
        for p in path_options:
            x = node.find(p)
            if x is not None and (x.text or "").strip():
                return x.text.strip()
        return ""

    for it in nodes:
        title = _text(it, ["title", "{http://www.w3.org/2005/Atom}title"])
        if not title:
            continue
        link_node = it.find("link")
        url = ""
        if link_node is not None:
            if link_node.text and link_node.text.strip():
                url = link_node.text.strip()
            elif link_node.get("href"):
                url = link_node.get("href")
        else:
            link_node = it.find("{http://www.w3.org/2005/Atom}link")
            if link_node is not None and link_node.get("href"):
                url = link_node.get("href")

        pub_ts = int(time.time())
        pub_text = _text(it, ["pubDate", "{http://www.w3.org/2005/Atom}updated"])
        if pub_text:
            # 简单解析日期（RSS 常用格式），失败就用当前时间
            try:
                import email.utils
                pub_ts = int(time.mktime(email.utils.parsedate(pub_text)))
            except Exception:
                pass

        items.append(Item.make(title=title, url=url, source=source, ts=pub_ts, lang=lang))
    return items

# 两个可用源（稳定公共 RSS）
def reuters_top() -> List[Item]:
    # 路透 Top News
    return parse_rss("https://www.reuters.com/world/rss", source="reuters", lang="en")

def google_news_world() -> List[Item]:
    # Google News World（英文全球）
    return parse_rss("https://news.google.com/news/rss?hl=en-US&gl=US&ceid=US:en", source="google-news", lang="en")
