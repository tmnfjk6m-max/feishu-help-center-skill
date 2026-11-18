#!/usr/bin/env python3
"""飛書幫助中心全文檢索（離線，基於 ../data/articles.jsonl.gz）。

用法：
  python3 hc_search.py 视频会议 最大人数          # 多關鍵字（AND 優先，無結果自動放寬為 OR）
  python3 hc_search.py 审批 转交 --limit 15
  python3 hc_search.py --product 多维表格 权限     # 限定產品線
  python3 hc_search.py --faq 会议 加密             # 只輸出問答段落
"""
import argparse, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data", "articles.jsonl.gz")


def load():
    with gzip.open(DATA, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def hit(rec, kws):
    text = rec.get("text", "")
    title = rec.get("title", "")
    return all((k in title or k in text) for k in kws)


def score(rec, kws):
    text = rec.get("text", "")
    title = rec.get("title", "")
    s = 0
    for k in kws:
        s += title.count(k) * 12 + text.count(k) * 2
    return s


def snippet(text, kws, width=140):
    text = re.sub(r"\s+", " ", text)
    pos = -1
    for k in kws:
        p = text.find(k)
        if p >= 0 and (pos < 0 or p < pos):
            pos = p
    if pos < 0:
        return text[:width]
    start = max(0, pos - width // 2)
    return ("…" if start else "") + text[start:start + width] + "…"


def faq_blocks(text, kws):
    """把 FAQ 型文章切成問答段，優先回傳同時命中所有關鍵字的段落。"""
    blocks = re.split(r"(?m)^问", text)
    if text.lstrip().startswith("问"):
        blocks = ["问" + b for b in blocks if b.strip()]
    else:
        blocks = ["问" + b for b in blocks[1:] if b.strip()]
    strict = [b for b in blocks if all(k in b for k in kws)]
    loose = [b for b in blocks if any(k in b for k in kws)]
    return strict or loose


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords", nargs="+")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--product", default="")
    ap.add_argument("--faq", action="store_true", help="只輸出問答段落")
    args = ap.parse_args()

    kws = [k for k in args.keywords if k.strip()]
    rows = load()
    if args.faq:
        rows = [r for r in rows if "答：" in r.get("text", "")]
    if args.product:
        rows = [r for r in rows if args.product in r.get("product", "")]

    res = [r for r in rows if hit(r, kws)]
    if not res and len(kws) > 1:
        res = [r for r in rows if any(k in r.get("title", "") or k in r.get("text", "") for k in kws)]
    res.sort(key=lambda r: -score(r, kws))

    show = min(args.limit, len(res))
    print("命中 %d 篇（顯示前 %d）\n" % (len(res), show))
    for r in res[:show]:
        cats = "／".join(r["category_path"][2:] or r["category_path"][-1:])
        print("■ %s  [%s／%s]" % (r["title"], r["product"], cats))
        print("  " + r["url"])
        if args.faq:
            for b in faq_blocks(r["text"], kws)[:3]:
                print("  " + re.sub(r"\s+", " ", b).strip()[:400])
        else:
            print("  " + snippet(r["text"], kws))
        print()


if __name__ == "__main__":
    main()
