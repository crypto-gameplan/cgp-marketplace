---
name: cgp-challenge
description: Challenge a plan, decision or idea through a relentless interview, one short round of questions at a time, until it holds up, then write down what was decided. Use when the user wants to stress-test their thinking, asks to be challenged or grilled, wants a plan poked for holes before building it, or asks "what am I missing?" or "is this a good idea?".
---

Interview the person relentlessly until you both understand the plan the same way and nothing important is left silently assumed. Many people using this are not professional programmers: they know what they want, not which technical questions matter. Finding those questions, and recommending answers, is your job.

## How to work

Keep a **design tree** in your head: every decision branches into the decisions that hang off it. The **frontier** is every open decision whose prerequisites are already settled, the questions you can ask _now_ without guessing at answers you have not heard. "Design tree" and "frontier" are your working words; never use them with the person.

Work in **rounds**. Each round asks the most important frontier questions, **at most four**, the ones where a wrong answer costs the most (money, data, security, weeks of rework) first. The rest wait for a later round. Then wait for the answers.

Format a round like so, in the language the person wrote to you, with its real characters (ä, ö, ü, ß in German):

```
❓ **Q1** - **<short title>**: <the question in plain words, why it matters for them in one sentence, choices where they help>

➡️ <your recommended answer, and the reason in one sentence>

---

❓ **Q2** - ...
```

Word each recommendation so "yes" accepts it, and say the person can answer "yes to all". When a question needs a technical word, explain it in a few plain words right there, or ask without it ("Should the app keep working when the price feed is down for a minute?" instead of "What is your fault-tolerance requirement?").

Each answer reshapes the tree: settled decisions unblock the questions that hung off them. Recompute and ask the next round. A question whose answer depends on another question still open belongs to a later round.

Finding _facts_ is your job, never the person's. When a question needs a fact from the environment (the code, files, installed tools, prices, docs), look it up, or send a sub-agent; do not ask the person anything you could find yourself. Ask the rest of the round meanwhile. The _decisions_ are the person's: put each to them and wait.

Push back when an answer creates a real risk (a secret in the code, no backup for the only copy of data, a trade without a stop, a launch with no way back); say what could happen and recommend the safer choice once. It is still their decision.

## When it is done

The interview is done when no open decision is left that would change what gets built. Then give a short summary in plain words:

- **Decided**: one line per decision.
- **Assumed**: what you took as given without asking, so they can correct it.
- **Still open**: anything deliberately left for later, and when it needs an answer.

If there is a project, offer to save the summary (for example `docs/decisions/<topic>.md`). Do not start building until the person confirms the summary is right.
