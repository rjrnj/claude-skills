# claude-skills

Personal Claude Code skills, published as the `rjrnj-skills` plugin marketplace.

## Install

In Claude Code:

1. Add the marketplace:

   ```
   /plugin marketplace add rjrnj/claude-skills
   ```

2. Install the plugins you want:

   ```
   /plugin install basic-skills@rjrnj-skills
   /plugin install github-skills@rjrnj-skills
   ```

   | Plugin | Skills | Needs |
   |---|---|---|
   | `basic-skills` | `commit` | git |
   | `github-skills` | `github-stars-summary` | Python 3, an authenticated `gh` CLI |

3. Restart Claude Code if the skills don't show up.

To get updates later, run `/plugin marketplace update rjrnj-skills`.
