---
name: cgp-review
description: "Review code changes the way a careful senior developer would and explain the findings in plain words: is it safe (secrets, data loss, injection), does it do what was asked, and does it follow the project's standards and keep the code clean. Finds what to compare against by itself, runs the reviews in parallel sub-agents, and offers to fix what it found. Use when the user wants a branch, a PR or their latest changes reviewed, asks \"is this OK?\", \"check my code before I push\", \"review since X\", or wants a second opinion on what Claude just built."
---

The people using this skill are often not professional programmers. They cannot judge a diff themselves, so the review has to tell them what matters, how bad it is, and what to do, in plain words. Do the legwork yourself and ask only what the repository cannot tell you.

The review has three **axes**, each run by its own sub-agent so they do not blur into each other:

- **Safety**: can this change leak a secret, lose or corrupt data, let a stranger in, or cost money by accident?
- **Spec**: does the change do what was asked, all of it and nothing else?
- **Standards**: does it follow the project's documented rules and stay clean enough to change later?

## 1. Find what to review

Decide the starting point yourself:

- The person named one (a commit, a branch, `main`, "since yesterday"): use it.
- Uncommitted changes exist (`git status`): review those, plus commits not yet on the default branch.
- Otherwise: everything on this branch since it left the default branch (`git merge-base HEAD origin/main`, or `main`/`master` locally).

Capture the diff command once (`git diff <start>...HEAD`, plus `git diff HEAD` for uncommitted work) and the commit list (`git log <start>..HEAD --oneline`). Check that the start resolves and the diff is not empty before spawning anything; a bad ref should fail here, not in three sub-agents. Say in one line what you are reviewing ("the 4 commits on this branch plus your unsaved changes in 2 files").

## 2. Find the spec

What was the change supposed to do? Look, in this order: issue references in commits (`#123`, `Closes #45`), a path the person gave, a spec or plan under `docs/`, `specs/` or `.scratch/` matching the branch, the request earlier in this conversation. If none exists, write down the intent you read from the commit messages and code, label it as your assumption, and review against that; tell the person so they can correct it. Do not stop the review to ask.

## 3. Find the standards

Anything in the repo that says how code should be written: `CLAUDE.md`, `AGENTS.md`, `CODING_STANDARDS.md`, `CONTRIBUTING.md`, linter and formatter configs. A documented repo rule always wins over the baselines below.

## 4. Spawn the three sub-agents in parallel

Give each one the diff command, the commit list and its brief. Each reports under 400 words, every finding with file and line, a severity, and a one-line fix.

**Safety** brief: paste the [safety baseline](references/baselines.md#safety-baseline). "Report every place the diff could leak a secret, lose or corrupt data, let someone unauthorised in or act for them, or run up costs. Also check that error cases are handled where failure is likely (network, files, user input). Severity: **must fix** when it can do real damage, **should fix** otherwise."

**Spec** brief: paste or point to the spec (or your assumed intent, marked as such). "Report (a) requirements missing or only partly done, (b) behaviour nobody asked for, (c) requirements that look done but work wrongly. Quote the spec line for each."

**Standards** brief: list the standards files and paste the [smell baseline](references/baselines.md#smell-baseline). "Report (a) breaches of a documented rule, citing file and rule, and (b) baseline smells, each a judgement call. Skip anything a linter or formatter already enforces. Severity: documented-rule breaches can be **should fix**; smells are **could improve**."

If tests exist, run them yourself while the sub-agents work and note the result.

## 5. Report

Write in the language the person wrote to you. Use the language's real characters (ä, ö, ü, ß in German), not ASCII stand-ins. Start with a verdict in one or two sentences: can this go in as it is, after small fixes, or not yet.

Then one section per axis (**Safety**, **Spec**, **Standards**), findings ordered by severity, each as:

> **must fix** · `src/orders.ts:42` · The Stripe key is written into the code, so anyone who sees the repository can charge cards. → Move it to `.env` and rotate the key in Stripe.

Keep the axes separate and do not rank across them: code can follow every rule and still do the wrong thing, or do exactly the right thing in a way that breaks the project's rules, and mixing them lets one hide the other. Say "nothing found" for an empty axis.

Explain why each finding matters in the person's terms (what could go wrong for them), not in pattern names. Write the fix the same way: say what the code should do ("if Stripe fails, show an error and leave the order unchanged"), not the construct ("wrap it in try/catch"); the person will ask you to make the fix, so they need to understand the outcome, not the code. HTTP status codes, library calls and terms like idempotency stay out of the report unless they come with plain words. A smell name like "Feature Envy" may follow in brackets for those who want to look it up; the sentence before it must stand alone.

End with the test result, then offer to fix: "Shall I fix the 2 must-fix and 3 should-fix findings now? ➡️ Yes, I'd do it in that order and rerun the tests." Fix only after a yes.

| Word | Plain words |
|---|---|
| diff | the lines that changed |
| commit / branch | a saved step / a line of work in git |
| spec | the description of what the change should do |
| secret | a password, API key or token; anyone who has it can act as you |
| injection | user input that ends up run as a command or database query |
