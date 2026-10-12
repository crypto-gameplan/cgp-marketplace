# Third-party skills

These skills come from their authors' repositories and keep their MIT licenses (each skill folder has its `LICENSE`). They are renamed with a `cgp-` prefix so they cannot clash with Claude Code's own commands or other plugins. Apart from the renaming, the files are unchanged except where noted. To update one, copy the files again from a newer checked commit, repeat the changes below, and update the commit.

| Skill | Original name | Source | Commit | License |
|---|---|---|---|---|
| `cgp-grill-me`, `cgp-grilling` | `grill-me`, `grilling` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/productivity/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-writing-for-agents` | `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/productivity/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-tdd`, `cgp-research`, `cgp-codebase-design`, `cgp-code-review` | `tdd`, `research`, `codebase-design`, `code-review` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-humanizer` | `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) | `225a6f3` (v3.1.0) | MIT, Copyright (c) 2025 Siqi Chen |

## Changes

- Every skill: `name` in the frontmatter carries the `cgp-` prefix.
- `cgp-grill-me`: calls `cgp-grilling` instead of `grilling`.
- `cgp-tdd`: points to `cgp-codebase-design` and `cgp-code-review` instead of `codebase-design` and `code-review`.
- `cgp-code-review`: the line telling the user to run `/setup-matt-pocock-skills` for the issue tracker now asks the agent to find the originating issue or spec, or to ask the user where it is.
- `cgp-writing-for-agents/SKILL-MECHANICS.md`, `cgp-humanizer/agents/openai.yaml`: the skill's own name in the text.
