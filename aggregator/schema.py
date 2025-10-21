# -*- coding: utf-8 -*-
import hashlib
import re
import time
from dataclasses import dataclass, asdict

def now_ts() -> int:
    return int(time.time())

def norm_text(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)           # 压空格
    s = re.sub(r"[|·•・\-—~_#@]+", " ", s)
    s = s.replace("，", ",").replace("。", ".").lower()
    return s

def stable_id(*parts: str) -> str:
    h = hashlib.sha1()
    for p in parts:
        h.update((p or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:16]

@dataclass
class Item:
    id: str
    title: str
    url: str
    source: str
    ts: int
    rank: int = 0
    hot: float = 0.0
    lang: str = "zh"
    topic: str = ""

    @staticmethod
    def make(title: str, url: str, source: str, ts: int = None, rank: int = 0, hot: float = 0.0, lang: str = "zh"):
        title_n = norm_text(title)
        url_n = (url or "").strip()
        i = Item(
            id=stable_id(title_n, url_n, source),
            title=title.strip(),
            url=url_n,
            source=source,
            ts=ts if ts else now_ts(),
            rank=rank,
            hot=hot,
            lang=lang,
            topic=""
        )
        return i

    def asdict(self):
        return asdict(self)
