---
name: commit
description: Create git commits with Conventional Commit messages, or with the repo's own commit style when --match-history is passed. Use when the user asks to commit, says "commit this" or "commit these changes", or wants a commit message written for the current changes.
argument-hint: "[--match-history]"
category: Git
tags:
  - git
  - conventional-commits
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(git add:*)
  - PowerShell(git status:*)
  - PowerShell(git diff:*)
  - PowerShell(git log:*)
  - PowerShell(git show:*)
  - PowerShell(git add:*)
---

# Commit

By default, every commit message follows Conventional Commits, regardless of the repo's existing history. If the invocation includes `--match-history`, or the user asks to match the repo's existing commit style, follow the "Matching repo history" section instead of the Conventional Commits format.

## Workflow

1. Run `git status` and `git diff` (plus `git diff --staged`) to see everything that changed. Read new untracked files directly, since `git diff` doesn't show them.
2. Decide what goes in the commit, without staging anything yet:
   - If files are already staged, commit exactly the staged set. Mention unstaged changes but do not add them.
   - If nothing is staged, choose the files to commit by name.
   - If the changes serve more than one purpose, propose splitting them into one commit per purpose and list the files for each.
3. Write the message: Conventional Commits by default, or the repo's own style with `--match-history`.
4. Show the proposed message and the list of files to be committed, then wait for the user's approval.
5. Only after approval, stage the chosen files by name (never `git add -A` or `git add .`) and run `git commit`. If the user rejects the proposal, nothing has been staged, so there is nothing to undo.
6. Report the result with `git log -1 --oneline`.

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
  2. Run `git commit -F <file>`.
  3. If the commit fails (for example, a pre-commit hook rejects it), reuse the same file for the retry.
  4. Leave the file in place afterwards. Don't delete it: the next commit overwrites it, so only one copy ever exists.

## Never commit

- Secrets: `.env` files, keys, tokens, credential files. If one is in the diff, stop and tell the user.
- Build output, dependency folders, or other generated files, unless the repo already tracks them.
- Large binaries, without flagging them to the user first.

## When a pre-commit hook fails

The commit did not happen. What to do depends on what the hook did:

- **It only reformatted files** (a formatter or auto-fixer rewrote them): stage the reformatted versions of the files already in the commit, and nothing else. Retry the commit, and tell the user which files the hook reformatted.
- **It reported a problem** (a lint error, a failing test, a detected secret): do not edit any code yet. Show the user the hook's output and propose a fix, then wait for approval. After the fix is approved and made, show the updated file list and get approval again before committing.

Never use `--no-verify`, and never `--amend` to recover, since amending would rewrite the previous commit.

## Out of scope

Do not push, amend, rebase, reset, or force anything unless the user asks for it explicitly.
