---
name: cgp-research
description: Investigate a question against high-trust primary sources (official docs, source code, specs, first-party APIs), save the findings with a source for each claim as a Markdown file in the repo, and explain the answer in plain words. Use when the user wants a topic researched, wants to know which library, service or approach to use, needs docs or API facts gathered, asks "is this still current?", or wants reading legwork delegated to a background agent.
---

Many people using this are not professional programmers. They need a trustworthy answer they can act on, not a pile of links. Do the reading in a **background agent** so you keep working while it reads; tell the person it is running and roughly what it checks.

## The agent's job

1. **Primary sources first**: official docs, source code, specs, changelogs, first-party APIs and pricing pages, not a blog post about them. Follow every claim back to the source that owns it. When only secondary sources exist, say so.
2. **Current**: note the date or version each fact belongs to. Libraries, prices, limits and APIs change; a fact without a date is a guess. Prefer the newest stable release and mention what changed recently if it matters.
3. **Honest about doubt**: mark claims as confirmed (source says so), likely (inferred) or unknown, and name conflicts between sources.
4. **Write the findings** to one Markdown file, starting with the answer in plain words (three to five sentences, in the language the person wrote in, with its real characters such as ä, ö, ü, ß), then the details, each claim with its source link and date. Explain unavoidable technical terms in a few words the first time.
5. **Save it** where the repo already keeps such notes (`docs/`, `notes/`, `research/`); match the convention. If there is none, use `docs/research/<topic>.md`. Without a project, keep it in the answer.

## Tell the person

In their language, short. The person reads this reply, not the file, so every term that decides their choice (async, webhook, rate limit) gets its few plain words here too:

- **The answer** and, when they asked which option to pick, **your recommendation** with the one or two reasons that decide it for them.
- **How sure** it is and anything that could change it (a beta API, a price that changes monthly).
- **Where the file is**, so they or the next session can read the sources.
