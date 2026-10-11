#!/usr/bin/env python3
"""Show activity details and the start of the README for GitHub repos.

Covers the follow-up lookups the skill needs after fetch_stars.py: whether a
repo is archived, when it was last pushed, its open-issue count, its latest
release, and the first lines of its README. Runs gh through subprocess, so it
behaves the same from Bash and PowerShell (no `head`, no shell quoting).

Usage:
    python repo_info.py OWNER/NAME [OWNER/NAME ...]
    python repo_info.py OWNER/NAME --readme 40   # also print 40 README lines
"""
import argparse
import json
import shutil
import subprocess
import sys


def gh(args):
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8"
    )
    return result.returncode, result.stdout, result.stderr.strip()


def info(repo, readme_lines):
    code, out, err = gh(["api", f"repos/{repo}"])
    if code != 0:
        print(f"== {repo}\n  error: {err}")
        return
    r = json.loads(out)
    print(f"== {repo}")
    print(f"  archived: {r.get('archived', False)}")
    print(f"  pushed_at: {r.get('pushed_at')}")
    print(f"  open_issues: {r.get('open_issues_count')}  (includes open PRs)")

    # 404 here just means the repo has never published a release.
    code, out, _ = gh(["api", f"repos/{repo}/releases/latest"])
    if code == 0:
        rel = json.loads(out)
        print(f"  latest_release: {rel.get('tag_name')} ({(rel.get('published_at') or '')[:10]})")
    else:
        print("  latest_release: none")

    if readme_lines:
        code, out, _ = gh(["api", f"repos/{repo}/readme", "-H", "Accept: application/vnd.github.raw"])
        print("  readme:")
        if code != 0:
            print("    (no README)")
        else:
            for line in out.splitlines()[:readme_lines]:
                print(f"    {line}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repos", nargs="+", metavar="OWNER/NAME")
    ap.add_argument("--readme", type=int, default=0, metavar="N",
                    help="also print the first N lines of each README")
    args = ap.parse_args()

    if not shutil.which("gh"):
        sys.exit("gh CLI not found on PATH. Install it from https://cli.github.com and run `gh auth login`.")

    sys.stdout.reconfigure(encoding="utf-8")
    for repo in args.repos:
        info(repo, args.readme)


if __name__ == "__main__":
    main()
