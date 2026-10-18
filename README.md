# reddit-to-csv

Search Reddit and export posts and comment threads to CSV in one command, using the [ProLevelMax](https://prolevelmax.com) API. No Reddit API key, no OAuth app, no dependencies beyond Python 3.8+.

Useful now that Reddit RSS feeds are switching off on **13 November 2026**: anything that read Reddit through RSS can read it through this instead.

## Setup

1. Create a ProLevelMax account at [prolevelmax.com](https://prolevelmax.com). New accounts get $1 of free credit after verifying their email.
2. Create an API key in the dashboard (set a daily spend limit while you're there).
3. Export it:

```bash
export PROLEVELMAX_KEY=sk_procli_...
```

## Usage

```bash
# Posts mentioning a phrase in the past week, newest first
python reddit_to_csv.py "notion vs obsidian"

# Past month, plus full comment threads for the 5 most-discussed posts
python reddit_to_csv.py "standing desk" --time month --comments 5 --out desks
```

Output:

| File | Columns |
|---|---|
| `<out>_posts.csv` | id, subreddit, title, score, comments, created_at, url |
| `<out>_comments.csv` | post_id, comment_id, depth, author, score, created_at, text, url |

Feed the CSV to Claude or ChatGPT and ask it to group complaints, feature requests or arguments.

## Cost

Each search call and each comment page is billed per call from your prepaid ProLevelMax balance (Reddit calls start at $0.003). Use `POST /v1/inspect` to get a quote before running anything large.

## Use it from an AI client instead

Skip the script: send this one line to Claude, Claude Code, Codex or Cursor, open the link it returns and click Allow.

```
set up https://prolevelmax.com/SKILL.md
```

Then ask in plain language, for example "pull the comments on this Reddit thread and group the complaints". In ChatGPT, add `https://prolevelmax.com/mcp` as a custom MCP server instead. The same account covers 150+ platforms, including TikTok, YouTube, Instagram, Xiaohongshu and Douyin.

## License

MIT
