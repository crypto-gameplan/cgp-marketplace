# Third-party skills

These skills are based on skills from their authors' repositories and keep their MIT licenses (each skill folder has its `LICENSE`). They carry our own names so they fit the CGP framework and cannot clash with Claude Code's commands or other plugins. To update one, copy the original files again from a newer checked commit, repeat the changes below, and update the commit.

| Our skill | Based on | Source | Commit | License |
|---|---|---|---|---|
| `cgp-challenge` | `grilling` (and its shortcut `grill-me`) | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/productivity/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-agent-docs` | `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/productivity/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-test-first` | `tdd` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-research` | `research` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-architecture` | `codebase-design` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-review` | `code-review` | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/` | `24fe0ef` (release v1.3.1) | MIT, Copyright (c) 2026 Matt Pocock |
| `cgp-natural-writing` | `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) | `225a6f3` (v3.1.0) | MIT, Copyright (c) 2025 Siqi Chen |

`cgp-knowledge` is our own skill.

## Changes against the originals

- Every skill: `name` in the frontmatter is our name above.
- `cgp-challenge`: `grill-me` and `grilling` merged into one skill. It uses the body of `grilling` with a new description; `grill-me` was only a shortcut that called `grilling`. It can be started with `/cgp-challenge` or by asking to be challenged or grilled.
- `cgp-test-first`: points to `cgp-architecture` and `cgp-review` instead of `codebase-design` and `code-review`.
- `cgp-review`: the line telling the user to run `/setup-matt-pocock-skills` for the issue tracker now asks the agent to find the originating issue or spec, or to ask the user where it is.
- Beginner pass (0.6.0): the skills are used by people who are not professional programmers, so each now does the legwork itself, asks at most a few questions with a recommended answer, answers in the person's language and explains or avoids jargon.
  - `cgp-test-first`: rewritten around that. It no longer asks the user to confirm seams; it lists the behaviours to test in plain words, sets up a test runner when there is none, reports red-then-green proof and how to run the tests, and has a glossary. The reference files `tests.md` and `mocking.md` are unchanged.
  - `cgp-review`: rewritten. It picks the starting point and the spec itself (assuming the intent from commits when there is no spec), adds a third axis **Safety** with its own baseline, reports a verdict first and findings by severity in plain words, and offers to fix after a yes. The smell baseline moved to `references/baselines.md` and gained Fowler's Long Function.
  - `cgp-challenge`: at most four questions per round, design tree and frontier stay internal, pushback on real risks, and a closing summary (decided, assumed, open).
  - `cgp-research`: dated sources, confidence marking, a plain answer with a recommendation, and a default location for the findings.
  - `cgp-architecture` and `cgp-agent-docs`: a "Working with the person" section (plain words with the person, verify before writing down, short hand-over); the descriptions name more beginner triggers. The rest of the bodies is unchanged.
- `cgp-agent-docs/SKILL-MECHANICS.md`, `cgp-natural-writing/agents/openai.yaml`, `cgp-challenge/agents/openai.yaml`: the skill's own name in the text.
