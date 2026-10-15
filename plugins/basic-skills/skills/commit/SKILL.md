---
name: commit
description: Create git commits with Conventional Commit messages, or with the repo's own commit style when --match-history is passed. Use when the user asks to commit, says "commit this" or "commit these changes", or wants the current changes committed.
argument-hint: "[--match-history]"
category: Git
tags:
  - git
  - conventional-commits
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - PowerShell(git status:*)
  - PowerShell(git diff:*)
  - PowerShell(git log:*)
  - PowerShell(git show:*)
  - PowerShell(git add:*)
  - PowerShell(git commit:*)
---

# Commit

This skill makes the commit. Invoking it is the user's approval: do not show a proposal and wait for a "yes" before committing. Work through the steps below in one turn and finish with the commit made.

By default, every commit message follows Conventional Commits, regardless of the repo's existing history. If the invocation includes `--match-history`, or the user asks to match the repo's existing commit style, follow the "Matching repo history" section instead of the Conventional Commits format.

## Workflow

1. Run `git status` and `git diff` (plus `git diff --staged`) to see everything that changed. Read new untracked files directly, since `git diff` doesn't show them.
2. Decide what goes in each commit. Every change in the working tree gets committed, staged or not: the index is not a signal of what the user wants, so treat staged and unstaged changes as one pool.
   - If all the changes serve one purpose, make one commit with every changed file.
   - If they serve more than one purpose, make one commit per purpose, in sequence. Group files by purpose, not by whether they happened to be staged.
3. Check the files against the "Never commit" section. A secret stops the whole run. Other excluded files are left out, and the rest is still committed.
4. Write the message: Conventional Commits by default, or the repo's own style with `--match-history`.
5. Stage that commit's files by name (never `git add -A` or `git add .`).
6. Commit those same files, following the "Every message" section. Repeat steps 4 to 6 for each remaining commit.
7. Report: the output of `git log -n <number of commits made> --stat`, so the user sees each hash, message, and the files that went in. If any file was left uncommitted (see "Never commit"), list it with a short reason.

## Message format (default)

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type** is one of: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- **scope** is optional: a short lowercase noun for the area touched (`feat(auth): ...`). Leave it out rather than invent a vague one.
- **subject** is imperative mood ("add", not "added" or "adds"), starts lowercase, has no trailing period, and keeps the whole header line at 72 characters or fewer.
- **body** is included when the reason for the change isn't obvious from the subject. Explain why, not what. Wrap at 72 characters.
- **Breaking changes:** add `!` after the type or scope (`feat(api)!: ...`) and a `BREAKING CHANGE: <what breaks and how to migrate>` footer.
- **Issue references** go in the footer: `Closes #12`, `Refs #34`.

## Matching repo history (`--match-history`)

1. Read recent history with `git log --no-merges -n 30 --format="%s%n%b%n---"`.
2. Work out the style from it: whether subjects use a prefix or type, capitalization, tense, typical subject length, whether bodies are used and how they're wrapped, and how issues are referenced.
3. Write the message in that style, and tell the user in one line what style you matched (for example, "matched: capitalized imperative subject, no prefix, no body").
4. Ignore suffixes like `(#12)` that GitHub adds to squash-merged pull requests. They come from the merge, so don't copy them into a local commit.
5. If the repo has fewer than 5 non-merge commits, or no consistent style, fall back to Conventional Commits and say so.

## Every message

- Always pass the message through a file, even a one-line message. Never use `git commit -m`. Shell quoting can mangle line breaks, `$`, backticks, and double quotes, and the rules differ between Bash and PowerShell.
  1. Write the message to a file named `commit-msg.txt` outside the working tree: in your scratchpad directory if you have one, otherwise in the system temp directory. Overwrite it if it already exists, reading it first if your file-writing tool refuses to overwrite a file it hasn't read. Never put it inside the repo, where it could be staged.
  2. Run `git commit -F <file> -- <the files for this commit>`, naming the files explicitly. With paths given, git commits only those files, so anything else that happens to be staged stays staged for a later commit instead of being swept into this one.
  3. If the commit fails (for example, a pre-commit hook rejects it), reuse the same file for the retry.
  4. Leave the file in place afterwards. Don't delete it: the next commit overwrites it, so only one copy ever exists.

## Never commit

- Secrets: `.env` files, keys, tokens, credential files. If one is in the diff, stop and tell the user.
- Build output, dependency folders, or other generated files, unless the repo already tracks them. Leave them out and say so in the report.
- Large binaries. Leave them out, commit the rest, and tell the user so they can decide.

## When a pre-commit hook fails

The commit did not happen. What to do depends on what the hook did:

- **It only reformatted files** (a formatter or auto-fixer rewrote them): stage the reformatted versions of the files already in the commit, and nothing else. Retry the commit, and tell the user which files the hook reformatted.
- **It reported a problem** (a lint error, a failing test, a detected secret): do not edit any code. Fixing code is outside this skill. Show the user the hook's output, say which files are staged, and stop. The user can fix the problem and run the skill again.

Never use `--no-verify`, and never `--amend` to recover, since amending would rewrite the previous commit.

## Out of scope

Never push. Do not amend, rebase, reset, or force anything unless the user asks for it explicitly.
