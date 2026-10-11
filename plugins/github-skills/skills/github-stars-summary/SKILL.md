---
name: github-stars-summary
description: Fetch someone's starred GitHub repositories with the gh CLI, then group them into themed categories with a short plain-language summary of each repo. Use this whenever the user asks about their GitHub stars or starred repos — e.g. "what have I starred", "organize/categorize/summarize my stars", "remind me what's in my starred list", "which of my starred repos are about X", "clean up my stars", or wants the same for another GitHub user's stars — even if they don't say "categorize".
category: GitHub
tags:
  - github
  - stars
  - gh-cli
allowed-tools:
  - Read
  - Grep
  - Glob
---

# GitHub Stars Summary

Turn a starred-repo list into something a person can actually skim: themed groups, one honest line per repo, and a note on anything stale.

## Step 1: Fetch the stars

Run the bundled script with Python. `<this-skill-dir>` is the base directory shown when this skill loads. Both scripts work the same from Bash and PowerShell.

```bash
python <this-skill-dir>/scripts/fetch_stars.py            # the logged-in user's stars
python <this-skill-dir>/scripts/fetch_stars.py --user NAME # another user's public stars
```

Use the script rather than hand-writing a `gh api ... --jq` command. It paginates, asks GitHub for the `starred_at` date, works out how long since each repo was last pushed, and calls `gh` without a shell in between. That matters on Windows: PowerShell 5.1 strips double quotes inside arguments passed to native programs, which breaks jq string expressions.

Output is one line per repo, most recently starred first:

```
full_name | stars | language | starred_at | topics | flags | description
```

`flags` marks `ARCHIVED`, `no pushes in Ny` (over two years idle), `quiet Nmo` (6–24 months idle), and `fork`. Add `--json PATH` if you need the full records (URLs, exact dates) for a follow-up.

**If it fails:** "gh CLI not found" means the user needs to install GitHub CLI. An auth error means they need to run `gh auth login`; suggest they type `! gh auth login` so it runs in their session. Don't try to work around a missing login.

## Step 2: Understand the repos

Most descriptions are enough to write a summary from. For repos with no description, or a description too vague to say what it does (e.g. just an install command like "pip install foo", or a one-word tagline), use the name, topics, and language. If it's still unclear, fetch the README for up to about 5 of these (several repos can go in one call):

```bash
python <this-skill-dir>/scripts/repo_info.py OWNER/NAME [OWNER/NAME ...] --readme 40
```

If you still can't tell, say so in the summary ("no description; small Go project, purpose unclear") rather than guessing confidently.

**When the user asks about abandoned, dead, or stale stars**, push dates alone don't tell the full story. A finished demo or personal project is supposed to stop changing, while a widely used library that has gone quiet may have been superseded by a fork or a rename. For each `quiet` or `no pushes` repo that isn't the user's own coursework, check a little further:

```bash
python <this-skill-dir>/scripts/repo_info.py OWNER/NAME [OWNER/NAME ...]            # archived, last push, open issues, latest release
python <this-skill-dir>/scripts/repo_info.py OWNER/NAME --readme 40                 # same, plus the README's opening lines
```

`latest_release: none` just means the repo never published a release, which is normal. If the README or description points to a successor (a community fork or a rename), mention it as a replacement to star instead. Only name a successor you've actually seen evidence for.

## Step 3: Categorize

Build categories from what's actually in this list. Don't use a fixed taxonomy. Someone with 25 Kubernetes repos needs a finer split there ("Operators", "Local clusters", "Learning resources") than someone with two. Someone with one Haskell library doesn't need a "Haskell" category.

- Aim for roughly 4–10 categories. Use fewer for short lists, and split a category once it passes about 12 entries if there's a natural seam.
- Put each repo in exactly one category, the one a reader would look in first.
- Name categories by what the repos are *for* ("Game engines & graphics"), not by language unless language really is the theme.
- Repos owned by the user, or class/coursework repos (GitHub Classroom, a username in the repo name), usually belong together under something like "Personal & coursework".
- A small "Other" bucket is fine for true one-offs. Don't let it become the biggest group.

## Step 4: Write the report

Use this shape in the chat response:

```markdown
**<N> starred repos for <login>**, grouped into <K> categories.

## <Category name> (<count>)
- [owner/repo](https://github.com/owner/repo) (<stars>★): <one-line summary>
...

## Possibly inactive
<repos flagged archived / no pushes in 2y+, one line each, or omit the section if none. Mention notable `quiet` repos too when the user asked about staleness.>

## Overall
<1–3 sentences on what the collection says overall — dominant interests, overlapping repos worth comparing, anything notable.>
```

Give every section a `##` markdown header, including any extra section the request calls for (such as `## Likely duplicates`) and the closing `## Overall`. Bold text isn't enough, and a bare paragraph after a list reads as part of that list. Don't number the headers. The categories aren't a sequence, and numbers just add noise.

Guidance on the details:

- **Always link repos.** Every time a repo is listed, in a category, under Possibly inactive, or in any extra section, write its full name as a markdown link: `[owner/repo](https://github.com/owner/repo)`. The URL is always `https://github.com/` plus the full name, so it never needs looking up. The reader should be able to click straight through from any line. In the Overall prose, a short name is fine for a repo already linked above.
- **Summaries say what the thing does, in plain words.** Don't paste the description. Rewrite marketing copy ("The blazing-fast, next-generation platform for modern data teams…") into a neutral "what it is" ("columnar SQL database for analytics"). Aim for under about 15 words.
- **Order** categories largest first, and repos within a category by star count, highest first. Round stars to a readable form (298k, 4.7k, 21).
- **Point out overlaps** when several repos do the same job (three HTTP clients, four "awesome" lists on the same topic). That's often the most useful thing for someone deciding what to keep or try.
- **Counts must add up.** Take every number you state ("40 of your 120 are web frameworks") from your category tallies, and check that the category counts sum to the total. A wrong count makes readers doubt the rest of the report.
- **Stay scoped to the request.** If the user asked about a subset ("just the Python ones", "which are about databases"), report that subset, say how many of the total it covers, and skip the rest. If they asked about staleness, lead with the flags.
- **For very large lists** (more than about 150 repos), keep a line per repo only in small categories. For big ones, show the top ~10 by stars and summarize the remainder in a sentence ("…plus 34 more VS Code themes and extensions"). Offer the full list on request.

End with a brief offer of natural follow-ups, such as comparing overlapping repos, listing unstar candidates, or filtering by language. Keep it to one line.
