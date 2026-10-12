---
name: cgp-test-first
description: Build features and fix bugs test-first, so the code is proven to work and stays working. Sets up a test runner if the project has none, writes one failing test per behaviour, makes it pass, and shows the person how to run the tests. Use when the user wants tests, test-driven development (TDD), "red-green", integration tests, wants to be sure a feature or fix really works, or a bug keeps coming back, even if they never say "test".
---

# Test-first development

The people using this skill are often not professional programmers. They want code that works and keeps working when they or Claude change it later. They cannot judge test architecture, so you make those calls, and you show proof instead of asking them to trust you.

The loop is **red → green**: write a test for one behaviour, watch it fail (red), write just enough code to make it pass (green), repeat. A test you never saw fail proves nothing, because it may pass no matter what the code does.

## 1. Look before you ask

Find out yourself what the project can tell you:

- Language, package manager and existing test setup (`package.json` scripts, `vitest`/`jest`/`pytest` config, a `tests/` folder). Run the existing tests once so you know the starting state.
- If there is no test runner, add the standard one for the stack (Vitest for JavaScript/TypeScript, pytest for Python, the built-in runner for Go or Rust) and a `test` script, so `npm test` or `uv run pytest` works.
- Read `GLOSSARY.md` and any decision records (ADRs) in the area, so test names use the project's own words.

## 2. Agree on the behaviours, in plain words

Before writing tests, list the behaviours you will test as sentences the person can check without reading code, each with your recommendation:

```
I'll prove these work, in this order:
1. A price alert fires when the price crosses the target from below.
2. An alert fires only once, not on every price update after that.
3. A missing or wrong API key gives a clear error instead of a crash.
Not tested: the exact text of the Telegram message (changes often, low risk).
➡️ OK like this?
```

Pick the behaviours yourself: the main path, the mistakes that would cost the person money or data, and the bug they reported. Ask only when a behaviour depends on something only they know (what should happen with an empty cart?), at most three questions, each with your recommended answer so "yes" is enough. If the person said to just do it, state the list and continue.

For a bug: the first test reproduces the bug and must fail for the reason the person described. That failing test is your proof you found it.

## 3. Run the loop, one behaviour at a time

- **Red.** Write one test for the next behaviour. Run it and see it fail for the expected reason (an assertion, not a typo or import error).
- **Green.** Write only enough code to pass it. No extra features for tests you have not written.
- **Run everything.** All tests pass before the next behaviour.

One test, then its code, then the next test. Writing all tests up front tests what you imagine the code will do; one at a time lets each test learn from the last.

Keep notes of each red and green run (the command and the one-line result) for the hand-over.

## What makes a test worth keeping

- **Test what the code does, through the way it is used**: call the function, hit the endpoint, run the command, and check the result. Not private helpers, not "function X was called". A good test survives a rewrite of the inside. See [tests.md](tests.md).
- **Expected values come from outside the code**: a worked example, a known number, the spec. `expect(add(a, b)).toBe(a + b)` repeats the code and can never fail.
- **Fake only what you do not own or cannot run in a test**: payment providers, email, the clock, randomness, paid APIs. Use the real database when it is cheap (SQLite, a test Postgres in Docker). See [mocking.md](mocking.md).
- **Names read like a sentence**: `fires once when price crosses target`, so a failing test tells the person what broke.
- **No real secrets or live services in tests.** Tests run often and on other machines; a real API key in a test file leaks, and a live call can cost money.

When the shape of the code makes testing hard (everything in one big function, the database opened inside the logic), the `cgp-architecture` skill describes how to restructure it so it can be tested; restructure in small steps with the tests passing after each.

Cleaning up code that works (refactoring) comes after the loop, with the tests as the safety net; the `cgp-review` skill covers it.

## 4. Hand over

Write in the language the person wrote to you. Use the language's real characters (ä, ö, ü, ß in German), not ASCII stand-ins. Tell them, short and plain:

- **What is now proven**, as the behaviour list, each marked passing.
- **The proof**: for each behaviour, that the test failed first and passes now (one line each, from your notes), and the full test run at the end.
- **How to run the tests themselves**, as its own step with the command in a code block, and what a pass and a failure look like.
- What is deliberately not tested, and why.

Explain a testing word the first time you use it, or avoid it:

| Word | Plain words |
|---|---|
| test | a small program that checks one thing the app should do |
| test runner (Vitest, pytest) | the tool that runs all tests and says which pass |
| red / green | the test fails / the test passes |
| mock, fake | a stand-in for a real service, so tests do not send real emails or payments |
| refactoring | tidying code without changing what it does |
