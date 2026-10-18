#!/usr/bin/env python3
"""Search Reddit and export posts (and optionally their comments) to CSV
using the ProLevelMax REST API. Standard library only.

Usage:
  export PROLEVELMAX_KEY=sk_procli_...
  python reddit_to_csv.py "notion vs obsidian" --time week --comments 5
"""
import argparse, csv, json, os, sys, time, urllib.request, urllib.error

API = "https://prolevelmax.com/v1/run"


def run(scraper, inp, key, retries=3):
    body = json.dumps({"scraper": scraper, "input": inp}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")
            if e.code < 500:
                sys.exit(f"API error {e.code}: {msg}")
        except urllib.error.URLError:
            pass
        time.sleep(2 * (attempt + 1))
    sys.exit("API unreachable after retries")


def search_posts(query, time_range, sort, key):
    q = query if query.startswith('"') else f'"{query}"'
    res = run("procli_reddit_d", {"query": q, "search_type": "post", "sort": sort,
                                  "time_range": time_range, "need_format": True}, key)
    cost = (res.get("cost") or {})
    rows = []
    items = res.get("items") or []
    # Results come either as a flat list of {"post": ...} or nested under items[0]["children"]
    if items and "children" in items[0]:
        items = items[0]["children"]
    for child in items:
        p = child.get("post") or {}
        sub = p.get("subreddit")
        sub = sub.get("name") if isinstance(sub, dict) else sub
        rows.append({
            "id": p.get("id"), "subreddit": sub, "title": p.get("postTitle"),
            "score": p.get("score"), "comments": p.get("commentCount"),
            "created_at": p.get("createdAt"),
            "url": "https://www.reddit.com" + (p.get("permalink") or ""),
        })
    return rows, cost


def post_comments(post_id, key, sort="TOP"):
    pid = post_id if post_id.startswith("t3_") else "t3_" + post_id
    res = run("procli_reddit_b", {"post_id": pid, "sort_type": sort}, key)
    out = []
    items = res.get("items") or []
    # Comments come either as a flat list of trees or nested under postInfoById
    if items and "postInfoById" in items[0]:
        items = (items[0]["postInfoById"].get("commentForest") or {}).get("trees", [])
    trees = items
    for t in trees:
        n = t.get("node") or {}
        if not n.get("content"):
            continue
        out.append({
            "post_id": pid, "comment_id": n.get("id"), "depth": t.get("depth"),
            "author": (n.get("authorInfo") or {}).get("name"), "score": n.get("score"),
            "created_at": n.get("createdAt"),
            "text": (n.get("content") or {}).get("markdown", "").replace("\r", ""),
            "url": "https://www.reddit.com" + (n.get("permalink") or ""),
        })
    return out


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", help="search phrase; wrapped in quotes for exact match")
    ap.add_argument("--time", default="week", choices=["hour", "day", "week", "month", "year", "all"])
    ap.add_argument("--sort", default="NEW", choices=["NEW", "TOP", "HOT", "RELEVANCE", "COMMENTS"])
    ap.add_argument("--comments", type=int, default=0, help="also fetch comments for the top N posts")
    ap.add_argument("--out", default="reddit")
    a = ap.parse_args()
    key = os.environ.get("PROLEVELMAX_KEY") or sys.exit("Set PROLEVELMAX_KEY first")

    posts, cost = search_posts(a.query, a.time, a.sort, key)
    write_csv(a.out + "_posts.csv", posts)
    print(f"{len(posts)} posts -> {a.out}_posts.csv")

    if a.comments:
        top = sorted(posts, key=lambda p: p.get("comments") or 0, reverse=True)[: a.comments]
        allc = []
        for p in top:
            allc += post_comments(p["id"], key)
            time.sleep(1)
        write_csv(a.out + "_comments.csv", allc)
        print(f"{len(allc)} comments from {len(top)} posts -> {a.out}_comments.csv")


if __name__ == "__main__":
    main()
