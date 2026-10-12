# Options and how to choose

## Contents

- [Dimensions](#dimensions): what to ask and what each answer decides
- [The options](#the-options): when each rung fits, and when it does not
- [Context file and skills](#context-file-and-skills): how to build rungs 1 and 2
- [Database behind a tool](#database-behind-a-tool): how to build rung 6
- [Mixes](#mixes): common combinations

The numbers below are rules of thumb from practice, not limits from any spec. Say so when you use one, and let the person's own measurements win.

## Dimensions

| Dimension | Typical question | What the answer decides |
|---|---|---|
| **Consumer** | Who reads this knowledge: a coding agent working in the repo (Claude Code, Codex), an app or chatbot you are building, people, or several of these? | An agent with file access can read and search files itself, which removes most reasons for RAG. An app without file access needs retrieval built in. |
| **Volume** | Roughly how much is there, and how fast does it grow? | Whether it fits as plain files the agent opens on demand, needs an index to navigate, or needs search. |
| **Shape** | Is it prose (guides, notes), facts about things (systems, tables, APIs, processes, people), records and numbers (trades, transactions, metrics), or documents like PDFs and scans? | Facts about things suit OKF. Records and numbers belong in a database. Large prose and documents lean to search or RAG. |
| **Authorship and churn** | Who writes it, people or agents, and how often does it change? | Agent-maintained knowledge needs provenance and freshness fields (OKF). Static reference can stay simple. |
| **Trust** | What happens if the agent uses an outdated or wrong entry? | High stakes call for `verified`, `status` and `stale_after` (OKF) and for answers that cite their source. |
| **Question style** | Are questions lookups of a known thing ("what does the `orders` table hold"), exploration ("anything about fee changes last year"), or calculations ("total fees per month")? | Lookups: files and indexes. Exploration over a lot of text: search or RAG. Calculations: a database and a tool, never RAG. |
| **Portability** | Must other tools, vendors or teams read it too? | Plain files in git (OKF) travel everywhere. A vector store ties you to its tooling. |
| **Privacy** | May the content leave the machine, for example to an embeddings API or a hosted vector database? | Local-only rules out hosted embeddings and vector stores and favours files or a local index. |
| **Maintenance** | Who keeps it current, and how much time is there? | Every rung above 2 needs an owner. A setup nobody maintains is worse than a lower rung that stays true. |

Skip dimensions the environment already answers, and skip those that cannot change the outcome (privacy rarely matters when everything stays in files the person already has).

## The options

### 1. Nothing extra

Fits when the knowledge already lives in the repo as readable files and the agent finds it by opening and searching them. Coding agents are good at this: give them the folder and a good question.

Breaks when the agent keeps missing a fact it should know, or the person keeps repeating the same instruction. Then move to rung 2.

### 2. Context file and skills

Fits for facts that are true in almost every session (conventions, commands, where things live, words the team uses) and for know-how only some tasks need.

- `CLAUDE.md` / `AGENTS.md`: always loaded, so every line costs on every turn. Keep it to what most sessions need, usually well under 200 lines.
- Skills: loaded only when their description matches the task. The right home for procedures and reference that a few kinds of task need.
- A plain `docs/` folder with a pointer in the context file ("Read docs/x.md before touching billing") covers a lot of ground before anything heavier.

Breaks when the knowledge is many separate things (dozens of systems, tables, playbooks, people), when agents write and update it, or when it matters where a fact came from and whether it is still true. Then OKF.

### 3. OKF bundle

Fits when knowledge is a set of **concepts** (systems, data assets, metrics, processes, decisions, people) that people and agents both read and maintain, and when provenance, trust and freshness matter. Plain markdown in git, so it is diffable, reviewable and readable by any tool. `index.md` files let an agent descend one level at a time instead of loading everything. Details: [okf.md](okf.md).

Rule of thumb: navigation through indexes works well up to a few hundred concepts per folder level and roughly a couple of thousand in total.

Honest caveats: OKF is young (v0.2, 2026) and from Google Cloud; tools that consume it natively are few. The risk is low because a bundle is ordinary markdown that every tool can still read.

Breaks when the agent cannot find the right concept by navigating, because there are too many or the questions are fuzzy. Then add search on top (rung 4) and keep the bundle as the source of truth.

### 4. Search over curated files

Fits when an OKF bundle or a docs tree is the right source but has outgrown navigation. Add full-text search first (ripgrep, SQLite FTS5, a static site search); add embeddings only if keyword search misses because people phrase things differently from how documents are written. The files stay the source of truth; the index is rebuilt from them.

### 5. RAG

Fits when there is a lot of unstructured text (thousands of documents or millions of tokens: PDFs, tickets, emails, transcripts, research reports), the content is not curated, questions are exploratory, and especially when the consumer is an app or chatbot without file access. Details: [rag.md](rag.md).

Does not fit for numbers and records (retrieved chunks do not add up), for small corpora an agent can read directly, or when nobody will evaluate retrieval quality. RAG that nobody measures fails quietly.

Search answers "what do the documents say about X". It cannot answer "which documents" or "how many": retrieval returns the top few chunks, not a complete list. When people will ask lists or counts ("all reports on SOL in 2024", "how many reports covered ETF flows"), keep a catalog of the documents' metadata (title, date, language, topics, access level) in a table the assistant can query through a tool, and build it in the first version alongside search.

### 6. Database behind a tool

Fits for structured records and anything you count, sum, filter or join: trades, transactions, prices, metrics, CRM records. The agent asks through a tool (SQL, an API, an MCP server) and gets exact answers. See [Database behind a tool](#database-behind-a-tool).

## Context file and skills

1. Read the existing `CLAUDE.md` / `AGENTS.md` and skills; extend rather than duplicate.
2. Put in the context file only what most sessions need. Write it as facts and pointers: "Trading rules live in `docs/rules/`; read the matching file before changing a strategy."
3. Move task-specific know-how into a skill: a folder with `SKILL.md` (a `name`, a `description` that says when to use it, and the instructions). Put long reference next to it and point to it from `SKILL.md`.
4. If both Claude Code and Codex are used, keep one source: `AGENTS.md` with the content and a `CLAUDE.md` that points to it (or the reverse), never two copies drifting apart.

## Database behind a tool

1. Pick the store the data already lives in. Do not copy records into a new store just for the agent.
2. Give the agent read access through the narrowest tool that works: an existing MCP server for the database or service, a small script with fixed queries, or read-only SQL credentials. Write access only when the task needs it, and then through specific operations rather than free SQL.
3. Document the schema for the agent: table and column meanings, units, currencies, the time zone that decides day and month boundaries, and which numbers are authoritative. Where the person has not said, state your choice as an assumption. This documentation itself is a good OKF bundle or a section of the context file.
4. Test with questions whose answers the person already knows, including one calculation.

## Mixes

Common combinations, each part on its own rung:

- **Context file + OKF**: conventions in `AGENTS.md`, curated knowledge about systems and data in a bundle, with one line in `AGENTS.md` pointing to the bundle's root `index.md`.
- **OKF + database**: the bundle describes tables, metrics and how to compute them; the numbers stay in the database and are queried through a tool.
- **OKF + search**: the bundle is the source of truth, an index makes it findable at scale.
- **Files + RAG**: curated docs as files for the agent, RAG only for the large archive of PDFs or tickets.
