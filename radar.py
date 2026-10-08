#!/usr/bin/env python3
"""Write a markdown triage list of recently updated open GitHub issues.

Reads queries.txt and exclude.txt, calls `gh search issues` and `gh api`
(read only), and writes reports/YYYY-MM-DD.md. No LLM, no comments posted.
"""
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DAYS = 7
LIMIT = 30


def read_lines(name):
    path = ROOT / name
    if not path.exists():
        return []
    lines = [l.strip() for l in path.read_text().splitlines()]
    return [l for l in lines if l and not l.startswith("#")]


def gh(*args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write(f"gh {' '.join(args[:2])} failed: {out.stderr.strip()}\n")
        return None
    return json.loads(out.stdout)


def main():
    today = datetime.date.today()
    since = (today - datetime.timedelta(days=DAYS)).isoformat()
    exclude = {e.lower() for e in read_lines("exclude.txt")}
    queries = read_lines("queries.txt")
    found = {}
    for q in queries:
        rows = gh(
            "search", "issues", q,
            "--state", "open", "--updated", f">={since}",
            "--sort", "updated", "--limit", str(LIMIT),
            "--json", "repository,number,title,url,commentsCount,updatedAt,isPullRequest",
        )
        for r in rows or []:
            repo = r["repository"]["nameWithOwner"]
            if repo.lower() in exclude or r.get("isPullRequest"):
                continue
            row = found.setdefault(r["url"], {**r, "repo": repo, "queries": []})
            row["queries"].append(q)
    stars = {}
    for row in found.values():
        repo = row["repo"]
        if repo not in stars:
            info = gh("api", f"repos/{repo}")
            stars[repo] = info["stargazers_count"] if info else -1
        row["stars"] = stars[repo]
    ordered = sorted(found.values(), key=lambda r: r["stars"], reverse=True)

    lines = [
        f"# Issue radar {today.isoformat()}",
        "",
        f"Open issues updated since {since}, matching {len(queries)} queries. Sorted by repo stars. A human decides which to answer.",
        "",
        "| Repo | Stars | Issue | Title | Comments | Updated | Matched |",
        "| --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for r in ordered:
        title = r["title"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {r['repo']} | {r['stars']} | [#{r['number']}]({r['url']}) | {title} "
            f"| {r['commentsCount']} | {r['updatedAt'][:10]} | {'; '.join(r['queries'])} |"
        )
    if not ordered:
        lines.append("| none | | | | | | |")
    (ROOT / "reports").mkdir(exist_ok=True)
    out = ROOT / "reports" / f"{today.isoformat()}.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out} ({len(ordered)} issues)")


if __name__ == "__main__":
    main()
