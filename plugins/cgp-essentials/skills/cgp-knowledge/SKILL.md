---
name: cgp-knowledge
description: Decide how an agent should get a project's knowledge (nothing extra, CLAUDE.md/AGENTS.md and skills, an Open Knowledge Format (OKF) bundle, RAG, a database behind a tool, or a mix), then set it up. Use when someone asks whether they need RAG, a vector database, embeddings, OKF, a knowledge base or agent memory, or how to give Claude or Codex their docs, notes, data or company knowledge, even if they never name a technique.
---

Help the person pick the **smallest rung** that serves their knowledge, then build it with them. The ladder, lowest first:

1. **Nothing extra**: the agent reads the files it needs when it needs them.
2. **Context file and skills**: `CLAUDE.md` / `AGENTS.md` for always-true project facts, skills for knowledge only some tasks need.
3. **OKF bundle**: curated knowledge as markdown files with YAML frontmatter in git, with provenance, trust and freshness, navigated through `index.md` files.
4. **Search over curated files**: the same files plus a search index once navigation stops scaling.
5. **RAG**: chunked, embedded retrieval over large or uncurated text.
6. **Database behind a tool**: structured records and numbers queried through SQL, an API or an MCP server.

Rungs 4 to 6 are not strictly higher than each other; they answer different shapes of knowledge. Climb only when a concrete need breaks the rung below, and say which need it was. Many people arrive asking for RAG when a context file or an OKF bundle serves them better; many others need a database and call it RAG.

"Rung" and "ladder" are your working words. With the person, name the options plainly ("a short note in CLAUDE.md", "a database Claude queries", "RAG").

## 1. Look before you ask

Facts are your job, never the person's. Before the first question, find out what you can from the environment:

- What knowledge exists, where, and in which formats (markdown, PDFs, spreadsheets, a database, a wiki export)?
- How big it is: file count and a rough token count (characters ÷ 4).
- What already gives the agent context: `CLAUDE.md`, `AGENTS.md`, skills, an existing `knowledge/` or `docs/` tree, MCP servers.

Use a subagent for anything larger than a quick look. If there is no project yet, skip to the next step.

## 2. Ask only the deciding questions

Read [references/options.md](references/options.md#dimensions) first: it lists the dimensions that change the decision. Then sort them:

- **Settled**: the person's message or the environment already answers it. State it as a finding.
- **Deciding**: an open dimension where a different answer would pick a different rung. These are your questions.
- **Detail**: anything that only shapes the build (stack, hosting, schedule, naming, team size). Make a sensible assumption, label it as an assumption, and settle it during the build.

Ask the deciding questions in **one round of at most four**. Number each, give your recommended answer, and word it so "yes" accepts it:

```
❓ **Q1** - **<title>**: <question, with choices where they help>

➡️ <your recommended answer, and the fact it rests on>
```

When nothing is deciding (the message already makes the choice clear), skip the round: decide, and list the one or two answers that would change your mind. Ask a second round only when an answer opens a branch the first round could not see. A long questionnaire costs the person more than a stated assumption they can correct.

## 3. Decide

Lead with the recommendation in one or two plain sentences, then:

- **Why**, tied to the person's own words and the facts you found.
- **Why not** the option they asked about, if you did not pick it, plus at most two others they would plausibly consider. One line each. Options nobody would weigh here need no rejection.
- **What the first version covers**: every kind of question the person mentioned gets a path in the first version, not a later phase. Lists and counts over documents ("which reports covered SOL in 2024") need a queryable catalog beside search; numbers need a database.
- **When to revisit**: the concrete signal that would change the choice (for example "when the folder passes about 2,000 entries or answers start missing documents that exist").
- **Effort and running cost** in plain words.
- **Assumptions** you made, so they can correct them. Name a convention only when it changes this answer: the time zone that decides day and month boundaries when the questions are about periods, the currency when sums are compared, the cost-basis method when profit is computed. Details the person never raised and the answer does not need stay out.

Keep the recommendation under about 500 words, wherever its parts appear in your answer. Detail for the build belongs in the build. State facts only from the person, the environment or a source you name; a tax rule, a price or someone's stack is an assumption until one of those confirms it.

Wait for the person to accept or adjust it.

## 4. Record

When there is a project, write the accepted decision into it so the next session and the next person can see it. Use the repo's existing place for decisions (an `adr/` or `decisions/` folder) if there is one; otherwise `docs/knowledge-decision.md`. Without a project, keep it in your answer. One screen:

```markdown
# Knowledge: <decision in one line>

Date: <YYYY-MM-DD>

## Situation
<the facts that drove the decision>

## Decision
<the option, and which knowledge goes where>

## Not chosen
<each rejected option and the reason>

## Revisit when
<the signals>
```

## 5. Build it

Build only after the person agrees, and change only what the knowledge setup needs: the knowledge files, the pointer in `CLAUDE.md` / `AGENTS.md`, the decision record and small helper scripts. Application code stays as it is unless the person asks. Read the guide for the chosen option first:

- Context file and skills, or nothing extra: [references/options.md](references/options.md#context-file-and-skills)
- OKF bundle, alone or under search: [references/okf.md](references/okf.md), starter files in [assets/okf-bundle/](assets/okf-bundle/), checker in [scripts/check_okf.py](scripts/check_okf.py)
- RAG: [references/rag.md](references/rag.md)
- Database behind a tool: [references/options.md](references/options.md#database-behind-a-tool)

The build is done when the agent answers real questions from the new knowledge. Write three to five questions with the answers the person expects, at least one a calculation when numbers are involved, ask them in a fresh session or a subagent that has only the new setup, and show the results. Save the questions, expected answers and actual answers next to the decision record (for example `docs/knowledge-tests.md`), so the next change can be checked the same way. A miss is a finding: fix the knowledge or its pointer, then ask again.
