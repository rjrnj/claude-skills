#!/usr/bin/env python3
"""Fetch a GitHub user's starred repositories via the gh CLI.

Prints one compact line per repo (most recently starred first) so the list is
cheap to read, and optionally saves the full records as JSON.

Calls gh through subprocess with an argument list, so no shell quoting is
involved -- this avoids the Windows PowerShell 5.1 bug where embedded double
quotes in a --jq expression get stripped.

Usage:
    python fetch_stars.py                 # the authenticated user's stars
    python fetch_stars.py --user octocat  # someone else's public stars
    python fetch_stars.py --json stars.json
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone

STALE_DAYS = 730  # no pushes in ~2 years => flag as possibly inactive
QUIET_DAYS = 180  # no pushes in ~6 months => worth a closer look


def run_gh(args):
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout


def fetch(user):
    endpoint = f"users/{user}/starred" if user else "user/starred"
    out = run_gh([
        "api", f"{endpoint}?per_page=100", "--paginate",
        # star+json adds starred_at; each item is {starred_at, repo}
        "-H", "Accept: application/vnd.github.star+json",
        "--jq", ".[]",
    ])
    now = datetime.now(timezone.utc)
    repos = []
    for line in out.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        r = item["repo"]
        pushed = r.get("pushed_at")
        days_since_push = None
        if pushed:
            days_since_push = (now - datetime.fromisoformat(pushed.replace("Z", "+00:00"))).days
        repos.append({
            "full_name": r["full_name"],
            "description": (r.get("description") or "").strip(),
            "language": r.get("language"),
            "topics": r.get("topics") or [],
            "stars": r.get("stargazers_count", 0),
            "url": r.get("html_url"),
            "homepage": r.get("homepage") or None,
            "starred_at": item.get("starred_at"),
            "pushed_at": pushed,
            "days_since_push": days_since_push,
            "archived": r.get("archived", False),
            "fork": r.get("fork", False),
            "owner": r["owner"]["login"],
        })
    return repos


def compact_line(r):
    flags = []
    if r["archived"]:
        flags.append("ARCHIVED")
    elif r["days_since_push"] is not None and r["days_since_push"] > STALE_DAYS:
        flags.append(f"no pushes in {r['days_since_push'] // 365}y")
    elif r["days_since_push"] is not None and r["days_since_push"] > QUIET_DAYS:
        flags.append(f"quiet {r['days_since_push'] // 30}mo")
    if r["fork"]:
        flags.append("fork")
    parts = [
        r["full_name"],
        f"{r['stars']}★",
        r["language"] or "-",
        (r["starred_at"] or "")[:10],
        ",".join(r["topics"][:6]) or "-",
        "; ".join(flags) or "-",
        r["description"] or "(no description)",
    ]
    return " | ".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--user", help="GitHub login to fetch (default: authenticated user)")
    ap.add_argument("--json", metavar="PATH", help="also write full records to this JSON file")
    args = ap.parse_args()

    if not shutil.which("gh"):
        sys.exit("gh CLI not found on PATH. Install it from https://cli.github.com and run `gh auth login`.")

    login = args.user or run_gh(["api", "user", "--jq", ".login"]).strip()
    repos = fetch(args.user)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"user": login, "count": len(repos), "repos": repos}, f, indent=2)

    # Force UTF-8 so the ★ and non-ASCII descriptions survive a Windows console.
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"# {len(repos)} starred repos for {login} (most recently starred first)")
    print("# full_name | stars | language | starred_at | topics | flags | description")
    for r in repos:
        print(compact_line(r))


if __name__ == "__main__":
    main()
