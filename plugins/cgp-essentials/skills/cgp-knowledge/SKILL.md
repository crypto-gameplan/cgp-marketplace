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

"Rung" and "ladder" are your working words. With the person, name the options plainly ("a short note in CLAUDE.md", "a database Claude queries", "RAG"). Write in the language the person wrote to you, with its real characters (ä, ö, ü, ß in German), and give every technical word a few plain words the first time it appears, or avoid it:

| Word | Plain words |
|---|---|
| CLAUDE.md / AGENTS.md | a short file Claude reads at the start of every session |
| skill | a guide Claude loads only for the tasks that need it |
| RAG | the text is cut into pieces and the pieces that sound most similar to the question are looked up |
| embeddings, vector database | the technique and the storage behind RAG: each piece of text becomes a list of numbers, so texts with similar meaning can be found even when the words differ |
| full-text search (for example SQLite FTS5) | a search index like a book's index: it finds every place a word appears, fast |
| token | a piece of a word; about 4 characters, the unit AI models count text in |
| index file | one list with a line per document, so Claude knows what exists and where |
| markdown | plain text files with simple formatting, which Claude reads best |

A term the person used themselves ("brauch ich RAG?") needs the explanation too: they often ask because they heard the word but do not know what it means. Talk to the person as a capable adult who is new to this field, never about what they do not know. Do not ask them to run commands to measure their files; ask in everyday terms ("roughly how many files, and are the PDFs text you can select or scanned pages?") or find out yourself when there is a project.
| OKF bundle | a folder of curated notes, each with its source, date and how much to trust it |
| MCP server / tool | a connector that lets Claude query a database or service |

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

Ask the deciding questions in **one round of at most four**, one thing per question. Number each, give your recommended answer, and word it so "yes" accepts it:

```
❓ **Q1** - **<title>**: <question, with choices where they help>

➡️ <your recommended answer, and the fact it rests on>
```

When nothing is deciding (the message already makes the choice clear), skip the round: decide, and list the one or two answers that would change your mind. Ask a second round only when an answer opens a branch the first round could not see. A long questionnaire costs the person more than a stated assumption they can correct.

## 3. Decide

Answer in this shape, each part a few lines, together under 450 words:

- **Recommendation** in one or two plain sentences: what to do and what not to build.
- **Why**, tied to the person's own words and the facts you found.
- **Why not** the option they asked about, in one or two lines. Others only if they would plausibly weigh them, one line each.
- **First step**: what happens first, and that every kind of question they mentioned is covered from the start. Lists and counts over documents ("which reports covered SOL in 2024") need a list of all documents beside search; numbers need a database.
- **When to change course**: the concrete signal, for example "when Claude misses things you know are in the notes".
- **Effort and cost** in one line.
- **Assumptions**: at most three, only those that would change the answer.

Say each point once. Name techniques by what they do ("a word search over your files", "search by meaning"), and if a technical name must appear, explain it right there, every section included; never drop in tool names like FTS5, ripgrep or pgvector for the person to decode. Detail for the build belongs in the build. State facts only from the person, the environment or a source you name; a tax rule, a price or someone's stack is an assumption until one of those confirms it.

Before you send it, reread it as the person would: someone who does not program. Find every word they would not use themselves, including synonyms and everyday tech words (retrieval, pipeline, hook, script, repo, index), and replace it with what it does or explain it in a few words where it first appears.

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
