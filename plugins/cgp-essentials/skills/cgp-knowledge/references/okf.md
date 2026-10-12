# Open Knowledge Format (OKF) v0.2

Source: the specification in [GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) (Apache-2.0). This file summarises v0.2; if the repo shows a newer version, read its SPEC.md and tell the person what changed.

OKF is a format, not software. The repo also has a reference agent that builds bundles from BigQuery with Gemini; it is a proof of concept and not needed to use the format.

## Contents

- [The format](#the-format)
- [Trust, provenance and freshness](#trust-provenance-and-freshness)
- [Setting up a bundle in a project](#setting-up-a-bundle-in-a-project)
- [How agents use the bundle](#how-agents-use-the-bundle)
- [Keeping it healthy](#keeping-it-healthy)

## The format

A **bundle** is a directory of markdown files, usually in git:

```
knowledge/
  index.md          optional; lists the folder's contents, may carry okf_version
  log.md            optional; dated change history, newest first
  <concept>.md      one concept per file
  <folder>/
    index.md
    <concept>.md
```

`index.md` and `log.md` are reserved names. Every other `.md` file is a **concept**: YAML frontmatter, then a markdown body.

```markdown
---
type: Exchange Account            # the only required key
title: Kraken main account
description: Spot account used for the long-term portfolio.
resource: https://www.kraken.com  # the thing described, if there is one
tags: [exchange, portfolio]
---

# Rules

- Only spot positions; no margin.
- Withdrawals go to the hardware wallet described in [cold storage](/custody/cold-storage.md).
```

- `type` is free text; choose short, self-explanatory names and reuse them consistently (`Playbook`, `Metric`, `API Endpoint`, `Database Table`, `Decision`).
- Recommended: `title`, `description` (one sentence, used by indexes and search), `resource`, `tags`. Any extra keys are allowed.
- Body: favour structure (headings, lists, tables, code blocks). Conventional headings: `# Schema`, `# Examples`, `# Computation`.
- Links between concepts are normal markdown links; bundle-relative paths starting with `/` are recommended. The link means "related"; the sentence around it says how. Broken links are allowed and can stand for knowledge not written yet.
- A `references/` folder conventionally mirrors external material the bundle relies on.

Conformance is small: every concept has parseable frontmatter with a non-empty `type`, and `index.md` / `log.md` follow their shapes. Consumers must accept unknown types and keys, missing optional fields, broken links and missing indexes.

### index.md

No frontmatter, except an optional `okf_version: "0.2"` in the bundle's root `index.md`. Sections of links with one-line descriptions:

```markdown
# Playbooks

* [Rebalancing](rebalancing.md) - Monthly rebalancing steps and limits
* [Custody](custody/) - Where funds are held and how they move
```

### log.md

```markdown
# Directory Update Log

## 2026-10-12
* **Creation**: Added [Rebalancing](/playbooks/rebalancing.md).
```

Dates as `YYYY-MM-DD`, newest first.

## Trust, provenance and freshness

All optional. Use them when agents write concepts or when outdated knowledge does harm.

```yaml
sources:
  - id: fee-schedule                 # cite it in the body as [^fee-schedule]
    resource: https://www.kraken.com/features/fee-schedule
    title: Kraken fee schedule
    last_modified: 2026-09-01T00:00:00Z
generated: { by: claude-code/opus-5.5, at: 2026-10-12T09:00:00Z }
verified:
  - { by: human:fabian, at: 2026-10-12T10:00:00Z }
status: stable                       # draft | stable | deprecated; absent means stable
stale_after: 2027-01-12T00:00:00Z    # stale on or after this instant
```

- **Actors**: `<tool>/<version>` for agents, `human:<id>` for people, `process:<id>` for automated jobs. Use `human:` for anything a person wrote or confirmed.
- **Trust tier**, derived by readers: no `verified` means unverified; only non-human verifiers mean machine-confirmed; any `human:` verifier means human-reviewed.
- `generated.at` is when the content last changed meaningfully; `verified[].at` is when someone last confirmed it. They are independent.
- Timestamps are ISO 8601 with an explicit offset (`Z`).
- Attribute single claims with footnotes keyed by `sources[].id`, so reordering sources does not break attribution.

**Facts that age at different speeds.** `verified` and `stale_after` cover the whole concept. When one concept holds facts that go out of date at different rates (a rate limit that changes yearly, a fee that changes monthly), add a `# Facts` table in the body with a row per fact: the value (or `unknown`), the source id, and when it was last checked. Keep the frontmatter honest: the concept's `verified` and `stale_after` follow its weakest important fact. This is an extension within the body, so every OKF reader still accepts it.

```markdown
# Facts

| Fact | Value | Source | Checked |
|---|---|---|---|
| Rate limit (free tier) | 30 calls/min | [^coingecko-docs] | 2026-10-12 |
| Data delay | unknown | | |
```

OKF also defines **Attested Computation** concepts (a sanctioned way to compute a value, with an executor and an attester). Mention them only when the person needs agents to compute official numbers the same way every time; then read §10 of the spec.

## Setting up a bundle in a project

1. **Place it.** A `knowledge/` folder at the repo root unless the project has a better home. One bundle per project is usually enough; split only when parts have different owners.
2. **Copy the starter files** from `assets/okf-bundle/` (root `index.md` with `okf_version`, `log.md`, a concept template). Replace the examples.
3. **Choose folders by how people look things up**, not by file type: `systems/`, `data/`, `playbooks/`, `decisions/`, `people/` are common. Give each folder an `index.md`.
4. **Pick a small set of `type` values** and write them into the root `index.md` under a short "Types" section so every author uses the same ones.
5. **Seed it with real concepts**: start with the five to ten things agents most often get wrong or ask about. Convert existing docs rather than writing from scratch; record their origin in `sources`.
6. **Point the agent at it**: one line in `AGENTS.md` / `CLAUDE.md`, for example: "Project knowledge is an OKF bundle in `knowledge/`. Start at `knowledge/index.md` and follow the indexes; prefer human-reviewed concepts and say when one is stale or deprecated. When you add or change a concept, update `generated`, the folder's `index.md` and `log.md`."
7. **Check it**: `python3 <skill-dir>/scripts/check_okf.py knowledge/`. Optionally copy the script into the repo and run it in CI.

## How agents use the bundle

- **Read**: start at the root `index.md`, descend into the folder that matches the question, open only the concepts needed. Read `status`, `stale_after` and the trust tier before relying on a concept, and mention them when they weaken the answer.
- **Write**: one concept per file; set `generated` to the agent's own actor and time; add `sources` for what it read; leave `verified` to people or checks; update the folder's `index.md` and the `log.md`. New or uncertain concepts start as `status: draft`.
- **Review**: people confirm drafts by adding a `verified` entry with their `human:` actor and changing `status` to `stable`. Reviews fit naturally into pull requests.

## Keeping it healthy

- Run the checker after every batch of changes.
- Look for concepts past `stale_after` and re-verify or deprecate them; deprecate instead of deleting so links keep working.
- When navigation gets slow (more than a few hundred concepts in one folder, or the agent reads many files to answer one question), add search over the bundle; see rung 4 in [options.md](options.md#4-search-over-curated-files).
