# RAG: retrieval-augmented generation

RAG splits documents into chunks, turns each chunk into an embedding (a vector of numbers that captures meaning), stores them in an index, and at question time retrieves the chunks closest to the question and hands them to the model. Use it for large, unstructured, uncurated text with exploratory questions; [options.md](options.md#5-rag) says when not to.

Tools and models in this space change monthly. Before naming a product, check its current docs and pricing, and prefer what the person already runs.

## Contents

- [Before building](#before-building)
- [Building blocks](#building-blocks)
- [A first version](#a-first-version)
- [Measuring it](#measuring-it)
- [Common failures](#common-failures)

## Before building

Settle these with the person; they decide most of the design:

- **Consumer**: an agent with file access (Claude Code, Codex) or an app. For an agent, a search tool over files (an MCP server or a script) is often enough; a full RAG pipeline earns its keep mostly in apps and for very large archives.
- **Corpus**: formats (PDF, HTML, email, transcripts), size, languages, how often it changes, who may see which documents.
- **Privacy**: may text go to a hosted embeddings API, or must everything run locally?
- **Test questions**: ten to twenty real questions with known answers and the documents that contain them. Without these, nobody can tell whether it works.

## Building blocks

| Block | Choices | Guidance |
|---|---|---|
| **Extraction** | Plain text and markdown as is; PDFs through a PDF-to-text or layout-aware parser; scans need OCR | Bad extraction ruins everything after it. Look at the extracted text of a few hard documents first. |
| **Chunking** | By heading or section first, then by size (a few hundred tokens) with a small overlap | Keep the document title and section path in each chunk; a chunk that does not say what it belongs to retrieves badly. |
| **Metadata** | Source path or URL, title, date, author, access group | Needed for citations, filters ("only 2026") and permissions. |
| **Embeddings** | A hosted embeddings API, or a local model (for example through Ollama) when text must stay local | Use one model for indexing and querying; re-embed everything when you switch. |
| **Index** | Small and local: SQLite with a vector extension, LanceDB, Chroma. Already on Postgres: pgvector. Large or shared: a managed vector database | Start with the smallest that fits; moving later is a re-index, not a rewrite. |
| **Retrieval** | Hybrid search (keyword plus vector) with a reranker | Pure vector search misses exact names, tickers, codes and numbers; keyword search catches them. |
| **Generation** | The model answers from the retrieved chunks and cites them | Tell it to say when the chunks do not contain the answer instead of guessing. |

## A first version

1. Collect the test questions and expected sources.
2. Extract and inspect ten representative documents.
3. Chunk by structure, attach metadata, embed, index. Keep the pipeline a script that rebuilds the index from the source folder, so the documents stay the source of truth.
4. Expose retrieval as one tool or function: `search(query, filters) -> chunks with source`. If people will ask for lists or counts of documents, add a second tool over the metadata catalog (`list_documents(filters) -> titles, dates, links`); search alone cannot answer those. For Claude Code or Codex this can be a small MCP server or a CLI the agent calls.
5. Run the test questions, measure (next section), then tune chunking and retrieval before anything else.
6. Document in the project how to rebuild the index and when it must be rebuilt.

## Measuring it

- **Retrieval hit rate**: for each test question, is a correct source among the top results (top 5 is a common bar)? Measure this before looking at answers; most RAG problems are retrieval problems.
- **Answer correctness and citations**: does the answer match the expected one and cite the right source?
- Re-run the set after every change to chunking, embeddings or retrieval, and keep the numbers in the repo.

## Common failures

- Chunks too small to carry meaning, or too large to rank well.
- Tables, figures and numbers flattened into unreadable text.
- Exact terms (tickers, IDs, error codes) missed by vector-only search.
- Stale index: documents changed, index not rebuilt.
- Permissions ignored: a chunk from a restricted document reaches someone who may not see it.
- Numbers answered from retrieved text instead of computed from a database.
