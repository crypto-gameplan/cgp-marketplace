# Review baselines

Paste the relevant baseline into the sub-agent's prompt; it has no other access to it. A documented repo rule always overrides a baseline item.

## Safety baseline

Each item: what to look for → why it matters → the usual fix.

- **Secrets in code or git**: API keys, passwords, tokens, private keys in source, config, tests, logs or a tracked `.env`. → Anyone with the repo can use them. → Move to `.env` (ignored by git) and read from the environment; a secret that was ever committed must be rotated, deleting it is not enough.
- **Injection**: user input concatenated into SQL, shell commands, file paths or HTML. → A stranger can read or delete data or run commands. → Parameterised queries, argument lists instead of shell strings, path checks, escaping by the template engine.
- **Missing access checks**: an endpoint or action that changes or reveals data without checking who is asking, or trusts an ID from the request. → Anyone can read or change other people's data. → Check the logged-in user owns the record.
- **Data loss**: deletes or overwrites without confirmation or backup, migrations that drop columns with data, writes that are not atomic, a database without a persistent volume. → Data is gone. → Soft delete, backups, transactions, reversible migrations.
- **Money and quotas**: loops or retries calling paid APIs without limits, trades or payments without a confirmation step or idempotency, amounts in floating point. → Unexpected bills or double charges. → Limits, idempotency keys, integer cents or decimals.
- **Unhandled failure**: network calls, file reads, JSON parsing or user input without error handling where failure is likely; errors swallowed silently. → The app crashes or silently does the wrong thing. → Handle the error, tell the user, log it.
- **Leaking through errors and logs**: stack traces, secrets or personal data in responses or logs. → Helps attackers, breaks privacy rules. → Generic error to the user, details only in server logs, no secrets logged.
- **Risky dependencies**: new packages that are unmaintained, typo-named, or pulled from unknown sources; versions not pinned in a lock file. → Supply-chain attacks, builds that break by themselves. → Well-known packages, lock file committed.

## Smell baseline

Fowler's code smells (_Refactoring_, ch. 3). Each is a judgement call ("possibly …"), never a hard violation. Each reads *what it is* → *how to fix*:

- **Mysterious Name**: a function, variable or type whose name doesn't reveal what it does or holds. → Rename it; if no honest name comes, the design is murky.
- **Duplicated Code**: the same logic shape in more than one place in the change. → Extract the shared shape, call it from both.
- **Long Function**: a function doing several things in a row that each deserve a name. → Split into named steps.
- **Feature Envy**: a function that reaches into another object's data more than its own. → Move it to the data it uses.
- **Data Clumps**: the same few fields or parameters keep travelling together. → Bundle them into one type.
- **Primitive Obsession**: a plain string or number standing in for a concept that deserves its own type (money, email, ID). → Give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if` chain on the same type in several places. → One map or polymorphism both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files. → Gather what changes together into one module.
- **Divergent Change**: one file edited for several unrelated reasons. → Split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters or hooks for needs the spec doesn't have. → Delete it until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → Hide the walk behind one method.
- **Middle Man**: a class or function that mostly just passes calls on. → Cut it, call the real target.
- **Refused Bequest**: a subclass that ignores or overrides most of what it inherits. → Use composition instead.
