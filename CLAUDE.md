# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code plugin marketplace (`rjrnj-skills`) of personal skills. No build, lint, or test tooling, and no code: the content is JSON manifests and Markdown skill files.

## Layout and how the pieces connect

- `.claude-plugin/marketplace.json`: the marketplace manifest. Each entry in `plugins` points at a plugin directory through `source` (relative path).
- `plugins/<plugin>/.claude-plugin/plugin.json`: the plugin manifest (name, description, version, author).
- `plugins/<plugin>/skills/<skill>/SKILL.md`: one directory per skill. Skills are found by directory convention, so they are not listed in either manifest.

Currently there are two plugins:

- `basic-skills`, with one skill, `commit`. Its description also mentions PR creation, code review, branch cleanup, and release notes, which are planned skills that don't exist yet.
- `github-skills`, with one skill, `github-stars-summary`. It bundles Python helper scripts under `scripts/` that call `gh` through `subprocess`, so the skill works the same from Bash and PowerShell. It requires Python 3 and an authenticated `gh` CLI.

When adding or changing things:

- A new plugin needs its own directory with `.claude-plugin/plugin.json` **and** an entry in `marketplace.json`. Keep the plugin's `description` the same in both files.
- Bump `version` in `plugin.json` when a plugin's skills change, because installed copies update by version.

## Skill conventions (from `commit/SKILL.md`)

- Frontmatter: `name`, `description` (says what the skill does and lists trigger phrases like "Use when the user says ..."), optional `argument-hint`, `category`, `tags`, and `allowed-tools`.
- Skills are written to work in both Bash and PowerShell, so `allowed-tools` lists each permitted command twice, as `Bash(...)` and as `PowerShell(...)`. The skill body also avoids shell-specific quoting (for example, commit messages go through a file with `git commit -F`, never `-m`).
- `allowed-tools` holds only read-only or low-risk commands. Anything that changes state, like `git commit`, is left out so it prompts for permission, and the skill also asks the user to approve before doing it.
- The body is a numbered workflow, followed by sections for format rules, edge cases (for example, pre-commit hook failures), and an explicit "Out of scope" list.

## Testing changes locally

There is no automated test. To check a change:

- `claude plugin validate .` validates the marketplace and plugin manifests.
- To try skills, add this directory as a marketplace in Claude Code (`/plugin marketplace add <path-to-repo>`), then install `basic-skills@rjrnj-skills` or `github-skills@rjrnj-skills`.
