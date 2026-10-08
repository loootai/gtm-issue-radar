# gtm-issue-radar

A weekly list of open GitHub issues where someone is stuck on a data API: Hunter, Apollo, SerpApi, Proxycurl, People Data Labs, email finders, remote MCP sign-in. It is a triage list. A human reads it and decides which issues, if any, deserve an answer.

It does not use an LLM, does not call looot, and does not post comments anywhere. It only reads GitHub search and writes a markdown file.

## How it works

1. `.github/workflows/radar.yml` runs every Monday (and on manual dispatch).
2. `radar.py` runs `gh search issues` once per line of `queries.txt`, for open issues updated in the last 7 days.
3. Repos listed in `exclude.txt` and pull requests are dropped.
4. Stars come from `gh api repos/<repo>`. Rows are sorted by stars.
5. The report is written to `reports/YYYY-MM-DD.md` and committed. Columns: repo, stars, issue, title, comments, updated, matched query.

The workflow uses the built-in `GITHUB_TOKEN`. `contents: write` is there only to commit the report.

## Run it locally

```bash
gh auth login
python3 radar.py
```

Python 3 standard library and the `gh` CLI. Edit `queries.txt` and `exclude.txt` to change what it looks for.

## Rules for whoever reads the list

Answer only if you can add something real: a working trace, a fix, a doc link that solves the problem. Mention looot only when the issue is about a data provider and looot fits, and say you work on it. Skip stale threads and never post the same text twice.

MIT. Maintained by [looot](https://looot.ai).
