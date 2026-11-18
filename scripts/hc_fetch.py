#!/usr/bin/env python3
"""即時抓取單篇飛書幫助中心文章（頁面改版或語料過期時使用）。

用法：
  python3 hc_fetch.py https://www.feishu.cn/hc/zh-CN/articles/410718208321-工作台介绍
  python3 hc_fetch.py 410718208321            # 用文章 ID（會自動 301 到正式網址）
"""
import gzip, json, re, sys, urllib.parse, urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
BASE = "https://www.feishu.cn"
MARKERS = ["window._templateValue = ", "window._defaultTemplateValue = "]


def norm_url(url):
    """把含中文的網址轉成可請求的形式。"""
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((
        parts.scheme, parts.netloc,
        urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/"),
        urllib.parse.quote(urllib.parse.unquote(parts.query), safe="=&"),
        ""))


def get(url):
    req = urllib.request.Request(norm_url(url), headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return data.decode("utf-8", "ignore")


def json_at(s, start):
    depth = 0; in_str = False; esc = False
    for i in range(start, len(s)):
        c = s[i]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
            continue
        if c == '"': in_str = True
        elif c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: return s[start:i + 1]
    return None


def walk(node, tabs, faq):
    if isinstance(node, dict):
        h = node.get("html")
        if isinstance(h, dict) and isinstance(h.get("text"), str) and len(h["text"]) > 20:
            tabs.append((node.get("tabName") or "", h["text"]))
        if isinstance(node.get("question"), str) and isinstance(node.get("answer_txt"), str):
            q = re.sub(r"^问[：:]\s*", "", node["question"].strip())
            a = re.sub(r"^答[：:]\s*", "", node["answer_txt"].strip())
            faq.append((q, a))
        for v in node.values():
            walk(v, tabs, faq)
    elif isinstance(node, list):
        for v in node:
            walk(v, tabs, faq)


def fetch(target):
    if target.isdigit():
        url = f"{BASE}/hc/zh-CN/articles/{target}"
    else:
        url = target
    html = get(url)
    for m in MARKERS:
        k = html.find(m)
        if k < 0:
            continue
        s = html.find("{", k + len(m))
        js = json_at(html, s)
        if not js:
            continue
        try:
            obj = json.loads(js)
        except Exception:
            continue
        tabs, faq = [], []
        walk(obj, tabs, faq)
        body = "\n\n".join((f"【{n}】\n{t}" if n else t) for n, t in tabs if len(t.strip()) > 20)
        if len(body) < 50 and faq:
            body = "\n\n".join(f"问：{q}\n答：{a}" for q, a in faq)
        title = obj.get("MwtJhWBjrj") or obj.get("WPPd2Oxz2G") or ""
        if body.strip():
            return title, body
    return "", "（找不到正文，頁面可能改版；請直接開原文閱讀）"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    t, b = fetch(sys.argv[1])
    print(f"# {t}\n")
    print(b)
